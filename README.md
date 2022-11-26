# Yatube
Социальная сеть блогеров (web приложение)

### Описание
Модель приложения позволяет создавать записи на любую тему и прикреплять к ним картинки. Записи разбиты по группам. Можно комментировать записи и подписываться на авторов. Создание и редактирование контента доступно только авторизованым пользователям. В страницах управления пользователем использованы кастомизированные HTML шаблоны. Настроена админ панель и пагинация. Для проекта написан блок юнит тестов с использованием встроенных в django инструментов запуска тестового сервера и клиента.

### Технологии
Python 3.7
Django 2.2.19

### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
py -3.7 -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
- В папке с файлом manage.py вы полните команды:
	- Выполните миграцию схемы базы данных
	```
	python manage.py migrate
	```
	- Создайте первого пользователя
	```
	python manage.py createsuperuser
	```
	- Запустите dev-сервер:
	```
	python manage.py runserver
	```
Адреса сервера и админки по умолчанию:
http://127.0.0.1:8000

http://127.0.0.1:8000/admin/

### Авторы
Алексей
