"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
import sys
from ipaddress import ip_address
from task_1 import host_ping

def host_range_ping():
    while True:
    # запрос первоначального адреса
        start_ip = input('Введите первоначальный адрес: \n')
        try:
        # смотрим чему равен последний октет
            fin_oct = int(start_ip.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        # Запрос на количество проверяемых адресов
        ip_range = input('Сколько адресов проверить?: ')
        if not ip_range.isnumeric():
            print('Необходимо ввести число: ')
        else:
            if (fin_oct + int(ip_range)) > 254:
                print(f"можем менять только последний октет, т.е."
                      f"максимальное число хостов для проверки: {254 - fin_oct}")
            else:
                break

    host_list = []
    # формируем список ip адресов
    [host_list.append(str(ip_address(start_ip) + x)) for x in range(int(ip_range))]
    # пердаем список в функцию из задания 1 для проверки доступности
    return host_ping(host_list)


if __name__ == '__main__':
    host_range_ping()





