import aiosqlite

#from config import DATABASE_PATH


async def create_tables(conn: aiosqlite.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            short_name TEXT UNIQUE NOT NULL
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS weekdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            short_name TEXT UNIQUE NOT NULL,
            order_index INTEGER NOT NULL UNIQUE
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schedule_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weekday_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            lesson_number INTEGER NOT NULL,
            UNIQUE(weekday_id, class_id, lesson_number),
            FOREIGN KEY (weekday_id) REFERENCES weekdays(id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE       
        )
    """)


async def insert_default_data(conn: aiosqlite.Connection) -> None:
    weekdays = [
        ("Понедельник", "пн", 1),
        ("Вторник", "вт", 2),
        ("Среда", "ср", 3),
        ("Четверг", "чт", 4),
        ("Пятница", "пт", 5),
        ("Суббота", "сб", 6),
        ("Воскресенье", "вс", 7)
    ]
    
    class_nums = list(range(5, 11+1))
    class_letters = ["А", "Б", "В", "Г", "Д", "Е"]

    classes = [(str(class_num)+class_letter.upper(), )
              for class_num in class_nums
              for class_letter in class_letters]

    subjects = [
        ("Биология", "био", ),
        ("Вероятность и статистика", "стат", ),
        ("География", "геог", ),
        ("Избранные вопросы математики", "мат. эл.", ),
        ("Английский язык", "англ", ),
        ("Информатика", "инф", ),
        ("История", "ист", ),
        ("Литература", "лит", ),
        ("Обществознание", "общ", ),
        ("Практикум решения задач по информатике", "инф. эл.", ),
        ("Русский язык", "рус", ),
        ("Физика", "физ", ),
        ("Химия", "хим", ),
        ("Алгебра", "алг", ),
        ("Геометрия", "геом", ),
        ("Основы безопасности и защиты Родины", "обзр", ),
        ("Физическая культура", "физра", ),
        ("Математика", "мат", ),
        ("--Нет урока--", "нет", )
    ]

    await conn.executemany("""
        INSERT OR IGNORE INTO weekdays(name, short_name, order_index)
            VALUES (?, ?, ?)
    """, weekdays)

    await conn.executemany("""
        INSERT OR IGNORE INTO classes(name) VALUES (?)
    """, classes)
    
    await conn.executemany("""
        INSERT OR IGNORE INTO subjects(name, short_name) VALUES (?, ?)
    """, subjects)

    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_schedule_lesson 
            ON schedule_entries(class_id, weekday_id)
    """)
    
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_schedule_class_weekday
            ON schedule_entries(lesson_number)
    """)
