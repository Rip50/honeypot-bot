import aiosqlite
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="messages.db"):
        self.db_path = db_path

    async def init_db(self):
        """Initialize the database and create necessary tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    role TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
            """)
            await db.commit()

    async def add_message(self, user_id: int, message: str, role: str):
        """Add a new message to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (user_id, message, role, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, message, role, datetime.now())
            )
            await db.commit()

    async def get_recent_messages(self, user_id: int, limit: int = 10) -> list:
        """Get recent messages for a specific user."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT message, role FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            ) as cursor:
                messages = await cursor.fetchall()
                return [{"role": role, "content": message} for message, role in reversed(messages)]

    async def cleanup_old_messages(self, days: int = 7):
        """Remove messages older than specified days."""
        async with aiosqlite.connect(self.db_path) as db:
            cutoff = datetime.now() - timedelta(days=days)
            await db.execute(
                "DELETE FROM messages WHERE timestamp < ?",
                (cutoff,)
            )
            await db.commit() 