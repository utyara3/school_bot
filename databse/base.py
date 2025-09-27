from sqlite3 import DatabaseError
import aiosqlite

from config import DATABASE_PATH


async def init_db() -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn:
            await conn.execute('PRAGMA foreign_keys = ON')

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
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn.execute(f'SELECT 1 FROM users WHERE tg_id=?', (user_tg_id, )) as cursor:
            return await cursor.fetchone() is not None
        

async def insert_user_to_database(tg_id: int, username: str = '', first_name: str = '', 
                                  last_name: str = '', roles: tuple[str] = ('student', )) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn:
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


async def get_user_roles(tg_id: int) -> list[str]:
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
    return role in await get_user_roles(tg_id)
    

async def add_role_to_user(tg_id: int, role_name: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn:
            cursor = await conn.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id, ))
            user = await cursor.fetchone()

            cursor = await conn.execute("SELECT id FROM roles WHERE name = ?", (role_name, ))
            role = await cursor.fetchone()

            if user and role:
                user_id = user[0]
                role_id = role[0]

                await conn.execute("""INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)""", (user_id, role_id))


async def remove_role_for_user(tg_id: int, role_name: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn:
            await conn.execute("""
                DELETE FROM user_roles
                WHERE user_id = (SELECT id FROM users WHERE tg_id = ?)
                AND role_id = (SELECT id FROM roles WHERE name = ?)
            """, (tg_id, role_name, ))


async def get_users_by_role(role_name: str) -> list[int]:
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
