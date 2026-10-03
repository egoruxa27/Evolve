# Evolve

Evolve — web-приложение для управления личными задачами с лёгкой
геймификацией. Оно помогает не только записывать дела, но и видеть прогресс:
за выполненные задачи пользователь получает опыт и повышает уровень.

Проект создаётся как портфолио-проект: здесь важны не только страницы задач,
но и устройство приложения — кастомная модель пользователя, PostgreSQL,
контейнеризация и фоновые задачи на Celery.

## Что уже реализовано

- регистрация, вход и выход из аккаунта;
- кастомная модель пользователя с уникальными email и никнеймом;
- профиль пользователя, загрузка аватарки и fallback по первой букве никнейма;
- создание задач с описанием, дедлайном и наградой в опыте;
- статусы задач: `Не начата`, `В процессе`, `Выполнена`, `Провалена`;
- категории задач: создание, редактирование, удаление и фильтрация;
- история и подробная страница задачи;
- начисление опыта и уровни пользователя;
- пагинация списка задач;
- настройки для PostgreSQL, Redis и Celery worker;
- Docker Compose-конфигурации для разработки и production.

## В разработке

Разрабатывается интеграция с Telegram для уведомлений о дедлайнах. Планируемый
сценарий — отправлять пользователю напоминание, когда до дедлайна задачи
остаётся заданное время (например, один час), чтобы он успел завершить задачу
до того, как она будет просрочена. Отправку уведомлений будет выполнять
Celery worker с использованием Redis в качестве брокера.

Telegram-уведомления пока не входят в список реализованных возможностей.

## Технологии

- Python;
- Django 6.1;
- PostgreSQL;
- Redis;
- Celery;
- Docker и Docker Compose;
- Pillow;
- python-dotenv;
- Django Debug Toolbar;
- HTML и CSS.

## Структура проекта

```text
Evolve/
├── apps/
│   ├── tasks/                # задачи, категории, формы и представления
│   └── users/                # пользователи, авторизация и профили
├── config/                   # настройки Django и конфигурация Celery
├── docker/                   # Docker Compose-конфигурации
├── media/                    # загруженные пользовательские файлы
├── static/                   # статические файлы и CSS
├── templates/                # HTML-шаблоны
├── .env.example              # пример переменных окружения
├── manage.py
└── requirements.txt
```

## Запуск через Docker

### Требования

- Docker Desktop или Docker Engine с Docker Compose.

### 1. Подготовьте переменные окружения

Создайте `.env` в корне проекта на основе `.env.example`. Для локального
запуска задайте как минимум:

```env
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=evolve
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Не используйте эти демонстрационные значения для production. Храните реальные
секреты вне репозитория.

### 2. Запустите сервисы

Из корня проекта выполните:

```bash
docker compose -f docker/compose.yaml -f docker/compose.dev.yaml up --build
```

Compose запустит PostgreSQL, Redis, Django-приложение и Celery worker.
Приложение будет доступно по адресу <http://127.0.0.1:8000/>.

В отдельном терминале примените миграции и создайте администратора:

```bash
docker compose -f docker/compose.yaml -f docker/compose.dev.yaml exec web python manage.py migrate
docker compose -f docker/compose.yaml -f docker/compose.dev.yaml exec web python manage.py createsuperuser
```

## Локальный запуск без Docker

В этом режиме PostgreSQL и Redis должны быть запущены отдельно и доступны
с настройками, указанными в конфигурации проекта.

### 1. Создайте виртуальное окружение и установите зависимости

Windows PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Настройте `.env`

Создайте файл `.env` по примеру выше и укажите параметры доступной PostgreSQL.

### 3. Выполните миграции и запустите приложение

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Чтобы вручную запустить Celery worker из корня проекта:

```bash
celery -A config worker -l INFO
```

## Основные маршруты

| Раздел | URL |
| --- | --- |
| Вход | `/users/login/` |
| Регистрация | `/users/register/` |
| Профиль | `/users/profile/` |
| Список задач | `/tasks/` |
| Создание задачи | `/tasks/create/` |
| История задач | `/tasks/history/` |
| Админ-панель | `/admin/` |

## Тесты

Запустите тесты Django:

```bash
python manage.py test
```

## Дальнейшее развитие

- завершить Telegram-интеграцию и уведомления о приближающихся дедлайнах;
- добавить периодическую постановку уведомлений в очередь;
- расширить тесты и обработку ошибок фоновых задач;
- развивать систему прогресса и геймификации;
- улучшить мобильную версию и подготовить production-деплой.

## Статус

Проект активно разрабатывается. Основной функционал управления задачами и
прогрессом реализован; Telegram-уведомления о дедлайнах находятся в разработке.
