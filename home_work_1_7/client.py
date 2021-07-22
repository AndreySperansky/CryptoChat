"""Программа-клиент"""

import sys
import json
import time
from socket import *
import argparse
import logging
import logs.configs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, STATUS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, ServerError
from decors import log


# Инициализация клиентского логера
LOGGER = logging.getLogger('client')


@log
def create_presence(account_name='Guest', user_status='User is online'):
    ''' Функция генерирует запрос о присутствии клиента '''
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: user_status
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        LOGGER.info(f'Получено сообщение от пользователя '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        sock.close()
        LOGGER.info('Завершение работы по команде пользователя.')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict



@log
def create_presence(account_name='Guest', user_status='User is online'):
    '''Функция генерирует запрос о присутствии клиента'''
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: user_status
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out




@log
def process_ans(message):
    '''
   Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    '''
    LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)



@log
def arg_parser():
    """Создаём парсер аргументов коммандной строки
    и читаем параметры, возвращаем 3 параметра
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # проверим подходящий номер порта

    # if not 1023 < server_port < 65536:
    #     LOGGER.critical(
    #         f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
    #         f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
    #     sys.exit(1)

    try:
        if not 1023 < server_port < 65536:
            raise ValueError
    except ValueError:
        LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{server_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode




def main():
    '''Загружаем параметы коммандной строки'''
    # client.py 192.168.1.51 8079
    server_address, server_port, client_mode = arg_parser()

    LOGGER.info(f'Запущен клиент с парамертами: '
                f'адрес сервера: {server_address}, '
                f'порт: {server_port}'
                f'режим работы: {client_mode}')

    # Инициализация сокета и обмен

    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(s, message_to_server)
        try:
            answer = process_ans(get_message(s))
            LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except (ValueError, json.JSONDecodeError):
            LOGGER.error('Не удалось декодировать полученную Json строку.')
            print('Не удалось декодировать сообщение сервера.')
            sys.exit(1)
        except ServerError as error:
            LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                        f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                            f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно,
            # начинаем обмен с ним, согласно требуемому режиму.
            # основной цикл прогрммы:
            if client_mode == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                # режим работы - отправка сообщений
                if client_mode == 'send':
                    try:
                        send_message(s, create_message(s))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

                # Режим работы приём:
                if client_mode == 'listen':
                    try:
                        message_from_server(get_message(s))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        LOGGER.error(f'Соединение с сервером {server_address} было потеряно.')
                        sys.exit(1)

if __name__ == '__main__':
    main()
