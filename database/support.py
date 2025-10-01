from optparse import Option
import aiosqlite
from typing import Optional, Any

from config import DATABASE_PATH


async def create_tables(conn: aiosqlite.Connection) -> None:
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            support_id INTEGER,
            message_text TEXT,
            is_answered BOOL DEFAULT FALSE,
            answered_by INTEGER,
            answer_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


async def get_ticket(ticket_id: int) -> Optional[tuple[Any, ...]]:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            SELECT id, user_id, is_answered, 
                   answered_by, message_text
            FROM support_tickets 
            WHERE id = ?
        """, (ticket_id, ))
        ticket = await cursor.fetchone()
        
        if ticket:
            keys = [description[0] for description in cursor.description]
            return dict(zip(keys,ticket))
        
        return False
    

async def create_ticket(user_id: int, message_text: str) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        cursor = await conn.execute("""
            INSERT INTO support_tickets (user_id, message_text)
            VALUES (?, ?)
        """, (user_id, message_text, ))
        
        return cursor.lastrowid
    

async def set_ticket_answered