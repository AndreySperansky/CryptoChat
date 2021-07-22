from setuptools import setup, find_packages

setup(name="mess_server",
      version="0.8.3",
      description="mess_server",
      author="Ivan Ivanov",
      author_email="iv.iv@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome']
      )
