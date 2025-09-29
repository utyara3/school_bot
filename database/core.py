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



