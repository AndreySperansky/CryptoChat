Common package
=================================================

Пакет общих утилит, использующихся в разных модулях проекта.

Скрипт decos.py
---------------

.. automodule:: common.decos
	:members:
	
Скрипт descryptors.py
---------------------

.. autoclass:: common.descryptors.Port
    :members:
   
Скрипт errors.py
---------------------
   
.. autoclass:: common.errors.ServerError
   :members:
   
Скрипт metaclasses.py
-----------------------

.. autoclass:: common.metaclasses.ServerMaker
   :members:
   
.. autoclass:: common.metaclasses.ClientMaker
   :members:
   
Скрипт utils.py
---------------------

common.utils. **get_message** (client)


	Функция приёма сообщений от удалённых компьютеров. Принимает сообщения JSON,
	декодирует полученное сообщение и проверяет что получен словарь.

common.utils. **send_message** (sock, message)


	Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет.


Скрипт variables.py
---------------------

Содержит разные глобальные переменные проекта.