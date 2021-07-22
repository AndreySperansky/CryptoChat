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
LOGGER = logging.getLogger('server')

@log
def process_client_message(message, messages_list, client, clients, names):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    '''
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        # Если такой пользователь ещё не зарегистрирован, регистрируем,
        # иначе отправляем ответ и завершаем соединение.
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
            and TIME in message and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        # если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]

        return
        # Иначе отдаём Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')




@log
def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default='7777', )
    parser.add_argument('-a', '--address', default='127.0.0.1', )
    args = parser.parse_args(sys.argv[1:])
    listen_port = args.port
    listen_address = args.address

    # проверка получения корретного номера порта для работы сервера.
    try:
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except ValueError:
        LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port



def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    server.py -p 8079 -a 192.168.1.51
    '''
    listen_address, listen_port = createParser()

    LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')


    # Готовим сокет

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((listen_address, listen_port))
        s.listen(MAX_CONNECTIONS)
        s.settimeout(2)

        # список клиентов , очередь сообщений
        clients = []
        messages = []
        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()


        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = s.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соедение с ПК {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения, кладём в словарь,
            #  если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        process_client_message(get_message(client_with_message),
                                               messages, client_with_message, clients, names)
                    except:
                        LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                    f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения для отправки, обрабаотываем каждое.
            for i in messages:
                try:
                    process_message(i, names, send_data_lst)
                except Exception:
                    LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()



if __name__ == '__main__':
    main()


