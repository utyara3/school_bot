import aiosqlite
import asyncio

import sys
import os

# Абсолютные импорты
sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from config import DATABASE_PATH
from database import core as db

async def main():
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute('SELECT * FROM users')
        allies = await cursor.fetchall()
        print("users:", allies)
        cursor = await conn.execute('SELECT * FROM roles')
        allies = await cursor.fetchall()
        print("roles:", allies)
        cursor = await conn.execute('SELECT * FROM user_roles')
        allies = await cursor.fetchall()
        print("user_roles:", allies)



import aiosqlite

from config import DATABASE_PATH
from utils.bot_logging import get_logger
from database import users, schedule

logger = get_logger('database.core')


async def init_db() -> None:
    """Инициализация базы данных"""
    logger.info("Инициализация базы данных...")
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute('PRAGMA foreign_keys = ON')

        await schedule.create_tables(conn)
        await users.create_tables(conn)

        await schedule.insert_default_data(conn)
        await users.insert_default_data(conn)

        await conn.commit()


if __name__ == "__main__":
    asyncio.run(init_db())