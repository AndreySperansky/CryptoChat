import socket
import sys
import os
import argparse
import logging
import select
import threading
import configparser
import time
import logs.configs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import *
from common.utils import *
from decors import log
from descrptrs import Port
from metaclasses import ServerMaker
from server_database import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, create_stat_model, ConfigWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem


# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')

# Флаг что был подключён новый пользователь, нужен чтобы не мучать BD
# постоянными запросами на обновление
new_connection = False
conflag_lock = threading.Lock()

################################################################################################
# Парсер аргументов коммандной строки.
################################################################################################


@log
def createParser(default_port, default_address):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=default_port, )
    parser.add_argument('-a', '--address', default=default_address, )
    args = parser.parse_args(sys.argv[1:])
    listen_port = args.port
    listen_address = args.address
    return listen_address, listen_port


################################################################################################
# Основной класс сервера
################################################################################################


class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # База данных сервера
        self.database = database


        # Список подключённых клиентов.
        self.clients = []

        # Список сообщений на отправку.
        self.messages = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.names = dict()

        # Конструктор предка
        super().__init__()

    def init_socket(self):
        LOGGER.info(
            f'Запущен сервер, порт для подключений: {self.port} , '
            f'адрес с которого принимаются подключения: {self.addr}. ' 
            f'Если адрес не указан, принимаются соединения с любых адресов.')

        # Готовим сокет
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.addr, self.port))
            s.settimeout(1)


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
                        recv_data_lst, send_data_lst, err_lst = \
                            select.select(self.clients, self.clients, [], 0)
                except OSError as err:
                    LOGGER.error(f'Ошибка работы с сокетами: {err}')

                # принимаем сообщения и если ошибка, исключаем клиента.
                if recv_data_lst:
                    for client_with_message in recv_data_lst:
                        try:
                            self.process_client_message(get_message(client_with_message), client_with_message)
                        except (OSError):
                            # Ищем клиента в словаре клиентов и удаляем его из него
                            # и  базы подключённых клиентов
                            LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                            for name in self.names:
                                if self.names[name] == client_with_message:
                                    self.database.user_logout(name)
                                    del self.names[name]
                                    break
                            self.clients.remove(client_with_message)

                # Если есть сообщения, обрабатываем каждое.
                for message in self.messages:
                    try:
                        self.process_message(message, send_data_lst)
                    except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                        LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна')
                        self.clients.remove(self.names[message[DESTINATION]])
                        self.database.user_logout(message[DESTINATION])
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
        global new_connection
        LOGGER.debug(f'Разбор сообщения от клиента : {message}')

        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован, регистрируем,
            # иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return

        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message and self.names[message[SENDER]] == client:
            self.messages.append(message)
            self.database.process_message(
                message[SENDER], message[DESTINATION])
            return

        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            # Добавлено в связи с server_database.py
            self.database.user_logout(message[ACCOUNT_NAME])
            LOGGER.info(
                f'Клиент {message[ACCOUNT_NAME]} корректно отключился от сервера.')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return


        # Если это запрос контакт-листа
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message and \
                self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            send_message(client, response)

        # Если это добавление контакта
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        # Если это удаление контакта
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and USER in message \
                and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client, RESPONSE_200)

        # Если это запрос известных пользователей
        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0]
                                   for user in self.database.users_list()]
            send_message(client, response)


        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return


def main():
    # Загрузка файла конфигурации сервера
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    # Загрузка параметров командной строки, если нет параметров, то задаём
    # значения по умоланию.
    listen_address, listen_port = createParser(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])



    # Инициализация базы данных
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file'])
    )

    # Создание экземпляра класса - сервера.
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    # server.init_socket()

    # Создаём графическое окуружение для сервера:
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # Инициализируем параметры в окна
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    # Функция обновляющяя список подключённых, проверяет флаг подключения, и
    # если надо обновляет список
    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    # Функция создающяя окно со статистикой клиентов
    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    # Функция создающяя окно с настройками сервера.
    def server_config():
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    # Функция сохранения настроек
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    # Запускаем GUI
    server_app.exec_()

if __name__ == '__main__':
    main()
