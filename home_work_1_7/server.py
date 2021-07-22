"""Программа-сервер"""

from socket import *
import sys
import json
import argparse
import logging
import select
import time
import logs.configs.config_server_log
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, \
    ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE,  ERROR, MESSAGE, MESSAGE_TEXT,  STATUS
from common.utils import get_message, send_message
from decors import log

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')

@log
def process_client_message(message, messages_list, client):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента
    '''
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest' \
            and message[USER][STATUS] == 'User is online':
        send_message(client, {RESPONSE: 200})
        return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
        # Иначе отдаём Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


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

            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        process_client_message(get_message(client_with_message),
                                               messages, client_with_message)
                    except:
                        LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                    f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            if messages and send_data_lst:
                message = {
                    ACTION: MESSAGE,
                    SENDER: messages[0][0],
                    TIME: time.time(),
                    MESSAGE_TEXT: messages[0][1]
                }
                del messages[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                        clients.remove(waiting_client)



if __name__ == '__main__':
    main()


