"""Демонстрационные данные центра «Умный ребёнок» (python manage.py seed_demo)."""

from datetime import date, time, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from kids.models import (
    Attendance,
    BookingRequest,
    Child,
    Club,
    ContactRequest,
    Group,
    MasterClass,
    NewsletterSubscriber,
    Payment,
    PricePlan,
    Profile,
    Review,
    Room,
    Schedule,
    Subscription,
    Teacher,
)

TODAY = date.today()


CLUBS = [
    {
        "name": "Робототехника",
        "slug": "robototehnika",
        "direction": "tech",
        "age_min": 6,
        "age_max": 11,
        "tagline": "Конструкторы, моторы и первые программы. Готовим команды к городским соревнованиям.",
        "description": "Первый год — механика: ребята собирают модели на конструкторе, разбираются в передачах, рычагах и устойчивости. Второй год — датчики и программирование: модель начинает реагировать на препятствие, свет и звук. Третий — собственный проект и подготовка к соревнованиям.\n\nМы не делим детей по «способностям»: группа идёт по программе, а педагог подбирает уровень задачи каждому.",
        "skills": "Читать простые схемы и собирать механизм по инструкции\nПонимать, как работают мотор, редуктор и датчик расстояния\nПисать первую программу из блоков и проверять её на модели\nДоводить проект до работающего результата\nПрезентовать свою работу перед группой",
        "format_text": "10 минут — разминка и разбор прошлой недели. 15 минут — новая тема и демонстрация. 25 минут — сборка и эксперимент. 10 минут — испытание модели и короткий итог. В конце каждого месяца — открытое занятие для родителей.",
        "price": 2600,
        "lessons_per_week": 2,
        "cover": "robo",
        "order": 1,
    },
    {
        "name": "Рисование и живопись",
        "slug": "risovanie",
        "direction": "art",
        "age_min": 4,
        "age_max": 12,
        "tagline": "Гуашь, акварель, пастель и коллаж. Каждое занятие — законченная работа.",
        "description": "Начинаем с пятна и линии, постепенно переходим к композиции, цвету и натуре. Работаем гуашью, акварелью, пастелью и в смешанной технике. Каждые два месяца — небольшая выставка в холле центра.\n\nМатериалы и фартуки входят в стоимость, домой ребёнок забирает готовые работы.",
        "skills": "Смешивать цвета и подбирать оттенки\nСтроить композицию листа\nРисовать с натуры и по представлению\nРаботать в разных техниках\nДоводить работу до конца и оформлять её",
        "format_text": "5 минут — разогрев и рассматривание референсов. 15 минут — показ техники. 35 минут — самостоятельная работа с поддержкой педагога. 5 минут — мини-выставка и обсуждение.",
        "price": 2400,
        "lessons_per_week": 2,
        "cover": "art",
        "order": 2,
    },
    {
        "name": "Английский язык",
        "slug": "angliyskiy",
        "direction": "lang",
        "age_min": 5,
        "age_max": 12,
        "tagline": "Разговорные группы по уровням: игры, диалоги и мини-спектакли.",
        "description": "Занятия строятся вокруг речи: короткие диалоги, игры, песни и мини-постановки. Группы делятся по уровню, а не только по возрасту, поэтому ребёнок попадает туда, где ему комфортно.\n\nДомашние задания небольшие: 10–15 минут на закрепление слов и фраз.",
        "skills": "Понимать простую речь на слух\nПоддерживать короткий диалог\nЧитать адаптированные тексты\nПисать короткие сообщения\nНе бояться говорить с ошибками",
        "format_text": "5 минут — warm-up на английском. 15 минут — новая лексика и конструкции. 20 минут — парная и групповая практика. 15 минут — игра или мини-сценка. 5 минут — итог и домашнее задание.",
        "price": 2800,
        "lessons_per_week": 2,
        "cover": "en",
        "order": 3,
    },
    {
        "name": "Подготовка к школе",
        "slug": "podgotovka-k-shkole",
        "direction": "dev",
        "age_min": 5,
        "age_max": 7,
        "tagline": "Чтение, счёт, письмо и внимание. Мягкая адаптация к первому классу.",
        "description": "Готовим не к конкретной школе, а к формату занятий: слушать, поднимать руку, работать в тетради, доводить задание до конца. Отдельно занимаемся чтением и счётом, развиваем мелкую моторику.\n\nРаз в месяц — открытое занятие, где родители видят прогресс и получают рекомендации.",
        "skills": "Читать слоги и простые слова\nСчитать в пределах 20 и решать простые задачи\nДержать ручку и писать элементы букв\nСлышать инструкцию и удерживать внимание 20–25 минут\nРаботать в группе и договариваться",
        "format_text": "Занятие идёт 60 минут и делится на три блока по 15–20 минут: чтение, математика, письмо и моторика. Между блоками — короткая подвижная пауза.",
        "price": 2200,
        "lessons_per_week": 2,
        "cover": "school",
        "order": 4,
    },
    {
        "name": "Научная лаборатория",
        "slug": "nauchnaya-laboratoriya",
        "direction": "tech",
        "age_min": 7,
        "age_max": 11,
        "tagline": "Опыты по физике и химии, микроскопы и собственные проекты.",
        "description": "Каждое занятие — вопрос и опыт: почему лёд скользит, как работает вулкан, что видно в микроскоп. Все опыты безопасные и повторяемые, материалы выдаём на месте.\n\nРаз в месяц ребята готовят мини-проект и защищают его перед группой.",
        "skills": "Формулировать гипотезу и проверять её\nПользоваться микроскопом и лабораторной посудой\nЗаписывать результаты опыта\nОбъяснять явление простыми словами\nСоблюдать технику безопасности",
        "format_text": "10 минут — вопрос занятия и гипотезы. 25 минут — опыт и наблюдения. 10 минут — обсуждение результатов. 10 минут — запись выводов и мини-проект.",
        "price": 2900,
        "lessons_per_week": 1,
        "cover": "science",
        "order": 5,
    },
    {
        "name": "Театральная студия",
        "slug": "teatralnaya-studiya",
        "direction": "art",
        "age_min": 6,
        "age_max": 14,
        "tagline": "Сценическая речь, пластика и две постановки за учебный год.",
        "description": "Начинаем с упражнений на внимание и раскрепощение, затем — сценическая речь, пластика и работа с текстом. За учебный год выпускаем две постановки: зимнюю и весеннюю.\n\nСпектакли показываем на сцене актового зала, вход для родителей свободный.",
        "skills": "Говорить чётко и слышно\nУправлять голосом и дыханием\nДержаться на сцене и не бояться зрителя\nРаботать в паре и в команде\nУчить текст и выходить на премьеру",
        "format_text": "10 минут — разминка тела и голоса. 20 минут — упражнения на внимание и взаимодействие. 25 минут — работа над сценой и текстом. 5 минут — обсуждение и планы.",
        "price": 2500,
        "lessons_per_week": 2,
        "cover": "theatre",
        "order": 6,
    },
]


TEACHERS = [
    ("Анна Ковалёва", "Робототехника", "Инженер-программист, тренер команд городских соревнований. Ведёт группы 6–11 лет с 2019 года.", 7, "accent"),
    ("Марина Соловьёва", "Рисование и живопись", "Художник-педагог, выпускница художественного училища. Работает с детьми от 4 лет.", 12, "sage"),
    ("Ирина Петрова", "Английский язык", "Лингвист, сертификат CELTA. Строит занятия вокруг разговорной практики и игр.", 9, "plain"),
    ("Дмитрий Ершов", "Шахматы", "Мастер FIDE, судья городских турниров. Учит думать на несколько ходов вперёд.", 11, "sage"),
    ("Ольга Титова", "Подготовка к школе", "Учитель начальных классов, логопед-дефектолог. 14 лет работы с дошкольниками.", 14, "accent"),
    ("Сергей Волков", "Научная лаборатория", "Химик, популяризатор науки. Проводит опыты, которые безопасно повторить дома.", 8, "plain"),
    ("Елена Морозова", "Театральная студия", "Актриса драматического театра, педагог по сценической речи.", 10, "accent"),
    ("Павел Крылов", "Шахматы", "Кандидат в мастера спорта, ведёт шахматный клуб центра с 2021 года.", 6, "plain"),
    ("Наталья Громова", "Рисование и живопись", "Преподаёт академический рисунок и скетчинг, куратор выставок детских работ.", 15, "sage"),
    ("Артём Белов", "Робототехника", "Инженер-механик, собирает с детьми модели и готовит их к соревнованиям.", 5, "plain"),
    ("Юлия Смирнова", "Английский язык", "Преподаватель с опытом работы в языковой школе, специализация — дошкольники.", 4, "accent"),
    ("Игорь Данилов", "Научная лаборатория", "Физик, автор программы «Наука вокруг нас» для младших школьников.", 7, "sage"),
]


GROUPS = {
    "robototehnika": [
        ("Робо-1 · начинающие", 6, 8, 10, ["Анна Ковалёва", "Артём Белов"]),
        ("Робо-2 · продолжающие", 8, 11, 10, ["Анна Ковалёва"]),
        ("Робо-3 · соревнования", 9, 11, 8, ["Анна Ковалёва", "Артём Белов"]),
        ("Робо-мини · 6–7 лет", 6, 7, 8, ["Артём Белов"]),
    ],
    "risovanie": [
        ("Акварель", 4, 6, 8, ["Марина Соловьёва"]),
        ("Палитра", 7, 9, 8, ["Марина Соловьёва"]),
        ("Мастерская", 10, 12, 8, ["Наталья Громова"]),
        ("Скетч", 6, 9, 8, ["Наталья Громова"]),
    ],
    "angliyskiy": [
        ("English Start", 5, 6, 8, ["Ирина Петрова", "Юлия Смирнова"]),
        ("English 1", 7, 9, 8, ["Ирина Петрова"]),
        ("English 2", 9, 12, 8, ["Ирина Петрова"]),
        ("Speaking Club", 10, 12, 6, ["Юлия Смирнова"]),
    ],
    "podgotovka-k-shkole": [
        ("Подготовка 1", 5, 6, 12, ["Ольга Титова"]),
        ("Подготовка 2", 6, 7, 12, ["Ольга Титова"]),
        ("Чтение", 5, 7, 10, ["Ольга Титова"]),
        ("Логика", 6, 7, 10, ["Ольга Титова"]),
    ],
    "nauchnaya-laboratoriya": [
        ("Лаборатория 1", 7, 9, 10, ["Сергей Волков"]),
        ("Лаборатория 2", 9, 11, 10, ["Игорь Данилов"]),
        ("Микроскоп", 8, 10, 10, ["Сергей Волков", "Игорь Данилов"]),
        ("Проекты", 10, 11, 8, ["Игорь Данилов"]),
    ],
    "teatralnaya-studiya": [
        ("Сцена 1", 6, 8, 12, ["Елена Морозова"]),
        ("Сцена 2", 8, 11, 12, ["Елена Морозова"]),
        ("Пластика", 7, 10, 10, ["Елена Морозова"]),
        ("Читка", 11, 14, 10, ["Елена Морозова"]),
    ],
}

ROOMS = [
    ("105", 12),
    ("108", 10),
    ("204", 12),
    ("207", 16),
    ("301", 10),
    ("Лаборатория", 10),
    ("Актовый зал", 40),
]

ROOM_BY_CLUB = {
    "robototehnika": "204",
    "risovanie": "108",
    "angliyskiy": "301",
    "podgotovka-k-shkole": "105",
    "nauchnaya-laboratoriya": "Лаборатория",
    "teatralnaya-studiya": "Актовый зал",
}

LEAD_BY_COVER = {
    "robo": "Анна Ковалёва",
    "art": "Марина Соловьёва",
    "en": "Ирина Петрова",
    "school": "Ольга Титова",
    "science": "Сергей Волков",
    "theatre": "Елена Морозова",
}

PLANS = [
    {
        "name": "Разовое занятие",
        "price": 700,
        "lessons": 1,
        "description": "Если хочется попробовать формат без обязательств.",
        "features": "Одно занятие в любой группе\nВсе материалы включены\nДействует 14 дней с покупки\nНе переносится на другого ребёнка",
        "is_featured": False,
        "order": 1,
    },
    {
        "name": "Абонемент «4 занятия»",
        "price": 2600,
        "lessons": 4,
        "description": "Одно направление, одна группа, занятия 2 раза в неделю.",
        "features": "4 занятия по 60 минут\n650 ₽ за занятие вместо 700 ₽\nПропуск по справке переносится\nОткрытые занятия для родителей\nДействует 30 дней с первого занятия",
        "is_featured": True,
        "order": 2,
    },
    {
        "name": "Абонемент «8 занятий»",
        "price": 4800,
        "lessons": 8,
        "description": "Для тех, кто ходит регулярно и не хочет думать об оплате каждый месяц.",
        "features": "8 занятий по 60 минут\n600 ₽ за занятие\nЗаморозка до 14 дней\nСкидка 10% на мастер-классы\nДействует 60 дней с первого занятия",
        "is_featured": False,
        "order": 3,
    },
]

REVIEWS = [
    ("Дмитрий", "Артём, 9 лет", "Робототехника", 24, "За два года сменили три кружка, а здесь остались. Нравится, что администратор сама напоминает про перенос и не приходится выбивать информацию.", 1),
    ("Наталья", "Полина, 6 лет", "Рисование и английский", 12, "Дочка ходит на рисование и английский подряд, в один день. Удобно, что можно оставить её на два занятия и забрать через три часа.", 2),
    ("Мария", "Миша, 7 лет", "Робототехника", 8, "Сын впервые довёл проект до конца и сам показал его группе. Для нас это важнее оценок.", 3),
    ("Ольга", "Соня, 5 лет", "Рисование и живопись", 6, "На занятиях не сравнивают работы детей между собой. Дочь перестала бояться «испортить лист» и рисует дома каждый день.", 4),
]

MASTER_CLASSES = [
    ("Робот-жук из картона", "robot-zhuk", 2, time(12, 0), time(13, 30), 7, 10, 900, 12, 9, "robo",
     "Собираем вибробота из мотора, батарейки и картона. Гоняем по трассе и забираем домой.",
     "Знакомство с вибромотором, сборка корпуса, испытание модели на трассе."),
    ("Осенний скетч гуашью", "osenniy-sketch", 2, time(15, 0), time(16, 30), 5, 9, 800, 12, 5, "art",
     "Тёплые оттенки, листья с натуры и оформление работы в паспарту.",
     "Смешивание тёплых оттенков, быстрый рисунок с натуры, оформление работы."),
    ("Научное шоу «Слизь»", "nauchnoe-shou-sliz", 3, time(11, 0), time(12, 0), 6, 10, 700, 16, 11, "science",
     "Полимеры и реакции: делаем неньютоновскую жидкость и объясняем, почему она так себя ведёт.",
     "Опыты с полимерами, неньютоновская жидкость, обсуждение свойств веществ."),
    ("Кукольный театр", "kukolnyy-teatr", 9, time(12, 0), time(14, 0), 6, 9, 1100, 12, 4, "theatre",
     "Придумываем персонажа, клеим куклу и играем короткую сцену на ширме.",
     "Создание куклы, работа с голосом, короткая сцена на ширме."),
    ("Пряники и геометрия", "pryaniki-i-geometriya", 16, time(11, 0), time(12, 30), 4, 7, 850, 14, 8, "school",
     "Расписываем пряники и заодно разбираемся в симметрии и узорах.",
     "Симметрия, узоры, роспись пряников и мини-выставка."),
    ("Christmas Workshop", "christmas-workshop", 23, time(13, 0), time(15, 0), 7, 11, 1200, 12, 6, "en",
     "Мини-спектакль на английском: учим роли, репетируем и показываем родителям.",
     "Роли на английском, репетиция, показ мини-спектакля родителям."),
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные центра «Умный ребёнок»"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Очищаю демонстрационные данные…")
        Attendance.objects.all().delete()
        Payment.objects.all().delete()
        Subscription.objects.all().delete()
        Child.objects.all().delete()
        Schedule.objects.all().delete()
        Group.objects.all().delete()
        MasterClass.objects.all().delete()
        Review.objects.all().delete()
        PricePlan.objects.all().delete()
        BookingRequest.objects.all().delete()
        ContactRequest.objects.all().delete()
        NewsletterSubscriber.objects.all().delete()
        Club.objects.all().delete()
        Teacher.objects.all().delete()
        Room.objects.all().delete()

        rooms = {number: Room.objects.create(number=number, capacity=capacity) for number, capacity in ROOMS}

        teachers = {}
        for order, (name, spec, bio, experience, tone) in enumerate(TEACHERS, start=1):
            teachers[name] = Teacher.objects.create(
                full_name=name,
                specialization=spec,
                bio=bio,
                experience_years=experience,
                tone=tone,
                order=order,
            )

        clubs = {}
        groups = []
        for data in CLUBS:
            club = Club.objects.create(**data)
            clubs[data["slug"]] = club
            for title, min_age, max_age, capacity, teacher_names in GROUPS[data["slug"]]:
                group = Group.objects.create(
                    club=club,
                    title=title,
                    room=rooms[ROOM_BY_CLUB[data["slug"]]],
                    min_age=min_age,
                    max_age=max_age,
                    capacity=capacity,
                )
                group.teachers.set([teachers[name] for name in teacher_names])
                groups.append(group)

        day_pairs = [(1, 3), (2, 4), (1, 4), (2, 5), (3, 5), (5, 6)]
        start_times = [
            time(9, 30),
            time(10, 30),
            time(11, 30),
            time(15, 30),
            time(16, 30),
            time(17, 30),
            time(18, 30),
        ]
        for index, group in enumerate(groups):
            days = day_pairs[index % len(day_pairs)]
            for shift, day in enumerate(days):
                start = start_times[(index + shift * 3) % len(start_times)]
                Schedule.objects.create(
                    group=group,
                    room=group.room,
                    day_of_week=day,
                    start_time=start,
                    end_time=time(start.hour + 1, start.minute),
                )

        for title, slug, days_ahead, start, end, age_min, age_max, price, seats, taken, cover, summary, program in MASTER_CLASSES:
            MasterClass.objects.create(
                title=title,
                slug=slug,
                date=TODAY + timedelta(days=days_ahead),
                start_time=start,
                end_time=end,
                age_min=age_min,
                age_max=age_max,
                price=price,
                seats=seats,
                seats_taken=taken,
                teacher=teachers[LEAD_BY_COVER[cover]],
                room=rooms["204"],
                cover=cover,
                summary=summary,
                program=program,
            )

        for data in PLANS:
            PricePlan.objects.create(**data)

        for author, child, club, months, text, order in REVIEWS:
            Review.objects.create(author=author, child=child, club=club, months=months, text=text, order=order)

        # Демо-родитель
        parent, created = User.objects.get_or_create(
            username="parent@example.com",
            defaults={"email": "parent@example.com", "first_name": "Мария", "last_name": "Хасанзянова"},
        )
        parent.email = "parent@example.com"
        parent.first_name = "Мария"
        parent.last_name = "Хасанзянова"
        parent.set_password("demo12345")
        parent.save()
        Profile.objects.update_or_create(user=parent, defaults={"phone": "+7 900 000-00-00"})

        # Администратор
        admin_user, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("admin12345")
        admin_user.save()

        misha = Child.objects.create(parent=parent, full_name="Миша Хасанзянов", birth_date=TODAY - timedelta(days=365 * 7 + 40))
        sonya = Child.objects.create(parent=parent, full_name="Соня Хасанзянова", birth_date=TODAY - timedelta(days=365 * 5 + 120))

        robo_group = groups[0]
        art_group = groups[4]
        theatre_group = groups[22]

        robo_sub = Subscription.objects.create(
            child=misha,
            group=robo_group,
            start_date=TODAY - timedelta(days=20),
            end_date=TODAY + timedelta(days=40),
            total_classes=8,
            remaining_classes=5,
            status="active",
        )
        art_sub = Subscription.objects.create(
            child=sonya,
            group=art_group,
            start_date=TODAY - timedelta(days=25),
            end_date=TODAY + timedelta(days=5),
            total_classes=4,
            remaining_classes=1,
            status="active",
        )
        Subscription.objects.create(
            child=misha,
            group=theatre_group,
            start_date=TODAY - timedelta(days=120),
            end_date=TODAY - timedelta(days=30),
            total_classes=4,
            remaining_classes=0,
            status="expired",
        )

        robo_lessons = list(robo_sub.group.schedules.all()[:2])
        art_lessons = list(art_sub.group.schedules.all()[:2])
        for offset, lesson in enumerate(robo_lessons + art_lessons, start=1):
            child = misha if lesson in robo_lessons else sonya
            Attendance.objects.create(
                schedule=lesson,
                child=child,
                date=TODAY - timedelta(days=7 * offset),
                status="present" if offset != 3 else "absent",
            )

        Payment.objects.create(
            child=misha, date=TODAY - timedelta(days=20), amount=4800,
            purpose="Абонемент «8 занятий» · Робототехника", status="paid",
        )
        Payment.objects.create(
            child=sonya, date=TODAY - timedelta(days=25), amount=2600,
            purpose="Абонемент «4 занятия» · Рисование", status="paid",
        )
        Payment.objects.create(
            child=misha, date=TODAY + timedelta(days=3), amount=4800,
            purpose="Продление абонемента · Робототехника", status="waiting",
        )

        BookingRequest.objects.create(
            parent_name="Екатерина Лисова", phone="+7 902 111-22-33", email="lisova@example.com",
            child_name="Тимур", child_age=7, club=clubs["robototehnika"],
            preferred_day="sat", preferred_time="morning",
            comment="Хотим на пробное в субботу, ребёнок занимался Lego дома.",
            consent=True,
        )
        BookingRequest.objects.create(
            parent_name="Алексей Фомин", phone="+7 927 444-55-66", email="fomin@example.com",
            child_name="Вера", child_age=5, club=clubs["risovanie"],
            preferred_day="weekday", preferred_time="evening",
            comment="Интересует рисование, удобно после садика.",
            consent=True, is_processed=True,
        )

        ContactRequest.objects.create(
            name="Светлана", phone="+7 902 777-88-99", topic="payment",
            message="Подскажите, можно ли оплатить абонемент двумя платежами?", consent=True,
        )
        ContactRequest.objects.create(
            name="Ирина", phone="+7 908 123-45-67", topic="booking",
            message="Ребёнку 6 лет, хотим на робототехнику в субботу утром.", consent=True,
        )

        NewsletterSubscriber.objects.create(email="parent@example.com")
        NewsletterSubscriber.objects.create(email="news@example.com")

        self.stdout.write(self.style.SUCCESS(
            "Готово: %d направлений, %d группы, %d педагогов, %d мастер-класса."
            % (Club.objects.count(), Group.objects.count(), Teacher.objects.count(), MasterClass.objects.count())
        ))
