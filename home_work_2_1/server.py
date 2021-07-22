"""Программа-сервер"""

from socket import *
import sys
import argparse
import logging
import select
import time
import logs.configs.config_server_log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, \
    ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE,  ERROR, MESSAGE, MESSAGE_TEXT,  STATUS, \
    RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from common.utils import get_message, send_message
from decors import log

# Инициализация логирования сервера.


class Server:

    def __init__(self, DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER,
                 ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE,  ERROR, MESSAGE, MESSAGE_TEXT,  STATUS,
                 RESPONSE_200, RESPONSE_400, DESTINATION, EXIT):

        self.DEFAULT_PORT=DEFAULT_PORT
        self.MAX_CONNECTIONS=MAX_CONNECTIONS
        self.ACTION=ACTION
        self.TIME=TIME
        self.USER=USER
        self.ACCOUNT_NAME=ACCOUNT_NAME
        self.SENDER=SENDER
        self.PRESENCE=PRESENCE
        self.RESPONSE=RESPONSE
        self.ERROR=ERROR
        self.MESSAGE=MESSAGE
        self.MESSAGE_TEXT=MESSAGE_TEXT
        self.STATUS=STATUS
        self.RESPONSE_200=RESPONSE_200
        self.RESPONSE_400=RESPONSE_400
        self.DESTINATION=DESTINATION
        self.EXIT=EXIT
        self.log=log()


        self.LOGGER = logging.getLogger('server')
        self.get_message = get_message()
        self.send_message = send_message()



    @log
    def process_client_message(self, message, messages_list, client, clients, names):
        self.message = message
        self.client = client
        self.clients = clients
        self.names = names
        self.messages_list = messages_list

        '''
        Обработчик сообщений от клиентов, принимает словарь -
        сообщение от клинта, проверяет корректность,
        возвращает словарь-ответ для клиента
        '''
        self.LOGGER.debug(f'Разбор сообщения от клиента : {self.message}')
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if self.ACTION in self.message and self.message[ACTION] == self.PRESENCE \
                and self.TIME in self.message and self.USER in self.message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем,
            # иначе отправляем ответ и завершаем соединение.
            if self.message[self.USER][self.ACCOUNT_NAME] not in self.names.keys():
                self.names[message[self.USER][self.ACCOUNT_NAME]] = self.client
                send_message(self.client, self.RESPONSE_200)
            else:
                self.response = self.RESPONSE_400
                self.response[self.ERROR] = 'Имя пользователя уже занято.'
                send_message(self.client, self.response)
                self.clients.remove(self.client)
                self.client.close()
            return
            # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in self.message and self.message[self.ACTION] == self.MESSAGE \
                and self.DESTINATION in self.message \
                and TIME in self.message and SENDER in self.message and self.MESSAGE_TEXT in self.message:
            self.messages_list.append(self.message)
            # если клиент выходит
        elif ACTION in self.message and self.message[self.ACTION] == self.EXIT and self.ACCOUNT_NAME in self.message:
            self.clients.remove(self.names[self.message[self.ACCOUNT_NAME]])
            self.names[self.message[self.ACCOUNT_NAME]].close()
            del self.names[self.message[self.ACCOUNT_NAME]]

            return
            # Иначе отдаём Bad request
        else:
            self.response = self.RESPONSE_400
            self.response[self.ERROR] = 'Запрос некорректен.'
            send_message(self.client, self.response)
            return


    @log
    def process_message(self, message, names, listen_socks):
        self.message = message
        self.names = names
        self.listen_socks =  listen_socks
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        """
        if self.message[self.DESTINATION] in self.names and self.names[self.message[self.DESTINATION]] \
                in self.listen_socks:
            send_message(self.names[self.message[DESTINATION]], self.message)
            self.LOGGER.info(f'Отправлено сообщение пользователю {self.message[self.DESTINATION]} '
                        f'от пользователя {self.message[SENDER]}.')
        elif self.message[DESTINATION] in self.names and \
                self.names[self.message[self.DESTINATION]] not in self.listen_socks:
            raise ConnectionError
        else:
            self.LOGGER.error(
                f'Пользователь {self.message[self.DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')




    # @log
    def createParser(self ):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-p', '--port', type=int, default='7777', )
        self.parser.add_argument('-a', '--address', default='127.0.0.1', )
        self.args = self.parser.parse_args(sys.argv[1:])
        self.listen_port = self.args.port
        self.listen_address = self.args.address

        # проверка получения корретного номера порта для работы сервера.
        try:
            if self.listen_port < 1024 or self.listen_port > 65535:
                raise ValueError
        except ValueError:
            self.LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                                   f'{self.listen_port}. Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

        return self.listen_address, self.listen_port



    def main(self):
        '''
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
        server.py -p 8079 -a 192.168.1.51
        '''
        self.listen_address, self.listen_port = self.createParser()

        self.LOGGER.info(f'Запущен сервер, порт для подключений: {self.listen_port}, '
                           f'адрес с которого принимаются подключения: {self.listen_address}. '
                           f'Если адрес не указан, принимаются соединения с любых адресов.')


        # Готовим сокет

        with socket(AF_INET, SOCK_STREAM) as self.s:
            self.s.bind((self.listen_address, self.listen_port))
            self.s.listen(self.MAX_CONNECTIONS)
            self.s.settimeout(2)

            # список клиентов , очередь сообщений
            self.clients = []
            self.messages = []
            # Словарь, содержащий имена пользователей и соответствующие им сокеты.
            self.names = dict()


            while True:
                # Ждём подключения, если таймаут вышел, ловим исключение.
                try:
                    self.client, self.client_address = self.s.accept()
                except OSError:
                    pass
                else:
                    self.LOGGER.info(f'Установлено соедение с ПК {self.client_address}')
                    self.clients.append(self.client)

                self.recv_data_lst = []
                self.send_data_lst = []
                self.err_lst = []

                # Проверяем на наличие ждущих клиентов
                try:
                    if self.clients:
                        self.recv_data_lst, self.send_data_lst, \
                        self.err_lst = select.select(self.clients, self.clients, [], 0)
                except OSError:
                    pass

                # принимаем сообщения и если там есть сообщения, кладём в словарь,
                #  если ошибка, исключаем клиента.
                if self.recv_data_lst:
                    for self.client_with_message in self.recv_data_lst:
                        try:
                            self.process_client_message(self.get_message(self.client_with_message),
                                        self.messages, self.client_with_message, self.clients, self.names)
                        except:
                            self.LOGGER.info(f'Клиент {self.client_with_message.getpeername()} '
                                        f'отключился от сервера.')
                            self.clients.remove(self.client_with_message)

                # Если есть сообщения для отправки, обрабаотываем каждое.
                for i in self.messages:
                    try:
                        self.process_message(i, self.names, self.send_data_lst)
                    except Exception:
                        self.LOGGER.info(f'Связь с клиентом с именем {i[self.DESTINATION]} была потеряна')
                        self.clients.remove(self.names[i[DESTINATION]])
                        del self.names[i[self.DESTINATION]]
                self.messages.clear()



# if __name__ == '__main__':
#     main()


