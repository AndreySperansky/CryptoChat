"""Программа-клиент"""

import sys
import json
import time
from socket import *
import argparse
import logging
import threading
import logs.configs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, STATUS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from decors import log


# Инициализация клиентского логера
LOGGER = logging.getLogger('client')


@log
def create_presence(account_name):
    ''' Функция создает словарь с сообщением о выходе '''

    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
    }


@log
def message_from_server(sock, my_username):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                            f'\n{message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }



@log
def create_message(sock, account_name='Guest'):
    """
    Функция запрашивает кому отправить сообщение и само сообщение,
    и отправляет полученные данные на сервер
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(1)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')





@log
def create_presence(account_name):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')




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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта

    try:
        if not 1023 < server_port < 65536:
            raise ValueError
    except ValueError:
        LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{server_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return server_address, server_port, client_name




def main():
    """Сообщаем о запуске"""
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки

    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(f'Запущен клиент с парамертами: '
                f'адрес сервера: {server_address}, '
                f'порт: {server_port}'
                f'имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении

    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((server_address, server_port))

        message_to_server = create_presence(client_name)
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
            # запускаем клиенский процесс приёма сообщний
            receiver = threading.Thread(target=message_from_server, args=(s, client_name))
            receiver.daemon = True
            receiver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            user_interface = threading.Thread(target=user_interactive, args=(s, client_name))
            user_interface.daemon = True
            user_interface.start()
            LOGGER.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён,
            # то значит или потеряно соединение или пользователь
            # ввёл exit. Поскольку все события обработываются в потоках,
            # достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break

if __name__ == '__main__':
    main()
