# Task3

'''
3.	Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
'''

b_word1 = b'attribute'     #OK
# b_word2 = b'класс'       error: Byte literal contains characters > 255
# b_word3 = b'функция'     error: Byte literal contains characters > 255
b_word4 = b'type'          #OK