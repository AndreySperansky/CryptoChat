"""Кофнфиг клиентского логгера"""

import sys
import os
import logging
sys.path.append('..\..')
from common.variables import LOGGING_LEVEL


# создаём формировщик логов (formatter):
CLIENT_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
# __file__ - это путь к файлу, из которого был загружен модуль, если он был загружен из файла
# это может быть относительный путь
# функция os.path.abspath() используется для превращения этого в абсолютный путь
# функция os.path.dirname() просто удаляет последний сегмент пути.
PATH = os.path.join(PATH, '..\logfiles\client.log')

# создаём потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.FileHandler(PATH, encoding='utf8')
LOG_FILE.setFormatter(CLIENT_FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    print(PATH)
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
