"""Программа-лаунчер"""

import subprocess

PROCESSES = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESSES.append(subprocess.Popen('python server.py',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n user1',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n user2',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
        PROCESSES.append(subprocess.Popen('python client.py -n user3',
                                          creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESSES:
            VICTIM = PROCESSES.pop()
            VICTIM.kill()
