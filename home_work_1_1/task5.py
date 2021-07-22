'''Выполнить пинг веб-ресурсов yandex.ru, youtube.com
и преобразовать результаты из байтовового в строковый тип на кириллице'''



import subprocess

ping_hosts = [['ping', 'yandex.ru'], ['ping', 'youtube.com']]

for ping_now in ping_hosts:

    ping = subprocess.Popen(ping_now, stdout=subprocess.PIPE)

   
    for line in ping.stdout:
        # print(line)
        line = line.decode('cp866').encode('utf-8')
        print(line.decode('utf-8'))

