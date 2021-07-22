"""Программа-клиент"""

import sys
import json
import time
from socket import *
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message


def create_presence(account_name='Guest', user_status='User is online'):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    '''
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: user_status
        }
    }
    return out


def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.51 8079
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Инициализация сокета и обмен

    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(s, message_to_server)
        try:
            answer = process_ans(get_message(s))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
