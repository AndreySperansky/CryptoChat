import dis

# Метакласс для проверки соответствия сервера:
class ServerMaker(type):
    def __init__(self, clsname, bases, clsdict):
        # clsname - экземпляр метакласса - Server
        # bases - кортеж базовых классов - ()
        # clsdict - словарь атрибутов и методов экземпляра метакласса
        # {'__module__': '__main__',
        # '__qualname__': 'Server',
        # 'port': <descrptrs.Port object at 0x000000DACC8F5748>,
        # '__init__': <function Server.__init__ at 0x000000DACCE3E378>,
        # 'init_socket': <function Server.init_socket at 0x000000DACCE3E400>,
        # 'main_loop': <function Server.main_loop at 0x000000DACCE3E488>,
        # 'process_message': <function Server.process_message at 0x000000DACCE3E510>,
        # 'process_client_message': <function Server.process_client_message at 0x000000DACCE3E598>}

        # Список методов, которые используются в функциях класса:
        methods = []
        # Атрибуты, используемые в функциях классов
        attrs = []
        # перебираем ключи
        for func in clsdict:
            # Пробуем
            try:
                # Возвращает итератор по инструкциям в предоставленной функции
                # , методе, строке исходного кода или объекте кода.
                ret = dis.get_instructions(clsdict[func])
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEAD7C8>
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEADF48>
                # ...
                # Если не функция то ловим исключение
                # (если порт)
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for i in ret:
                    print(i)
                    # i - Instruction(opname='LOAD_GLOBAL', opcode=116, arg=9, argval='send_message',
                    # argrepr='send_message', offset=308, starts_line=201, is_jump_target=False)
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        print(methods)
        # Если обнаружено использование недопустимого метода connect, бросаем исключение:
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        # Если сокет не инициализировался константами SOCK_STREAM(TCP) AF_INET(IPv4), тоже исключение.
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)


############################################################################
# Метакласс для проверки корректности клиентов:
############################################################################

class ClientMaker(type):
    def __init__(self, clsname, bases, clsdict):
        # Список методов, которые используются в функциях класса:
        methods = []
        for func in clsdict:
            # Пробуем
            try:
                ret = dis.get_instructions(clsdict[func])
                # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)