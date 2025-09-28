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
from database import base as db

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



async def main1():
    print(await db.get_number_of_users())


if __name__ == "__main__":
    asyncio.run(main1())