"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import os
import re


# путь к текущей рабочей директории
path = os.getcwd()
print(path)

# список файлов в текущем рабочем каталоге
lst_files = os.listdir(path)
print(lst_files)

os_prod_list = []
os_name_list = []
os_code_list = []
os_type_list = []
headers = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]

def find_file(lst_files, path): # функция принимает os.listdir, и путь на папку
    try:
        for f_n in lst_files:
            if os.path.isfile(path +'/' + f_n): #проверяем что перед нами, файл или нет
            # Проверяем расширение файла и исключаем ненужные файлы
                if f_n.find('.txt') != -1 and f_n.find('.py') == -1 and f_n.find('.csv') == -1:
                    get_data(f_n)
            else:
                #Если это директория, то проваливаемся в нее
                find_file(os.listdir(path +'/' + f_n), path + '/' + f_n)
    except Exception as err:
        print(err, path +'/' + f_n)



def get_data(file_name):

    # with open(file_name, "r") as f_o:
    #     for line in f_o:
    #         match1 = re.search(r"Изготовитель\s+системы:\s+(?P<manufacturer>\w+)", line)
    #         match2 = re.search(r"Название\s+ОС:\s+(?P<name>\w+)", line)
    #         match3 = re.search(r"Код\s+продукта:\s+(?P<code>[-\w]+)", line)
    #         match4 = re.search(r"Тип\s+системы:\s+(?P<type>[-\w]+\s+\w+)", line)
    #         if match1:
    #             v1 = match1.groupdict()
    #             os_prod_list.append(v1["manufacturer"])
    #         elif match2:
    #             v2 = match2.groupdict()
    #             os_name_list.append(v2["name"])
    #         elif match3:
    #             v3 = match3.groupdict()
    #             os_code_list.append(v3["code"])
    #         elif match4:
    #             v4 = match4.groupdict()
    #             os_type_list.append(v4["type"])


    with open(file_name, "r") as f_o:
        for line in f_o:
            match1 = re.search(r"(Изготовитель\s+системы:)\s+(\w+)", line)
            match2 = re.search(r"(Название\s+ОС:)\s+(\w+\s+\w+\s+\d+)", line)
            match3 = re.search(r"(Код\s+продукта:)\s+([-\w]+)", line)
            match4 = re.search(r"(Тип\s+системы:)\s+([-\w]+\s+\w+)", line)

            if match1:
                os_prod_list.append(match1.group(2))
            elif match2:
                os_name_list.append(match2.group(2))
            elif match3:
                os_code_list.append(match3.group(2))
            elif match4:
                os_type_list.append(match4.group(2))

        # print(os_prod_list, os_name_list, os_code_list, os_type_list)


find_file(lst_files, path)

print(headers, os_prod_list, os_name_list, os_code_list, os_type_list, sep="\n")



main_data = []
main_data.append(headers)
main_data.append(os_prod_list)
main_data.append(os_name_list)
main_data.append(os_code_list)
main_data.append(os_type_list)
print(main_data)


def write_to_csv():
    with open('data_write.csv', 'w') as foo:
        f_n_writer = csv.writer(foo)
        for row in main_data:
            f_n_writer.writerow(row)

    with open('data_write.csv') as foo:
        print(foo.read())

write_to_csv()


