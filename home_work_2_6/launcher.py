import subprocess

users = [
    'python client.py -n трус -ps 123',
    'python client.py -n балбес -ps 123',
    'python client.py -n бывалый -ps 123',
]



def main():
    process = []

    while True:
        action = input(
            'Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')
        if action == 'q':
            break
        elif action == 's':
            # Запускаем сервер!
            process.append(
                subprocess.Popen(
                    'python server.py',
                    creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')

            # Запускаем клиентов:
            for i in range(len(users)):
                process.append(subprocess.Popen(f'{users[i]}'))

        elif action == 'x':
            while process:
                process.pop().kill()


if __name__ == '__main__':
    main()