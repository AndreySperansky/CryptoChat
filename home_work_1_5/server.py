"""Программа-сервер"""

from socket import *
import sys
import json
import argparse
import logging
import logs.configs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, STATUS
from common.utils import get_message, send_message

#Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')

def process_client_message(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest' \
            and message[USER][STATUS] == 'User is online':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default='7777', )
    parser.add_argument('-a', '--address', default='127.0.0.1', )
    return parser



def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8079 -a 192.168.1.51
    :return:
    '''

    parser = createParser()
    args = parser.parse_args(sys.argv[1:])
    listen_port = args.port
    listen_address = args.address

    try:

        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except ValueError:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    # try:
    #
    # except IndexError:
    #     SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего IP адреса '
    #                            f'{listen_address}.')
    #     sys.exit(1)


    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')





    # Готовим сокет

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((listen_address, listen_port))
        s.listen(MAX_CONNECTIONS)

        while True:
            client, client_address = s.accept()
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
            try:
                message_from_cient = get_message(client)
                SERVER_LOGGER.debug(f'Получено сообщение {message_from_cient}')
                print(message_from_cient)
                # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
                response = process_client_message(message_from_cient)
                SERVER_LOGGER.info(f'Cформирован ответ клиенту {response}')
                send_message(client, response)
                SERVER_LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
            except (ValueError, json.JSONDecodeError):
                SERVER_LOGGER.error(f'Не удалось декодировать JSON строку, полученную от '
                                    f'клиента {client_address}. Соединение закрывается.')
                print('Принято некорретное сообщение от клиента.')



if __name__ == '__main__':
    main()


