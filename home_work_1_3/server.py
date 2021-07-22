"""Программа-сервер"""

from socket import *
import sys
import json
import argparse
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message


def process_client_message(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=7777, )
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
    try:
        listen_port = args.port
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except ValueError:
        print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        listen_address = args.address
    except IndexError:
        print(
            'После параметра \'a\'- необходимо указать IP - адрес, который будет слушать сервер.')
        sys.exit(1)





    # Готовим сокет

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((listen_address, listen_port))
        s.listen(MAX_CONNECTIONS)

        while True:
            client, client_address = s.accept()
            try:
                message_from_cient = get_message(client)
                print(message_from_cient)
                # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
                response = process_client_message(message_from_cient)
                send_message(client, response)
            except (ValueError, json.JSONDecodeError):
                print('Принято некорретное сообщение от клиента.')



if __name__ == '__main__':
    main()


