# Task3

'''
3.	Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
'''

b_word1 = b'attribute'     #OK
# b_word2 = b'класс'       error: Byte literal contains characters > 255
# b_word3 = b'функция'     error: Byte literal contains characters > 255
b_word4 = b'type'          #OK

VAR_1 = "attribute"
VAR_2 = "класс"
VAR_3 = "функция"
VAR_4 = "type"

VAR_LIST = [VAR_1, VAR_2, VAR_3, VAR_4]

for el in VAR_LIST:
    try:
        print(bytes(el, 'ascii'))
    except UnicodeEncodeError:
        print(f'Слово "{el}" невозможно записать в виде байтовой строки')


# ВТОРОЙ ВАРИАНТ

# for el in VAR_LIST:
#     try:
#         print('Слово записано в байтовом типе:', eval(f'b"{el}"') )
#     except SyntaxError:
#         print(f'Слово "{el}" невозможно записать в байтовом типе с помощью префикса b')