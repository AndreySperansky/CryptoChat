"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес
сетевого узла должен создаваться с помощью функции ip_address().
"""
from ipaddress import ip_address
from subprocess import  Popen, PIPE
import socket


def host_ping(ips, timeout=500, request=1):
    output = {'Reachable': "", 'Unreachable': ""}    # словарь с результатами
    for ip in ips:
        try:
            ip = ip_address(ip)
            # перехват исключений типа ValueError:
            # 'yandex.ru' does not appear to be an IPv4 or IPv6 address
        except ValueError:
            ip = socket.gethostbyname(ip)
        process = Popen(f"ping {ip} -w {timeout} -n {request}", shell=False, stdout=PIPE)
        process.wait()
        # проверяем код завершения подпроцесса
        if process.returncode == 0:
            output['Reachable'] += f'{str(ip)}\n'
            res_string = f'{ip} - Узел доступен'
        else:
            output['Unreachable'] += f'{str(ip)}\n'
            res_string = f'{ip} - Узел недоступен'
        print(res_string)
    return output


if __name__ == '__main__':
    ip_addr = ['yandex.ru', 'google.com', '1.2.3.4', '8.8.8.8', '192.168.1.51', '192.168.1.1', '192.168.1.51', '192.168.1.41']
    host_ping(ip_addr)