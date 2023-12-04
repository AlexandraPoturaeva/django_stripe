# django_stripe

Данный сервис выполнен в качестве учебного проекта по реализации Django + Stripe API бэкенда со следующим функционалом и условиями:
- 	Django Модель Item с полями (name, description, price).

API с двумя методами:
- 	GET /buy/{id}, c помощью которого можно получить Stripe Session Id для оплаты выбранного Item. При выполнении этого метода c бэкенда с помощью python библиотеки stripe должен выполняться запрос stripe.checkout.Session.create(...) и полученный session.id выдаваться в результате запроса
- 	GET /item/{id}, c помощью которого можно получить простейшую HTML страницу, на которой будет информация о выбранном Item и кнопка Buy. По нажатию на кнопку Buy должен происходить запрос на /buy/{id}, получение session_id и далее с помощью JS библиотеки Stripe происходить редирект на Checkout форму stripe.redirectToCheckout(sessionId=session_id)

Бонусные задачи:

- Запуск используя Docker;
- Использование environment variables;
- Просмотр Django Моделей в Django Admin;
- Запуск приложения на удаленном сервере, доступном для тестирования;
- Модель Order, в которой можно объединить несколько Item и сделать платёж в Stripe на содержимое Order c общей стоимостью всех Items;
- Модели Discount, Tax, которые можно прикрепить к модели Order и связать с соответствующими атрибутами при создании платежа в Stripe - в таком случае они корректно отображаются в Stripe Checkout форме;
- Реализовать Stripe Payment Intent.

## Технологии

[![Python](https://img.shields.io/badge/Python-464641?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Stripe](https://img.shields.io/badge/Stripe-464646?style=flat-square&logo=Stripe)](https://stripe.com/)

## Запуск проекта локально

Клонировать репозиторий: 

```
git clone https://github.com/AlexandraPoturaeva/django_stripe.git
```
Перейти в корень проекта:

```
cd .../django_stripe
```

Создать файл .env в корне проекта. Пример заполнения: 

```
STRIPE_PUBLISHABLE_KEY=stripe_publishable_key
STRIPE_SECRET_KEY=stripe_secret_key
BACKEND_DOMAIN=backend_domain
ALLOWED_HOSTS=*
```
Создать и активировать виртуальное окружение

Windows:

```
python -m venv venv
venv\Scripts\activate
```
Linux:

```
python -m venv venv
source venv\Scripts\activate
```

Установить зависимости из файла requirements.txt

```
pip install -r requirements.txt
```

При необходимости создать и применить миграции:

```
python manage.py makemigrations
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Запуск проекта в Docker

Создать директорию проекта и создать в ней файл .env. Пример заполнения: 

```
STRIPE_PUBLISHABLE_KEY=stripe_publishable_key
STRIPE_SECRET_KEY=stripe_secret_key
BACKEND_DOMAIN=backend_domain
ALLOWED_HOSTS=*
```

Выполнить в командной строке из директории проекта: 

```
docker pull ghcr.io/alexandrapoturaeva/django_stripe:release
```

Запустить контейнер: 

```
docker run --env-file=.env -p 8001:8000 ghcr.io/alexandrapoturaeva/django_stripe:release
```

## Тестирование проекта на удалённом сервере

Проект доступен по адресу http://109.68.212.196:8001/
