
'''Преобразовать слова «разработка», «администрирование», «protocol»,
 «standard» из строкового представления в байтовое и выполнить обратное
  преобразование (используя методы encode и decode).'''

wrds = [
    'разработка',
    'администрирование',
    'protocol',
    'standard'
]
for w in wrds:
    a = w.encode('utf-8')
    print(a, type(a))
    b = bytes.decode(a, 'utf-8')
    print(b, type(b))
    print('***' *15)

