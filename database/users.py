import aiosqlite

from config import DATABASE_PATH
from utils.bot_logging import get_logger

logger = get_logger('database.users')


async def create_tables(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            permission_level INTEGER DEFAULT 0      
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE         
        )
    """)


async def insert_default_data(conn):
    default_roles = (
        ('student', 'Ученик. Имеет доступ к базовому функционалу.', 1),
        ('support', 'Саппорт. Получает сообщения для поддержки.', 10),
        ('supervisor', 'Супервайзер. Может делать глобальные оповещения.', 100),
        ('admin', 'Админ. Полный доступ к управлению ботом.', 1000),
    )

    await conn.executemany('INSERT OR IGNORE INTO roles (name, description, permission_level) VALUES (?, ?, ?)', default_roles)

    await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(tg_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id)')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id)')


async def is_user_in_database(user_tg_id: int) -> bool:
    """Есть ли пользователь в базе данных"""
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn.execute(f'SELECT 1 FROM users WHERE tg_id=?', (user_tg_id, )) as cursor:
            return await cursor.fetchone() is not None
        

async def insert_user_to_database(tg_id: int, username: str = '', first_name: str = '', 
                                  last_name: str = '', roles: tuple[str] = ('student', )) -> None:
    """Добавить пользователя в базу данных"""
    logger.info(f"Добавление пользователя ({tg_id}) в базу данных")

    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute('INSERT OR IGNORE INTO users (tg_id, username, first_name, last_name) VALUES (?, ?, ?, ?)', 
                            (tg_id, username, first_name, last_name, ))
        
        cursor = await conn.execute('SELECT id FROM users WHERE tg_id = ?', (tg_id, ))

        user = await cursor.fetchone()

        if user:
            user_id = user[0]

            placeholders = ', '.join(['?'] * len(roles))
            cursor = await conn.execute(f'SELECT id FROM roles WHERE name IN ({placeholders})', roles)

            role_ids = [row[0] for row in await cursor.fetchall()] 

            if role_ids:
                role_data = [(user_id, role_id) for role_id in role_ids]
                await conn.executemany('INSERT OR IGNORE INTO user_roles(user_id, role_id) VALUES (?, ?)', role_data)

        await conn.commit()


async def get_users(limit: int, offset: int) -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT * FROM users LIMIT ? OFFSET ?
        """, (limit, offset, ))
        users = await cursor.fetchall()
        descriptions = [description[0] for description in cursor.description]

        return [dict(zip(descriptions, user)) for user in users]
    

async def get_user(tg_id: int) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id, ))
        user = await cursor.fetchone()
        descriptions = [description[0] for description in cursor.description]

        return dict(zip(descriptions, user))
    

async def get_user_roles(tg_id: int) -> list[str]:
    """Получить роль пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT r.name 
            FROM users u
            JOIN user_roles ur
                ON ur.user_id = u.id
            JOIN roles r
                ON ur.role_id = r.id
            WHERE u.tg_id = ?
        """, (tg_id, ))

        roles = await cursor.fetchall()

        return [role[0] for role in roles]
    

async def has_user_role(tg_id: int, role: str) -> bool:
    """Есть ли у пользователя роль"""
    return role in await get_user_roles(tg_id)
    

async def add_role_to_user(tg_id: int, role_name: str) -> None:
    """Дать пользователю роль"""
    logger.info(f"Добавление пользователю ({tg_id}) роли {role_name}")

    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id, ))
        user = await cursor.fetchone()

        cursor = await conn.execute("SELECT id FROM roles WHERE name = ?", (role_name, ))
        role = await cursor.fetchone()

        if user and role:
            user_id = user[0]
            role_id = role[0]

            await conn.execute("""INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)""", (user_id, role_id))

        await conn.commit()


async def remove_role_for_user(tg_id: int, role_name: str) -> None:
    """Лишить пользователя роли"""
    logger.info(f'Лишениие пользователя ({tg_id}) роли {role_name}')

    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            DELETE FROM user_roles
            WHERE user_id = (SELECT id FROM users WHERE tg_id = ?)
            AND role_id = (SELECT id FROM roles WHERE name = ?)
        """, (tg_id, role_name, ))

        await conn.commit()


async def get_users_by_role(role_name: str) -> list[int]:
    """Получить список айди пользователей по определенной роли"""
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT u.tg_id
            FROM users u
            JOIN user_roles ur
                ON u.id = ur.user_id
            JOIN roles r
                ON ur.role_id = r.id
            WHERE r.name = ?
        """, (role_name, ))

        users = await cursor.fetchall()

        return [user[0] for user in users]
    

async def get_full_database_info() -> dict:
    """Получить статистику базы данных"""
    logger.info("Получение статистики базы данных.")

    ret_info = {}
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        #cursor = await conn.execute("""
        #    SELECT u.tg_id, u.first_name, r.name as roles
        #    FROM users u
        #    JOIN user_roles ur
        #        ON ur.user_id = u.id
        #    JOIN roles r
        #        ON r.id = ur.role_id           
        #""")
        #columns = [description[0] for description in cursor.description]
        #ret_info['all_users'] = [dict(zip(columns, user)) for user in users]

        cursor = await conn.execute("""SELECT COUNT(id) FROM users""")
        users = await cursor.fetchall()


    return ret_info


async def get_number_of_users() -> int:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""SELECT COUNT(id) FROM users""")
        users = await cursor.fetchone()

        return int(users[0]) 
    

async def get_all_roles() -> list[str]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""SELECT name FROM roles""")
        roles = await cursor.fetchall()

        return [role[0] for role in roles]
