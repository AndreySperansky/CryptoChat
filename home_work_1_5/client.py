"""Программа-клиент"""

import sys
import json
import time
from socket import *
import logging
import logs.configs.config_client_log
from errors import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, STATUS, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message


# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


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
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
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
        if not 1023 < server_port < 65536:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        CLIENT_LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}.'
            f' Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_address}, порт: {server_port}')

    # Инициализация сокета и обмен

    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(s, message_to_server)
        try:
            answer = process_ans(get_message(s))
            CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
            print(answer)
        except (ValueError, json.JSONDecodeError):
            CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
            print('Не удалось декодировать сообщение сервера.')
        except ReqFieldMissingError as missing_error:
            CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                                f'{missing_error.missing_field}')
        except ConnectionRefusedError:
            CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                                   f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    main()
