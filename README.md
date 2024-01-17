# Описание проекта Posts Service
Сервис для публикации отзывов, с комментариями и подписками на авторов.

## Стек использованных технологий
Django
Unittest
PostgreSQL
Django ORM

## Запуск проекта
Клонировать репозиторий:
```bash
git@github.com:akanelovw/posts-service.git
```

Перейти в клонированный репозиторий:
```bash    
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```

Выполнить миграции:
```bash
python manage.py migrate
```

Запустить проект:
```bash  
python manage.py runserver
```
