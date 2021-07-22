import sys
import os
import argparse
import logging
import configparser
import logs.configs.config_server_log
from common.variables import DEFAULT_PORT
from common.utils import *
from common.decos import log
from server.core import MessageProcessor
from server.database import ServerStorage
from server.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Инициализация логирования сервера.
LOGGER = logging.getLogger('server')


@log
def create_parser(default_port, default_address):
    '''Парсер аргументов коммандной строки.'''
    LOGGER.debug(
        f'Инициализация парсера аргументов коммандной строки: {sys.argv}')
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=default_port, type=int, nargs='?')
    parser.add_argument('-a', '--address', default=default_address, nargs='?')
    parser.add_argument('--no_gui', action='store_true')
    args = parser.parse_args(sys.argv[1:])
    listen_address = args.address
    listen_port = args.port
    gui_flag = args.no_gui
    LOGGER.debug('Аргументы успешно загружены.')
    return listen_address, listen_port, gui_flag


@log
def config_load():
    '''Парсер конфигурационного ini файла.'''
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по
    # умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_database.db3')
        return config


@log
def main():
    '''Основная функция'''
    # Загрузка файла конфигурации сервера
    config = config_load()

    # Загрузка параметров командной строки, если нет параметров, то задаём
    # значения по умоланию.
    listen_address, listen_port, gui_flag = create_parser(
        config['SETTINGS']['Default_port'],
        config['SETTINGS']['Listen_Address'])

    # Инициализация базы данных
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    # Создание экземпляра класса - сервера и его запуск:
    server = MessageProcessor(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Если  указан параметр без GUI то запускаем простенький обработчик
    # консольного ввода
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                # Если выход, то завршаем основной цикл сервера.
                server.running = False
                server.join()
                break

    # Если не указан запуск без GUI, то запускаем GUI:
    else:
        # Создаём графическое окуружение для сервера:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)

        # Запускаем GUI
        server_app.exec_()

        # По закрытию окон останавливаем обработчик сообщений
        server.running = False


if __name__ == '__main__':
    main()
