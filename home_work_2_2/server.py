"""Программа-сервер"""

import socket
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
from descrptrs import Port
from metaclasses import ServerMaker

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')


@log
def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default='7777', )
    parser.add_argument('-a', '--address', default='127.0.0.1', )
    args = parser.parse_args(sys.argv[1:])
    listen_port = args.port
    listen_address = args.address
    return listen_address, listen_port



################################################################################################
# Основной класс сервера
################################################################################################


LOGGER = logging.getLogger('server')


# Парсер аргументов коммандной строки.
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port



################################################################################################
# Основной класс сервера
################################################################################################


class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

    def init_socket(self):
        LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.port} , '
            f'адрес с которого принимаются подключения: {self.addr}.' 
            'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.addr, self.port))
            s.listen(MAX_CONNECTIONS)
            s.settimeout(2)


            # Начинаем слушать сокет.
            self.sock = s
            self.sock.listen()

    # def main_loop(self):
    #     # Инициализация Сокета
    #     self.init_socket()

            # Основной цикл программы сервера
            while True:
                # Ждём подключения, если таймаут вышел, ловим исключение.
                try:
                    client, client_address = self.sock.accept()
                except OSError:
                    pass
                else:
                    LOGGER.info(f'Установлено соедение с ПК {client_address}')
                    self.clients.append(client)

                recv_data_lst = []
                send_data_lst = []
                err_lst = []
                # Проверяем на наличие ждущих клиентов
                try:
                    if self.clients:
                        recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
                except OSError:
                    pass

                # принимаем сообщения и если ошибка, исключаем клиента.
                if recv_data_lst:
                    for client_with_message in recv_data_lst:
                        try:
                            self.process_client_message(get_message(client_with_message), client_with_message)
                        except:
                            LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                            self.clients.remove(client_with_message)

                # Если есть сообщения, обрабатываем каждое.
                for message in self.messages:
                    try:
                        self.process_message(message, send_data_lst)
                    except:
                        LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                        self.clients.remove(self.names[message[DESTINATION]])
                        del self.names[message[DESTINATION]]
                self.messages.clear()


    #########################################################################################
        # Функция адресной отправки сообщения определённому клиенту.
        # Принимает словарь сообщение, список зарегистрированых
        # пользователей и слушающие сокеты. Ничего не возвращает.
    #########################################################################################

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна.')

    #########################################################################################
    # Обработчик сообщений от клиентов, принимает словарь -
    # сообщение от клинта, проверяет корректность,
    # возвращает словарь-ответ для клиента
    #########################################################################################


    def process_client_message(self, message, client):
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def main():
    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    listen_address, listen_port = arg_parser()

    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port)
    # server.main_loop()
    server.init_socket()


if __name__ == '__main__':
    main()
