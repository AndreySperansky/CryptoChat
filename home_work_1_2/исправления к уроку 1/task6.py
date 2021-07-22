'''Создать текстовый файл test_file.txt, заполнить его тремя строками:
«сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию. Принудительно открыть файл
в формате Unicode и вывести его содержимое'''

import locale

src = ['сетевое программирование', 'сокет', 'декоратор']
# src = ['new', 'let', 'run']

# Создаем файл
with open('resurs.txt', 'w+', encoding="utf-8") as foo:
    for elm in src:
        foo.write(elm + '\n')
    foo.seek(0)

print(foo)  # печатаем объект файла, что бы узнать его кодировку

file_coding = locale.getpreferredencoding()
print(file_coding)

# Читаем из файла
with open('resurs.txt', 'r', encoding="utf-8") as foo:
    for el_str in foo:
        print(el_str, end="")
    foo.seek(0)