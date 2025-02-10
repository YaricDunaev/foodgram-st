# Foodgram Project

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

Foodgram — это веб-платформа, где пользователи могут делиться своими рецептами, добавлять понравившиеся рецепты в избранное и подписываться на других авторов. Зарегистрированные пользователи также могут использовать сервис «Список покупок», который помогает составить перечень продуктов, необходимых для приготовления выбранных блюд.

## Структура проекта

Проект включает следующие страницы:
- Главная страница
- Страница входа
- Страница регистрации
- Страница рецепта
- Страница пользователя
- Страница подписок
- Избранное
- Список покупок
- Создание и редактирование рецепта
- Страница смены пароля
- Статические страницы: «О проекте» и «Технологии»

## Начало работы

1. **Клонирование репозитория**

   Для начала работы с проектом необходимо клонировать репозиторий:

   ```bash
   git clone https://github.com/YaricDunaev/foodgram-st.git
   ```

2. **Настройка окружения**

   Перейдите в директорию infra и создайте файл .env, используя .env.example как шаблон:

   ```bash
   cd foodgram-st/infra
   touch .env
   ```

3. **Запуск проекта**

   В директории `infra`:

   ```bash
   docker-compose up
   ```

4. **Миграции и создание суперпольователя**

   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Загрузка ингредиентов**

   Заполните базу ингредиентами ( написана команда `load_ingredients` в `core/commands/load_ingredients.py` она позволяет загружать данные из `.csv` файла ):
   
   ```bash
   docker-compose exec backend python manage.py load_ingredients
   ```
## Доступ к приложению

- Веб-интерфейс: [Localhost](http://localhost/)
- API документация: [Localhost docs](http://localhost/api/docs/)
- Админ-панель: [Localhost admin](http://localhost/admin/)

## Автор:

Дунаев Ярослав

**email**: yaricdunaev0@gmail.com
