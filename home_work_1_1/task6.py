'''Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию. Принудительно открыть файл
в формате Unicode и вывести его содержимое'''

import locale

src = ['сетевое программирование', 'сокет', 'декоратор']
# src = ['new', 'let', 'run']

# Создаем файл
with open('resurs.txt', 'w+', encoding="utf-8") as f_n:
    for elm in src:
        f_n.write(elm + '\n')
    f_n.seek(0)

print(f_n)  # печатаем объект файла, что бы узнать его кодировку

file_coding = locale.getpreferredencoding()
print(file_coding)

# Читаем из файла
with open('resurs.txt', 'r') as f_n:
    for el_str in f_n:
        # print(el_str)
        el_ascii = el_str.encode('ascii', 'replace')
        print(el_ascii)
    f_n.seek(0)