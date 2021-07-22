import subprocess

process = []

while True:
    action = input('Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')
    if action == 'q':
        break
    elif action == 's':
        # Запускаем сервер!
        process.append(subprocess.Popen('python server.py'))
    elif action == 'k':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем клиентов:
        for i in range(clients_count):
            process.append(subprocess.Popen(f'python client.py -n User_{i + 1}'))
    elif action == 'x':
        while process:
            process.pop().kill()