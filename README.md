# Announcement Channel with Real-time Features

**Студент:** Кухта Данило Ігорович  
**Група:** КВ-51мп  
**Лабораторна робота:** №2 - Організація спільної роботи користувачів Web-додатка  

## Опис завдання
Розробити функції обміну даними між користувачами Web-додатка у реальному часі та адміністрування користувачами, використовуючи Django Channels та WebSocket.

## Посилання на звіт
[Звіт на Google Drive](https://docs.google.com/document/d/1XQotyVttE2Tj13TXXfdrf44mZ3hwkmLQ9cOPkmIp39M/edit?usp=sharing)

## Real-time функції
- ✅ WebSocket з'єднання для всіх авторизованих користувачів
- ✅ Відстеження онлайн користувачів в реальному часі
- ✅ Real-time оновлення реакцій на оголошення
- ✅ Система персональних сповіщень
- ✅ Адміністративна панель для моніторингу онлайн користувачів
- ✅ Логування активності користувачів

## Технології
- Python 3.11+
- Django 4.2
- Django Channels 4.0
- Redis 7.0
- WebSocket
- Bootstrap 5

## Встановлення та запуск

### Вимоги
- Python 3.11+
- Redis Server

### Кроки встановлення

1. Клонування репозиторію:
``` bash
git clone https://github.com/joe1i/WEBTECH-lab-2.git
cd WEBTECH-lab-2
``` 
2. Створення віртуального середовища:
``` bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
``` 
3. Встановлення залежностей:
``` bash
pip install -r requirements.txt
``` 
4. Запуск Redis
``` bash
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows/Docker
docker run -d -p 6379:6379 redis:alpine
```
5. Міграції бази даних:
``` bash
python manage.py migrate
python manage.py createsuperuser
```
6. Запуск сервера:
``` bash
python manage.py runserver
```
7. (Опціонально) Наповнити базу тестовими даними:
``` bash
python manage.py populate_db
```
Дані тестового адміна для входу:
``` bash
email: admin@example.com
password: adminpass123
```