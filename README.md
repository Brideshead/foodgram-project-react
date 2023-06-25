![foodgram-project-react_workflow](https://github.com/Brideshead/foodgram-project-react/actions/workflows/foodgram-project-react.yml/badge.svg)


# Foodgram продуктовый помощник. Дипломный проект студента Яндекс Практикум Богоевич Александра

Проект доступен по адресу: http://51.250.87.5/

### Документация Foodgram
Документация доступна по адресу: http://51.250.87.5/api/docs/

## Описание проекта Foodgram:
Сайт - продуктовый помощник. На нём пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд и скачивать его в формате .txt

## Cтек используемых технологий:
-Python
-Django
-Django REST Framework
-Docker
-Github-Actions
-Postgresql
-Gunicorn
-Nginx

## Как развернуть проект:

### Клонируем репозиторий и и переходим в него:

```bash
git clone git@github.com:brideshead/foodgram_project_react.git
```
```bash
cd foodgram_project_react
```

### Создать .env файл:
Путь для создания: cd infra/
Содержимое:
DB_ENGINE=django.db.backends.postgresql 
DB_NAME=postgres 
POSTGRES_USER=postgres 
POSTGRES_PASSWORD=postgres 
DB_HOST=db 
DB_PORT=5432

### В settings.py добавляем следующее:
```python
from dotenv import load_dotenv

load_dotenv()

...

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

```

### Из директории infra/ запускаем docker-compose
```bash
sudo docker-compose up -d --build 
```

### Выполняем миграции:
```bash
sudo docker-compose exec backend python manage.py makemigrations users 
```
```bash
sudo docker-compose exec backend python manage.py makemigrations recipes 
```
```bash
sudo docker-compose exec backend python manage.py migrate --run-syncdb
```
### Создаем суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser 
```

### Собираем статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input 
```
### Дополнительно наполянем БД ингредиентами командой:

```bash
sudo docker-compose exec backend python manage.py load_tags
```



### Автор проекта:

[Богоевич Александр](https://github.com/Brideshead)
