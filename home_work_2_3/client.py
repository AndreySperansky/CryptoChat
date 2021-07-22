"""Программа-клиент"""

import sys
import json
import time
import socket
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
from metaclasses import ClientMaker


# Инициализация клиентского логера
LOGGER = logging.getLogger('client')

###################################################################################
# Класс формировки и отправки сообщений на сервер и взаимодействия с пользователем.
###################################################################################

class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Функция создаёт словарь с сообщением о выходе.
    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # Функция запрашивает кому отправить сообщение и само сообщение, и отправляет полученные данные на сервер.
    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            LOGGER.info(f'Отправлено сообщение для пользователя {to}')
        except:
            LOGGER.critical('Потеряно соединение с сервером.')
            exit(1)

    # Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Завершение соединения.')
                LOGGER.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    # Функция выводящяя справку по использованию.
    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


# Класс-приёмник сообщений с сервера. Принимает сообщения, выводит в консоль.
class ClientReader(threading.Thread , metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Основной цикл приёмника сообщений, принимает сообщения, выводит в консоль. Завершается при потере соединения.
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                LOGGER.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f'Потеряно соединение с сервером.')
                break


# Функция генерирует запрос о присутствии клиента
@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


# Функция разбирает ответ сервера на сообщение о присутствии, возращает 200 если все ОК или генерирует исключение при\
# ошибке.
@log
def process_response_ans(message):
    LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


# Парсер аргументов коммандной строки
@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        LOGGER.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)

    return server_address, server_port, client_name


def main():
    # Сообщаем о запуске
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    LOGGER.info(f'Запущен клиент с парамертами: '
                f'адрес сервера: {server_address}, '
                f'порт: {server_port}'
                f'имя пользователя: {client_name}')
    # Инициализация сокета и сообщение серверу о нашем появлении


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_address, server_port))

        message_to_server = create_presence(client_name)
        send_message(s, message_to_server)


        try:

            answer = process_response_ans(get_message(s))
            LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером.')
        except json.JSONDecodeError:
            LOGGER.error('Не удалось декодировать полученную Json строку.')
            exit(1)
        except ServerError as error:
            LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            exit(1)
        except ReqFieldMissingError as missing_error:
            LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            exit(1)
        except (ConnectionRefusedError, ConnectionError):
            LOGGER.critical(
                f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
            exit(1)
        else:
            # Если соединение с сервером установлено корректно, запускаем клиенский процесс приёма сообщний
            module_reciver = ClientReader(client_name , s)
            module_reciver.daemon = True
            module_reciver.start()

            # затем запускаем отправку сообщений и взаимодействие с пользователем.
            module_sender = ClientSender(client_name , s)
            module_sender.daemon = True
            module_sender.start()
            LOGGER.debug('Запущены процессы')

        # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках, достаточно просто завершить цикл.
            while True:
                time.sleep(1)
                if module_reciver.is_alive() and module_sender.is_alive():
                    continue
                break


if __name__ == '__main__':
    main()
