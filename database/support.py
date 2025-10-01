import aiosqlite
from typing import Optional, Any

from config import DATABASE_PATH
from utils.bot_logging import get_logger

logger = get_logger('database.support')


async def create_tables(conn: aiosqlite.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            support_id INTEGER,
            message_text TEXT,
            status TEXT DEFAULT 'pending',
            answer_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


async def create_ticket(user_id: int, message_text: str) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            INSERT INTO support_tickets (user_id, status, message_text)
            VALUES (?, ?, ?)
        """, (user_id, 'pending', message_text, ))

        await conn.commit()

        num = cursor.lastrowid

        logger.info(f"Обращение №{num} в поддержку пользователем ({user_id})")
        
        return num


async def get_ticket(ticket_id: int) -> dict | bool:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, user_id, status, 
                   support_id, message_text
            FROM support_tickets 
            WHERE id = ?
        """, (ticket_id, ))
        ticket = await cursor.fetchone()
        
        if ticket:
            keys = [description[0] for description in cursor.description]
            return dict(zip(keys,ticket))
        
        return False


async def set_ticket_status_pending(ticket_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            UPDATE support_tickets
            SET support_id = ?, status = ?
            WHERE id = ?
        """, (None, "pending", ticket_id))

        await conn.commit()


async def set_ticket_status_in_progress(ticket_id: int, support_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            UPDATE support_tickets
            SET support_id = ?, status = ?
            WHERE id = ?
        """, (support_id, "in_progress", ticket_id))

        await conn.commit()


async def set_ticket_status_resolved(ticket_id: int, answer_text: str) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        await conn.execute("""
            UPDATE support_tickets
            SET status = ?, answer_text = ?
            WHERE id = ?
        """, ("resolved", answer_text, ticket_id))

        logger.info(f"Обращение №{ticket_id} было решено.")

        await conn.commit()