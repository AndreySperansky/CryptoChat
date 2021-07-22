"""Декораторы"""

import sys
import logging
import logs.configs.config_server_log
import logs.configs.config_client_log
import traceback
import inspect

# метод определения модуля, источника запуска.
# Метод find () возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке.
# Если его не найдено, - возвращает -1.

if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    LOGGER = logging.getLogger('server')
else:
    # ну, раз не сервер, то клиент
    LOGGER = logging.getLogger('client')


# Реализация в виде функции
def log(func_to_log):
    """Функция-декоратор"""
    def log_saver(*args, **kwargs):
        """Обертка"""
        ret = func_to_log(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} из модуля {func_to_log.__module__}.')
        return ret
    return log_saver


# Реализация в виде класса
# class Log:
#     """Класс-декоратор"""
#     def __call__(self, func_to_log):
#         def log_saver(*args, **kwargs):
#             """Обертка"""
#             ret = func_to_log(*args, **kwargs)
#             LOGGER.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}. '
#                          f'Вызов из модуля {func_to_log.__module__}. Вызов из'
#                          f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
#                          f'Вызов из функции {inspect.stack()[1][3]}')
#             return ret
#         return log_saver
