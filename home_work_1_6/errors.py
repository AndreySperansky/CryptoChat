"""Ошибки"""

class IncorrectDataRecivedError(Exception):
    """
    Исключение  - некорректные данные получены от сокета
    """
    def __str__(self):
        return 'Принято некорректное сообщение от удалённого компьютера.'


class NonDictInputError(Exception):
    """
    Исключение - аргумент функции не словарь
    """
    def __str__(self):
        return 'Аргумент функции должен быть словарём.'

class ReqFieldMissingError(Exception):
    """
    Ошибка - отсутствует обязательное поле в принятом словаре
    """
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'
