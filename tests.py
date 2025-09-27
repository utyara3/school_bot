import aiosqlite
import asyncio

from config import DATABASE_PATH

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

asyncio.run(main())