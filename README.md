# Детский центр «Умный ребёнок»

Сайт детского развивающего центра: направления, расписание, мастер-классы,
педагоги, абонементы, запись на пробное занятие и личный кабинет родителя.
Django-версия макетов из занятия 6 (вариант 22).

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "django==6.1.3"
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py runserver
```

Сайт — <http://127.0.0.1:8000/>, админка — <http://127.0.0.1:8000/admin/>.

Демо-доступ родителя: `parent@example.com` / `demo12345`.
Администратор: `admin` / `admin12345`.

## Структура

```
kids_project/        настройки, корневые маршруты
kids/
  models.py          направления, группы, педагоги, расписание, заявки, абонементы
  forms.py           BookingForm, ContactForm, RegisterForm, LoginForm
  views.py           страницы, JSON-представления, обработчик 404
  urls.py            именованные маршруты приложения
  admin.py           регистрация моделей
  management/commands/seed_demo.py
  templates/kids/    шаблоны страниц и partials
templates/base.html  общий каркас: шапка, меню, поиск, подвал
static/css/style.css стили UI-kit занятия 6 + служебные классы
static/js/main.js    бургер, живой поиск, фильтр каталога, валидация форм
static/img/          favicon
docs/                скриншоты и отчёты валидаторов
```

## Страницы

`/` — главная, `/clubs/` — каталог, `/clubs/<slug>/` — страница направления,
`/schedule/` — расписание, `/master-classes/`, `/teachers/`, `/pricing/`,
`/about/`, `/contacts/`, `/booking/`, `/login/`, `/register/`, `/account/`,
`/search/`. JSON: `/api/clubs/`, `/api/suggest/`.
