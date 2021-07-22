from setuptools import setup, find_packages

setup(name="Another_One_Messenger_Client",
      version="0.9.1",
      description="Messenger_Client",
      author="Mihail Pendyurin",
      author_email="mihail.pendyurin@rt.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome']
      )
