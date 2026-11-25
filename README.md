# Детский центр «Умный ребёнок»

Веб-приложение на Django: каталог кружков и мастер-классов, расписание, запись на пробное занятие, личный кабинет родителя и административная часть.

## Стек

- Python 3.11+, Django 6.1
- SQLite в разработке, PostgreSQL в эксплуатации
- HTML5, CSS3, JavaScript без фронтенд-фреймворков
- WhiteNoise для статических файлов

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
# в .env задайте свой DJANGO_SECRET_KEY
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
python manage.py runserver 127.0.0.1:8000
```

Секреты в репозиторий не попадают: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` и параметры БД читаются из `.env` или переменных окружения. Файл `.env` добавлен в `.gitignore`.

## Демо-доступ

Демо-учётные записи создаются командой `seed_demo`:

- родитель: `parent@example.com` / `demo12345`
- администратор: `admin` / `admin12345`

Перед эксплуатацией пароли демо-учёток нужно сменить. На странице входа подсказка с паролем не выводится.

## Проверки

```powershell
python manage.py test
python manage.py check
$env:DJANGO_SECURE_SSL="1"; $env:DJANGO_HSTS_SECONDS="31536000"; python manage.py check --deploy
```

## Безопасность

- CSRF включён для всех POST-форм, выход выполняется только POST-запросом.
- Пароли хранятся в виде хешей PBKDF2-SHA256, включены валидаторы сложности.
- Вход ограничен: 5 неудачных попыток на IP и логин, блокировка 15 минут.
- Медицинские справки: только PDF, JPG, PNG до 5 МБ; тип проверяется по сигнатуре, файл переименовывается в UUID.
- При `DEBUG=False` пользователь видит страницы 404/500 без трассировки и настроек.
- Загруженные файлы хранятся в `media/` вне статики и не исполняются веб-сервером.
