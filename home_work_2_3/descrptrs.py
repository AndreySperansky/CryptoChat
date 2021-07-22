import logging
logger = logging.getLogger('server')

# Дескриптор для описания порта:
class Port:
    def __set__(self, instance, value):
        # instance - <__main__.Server object at 0x000000D582740C50>
        # value - 7777
        if not 1023 < value < 65536:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        # owner - <class '__main__.Server'>
        # name - port
        self.name = name

