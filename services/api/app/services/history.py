import aiosqlite
import json
import uuid
import time
from typing import List, Dict, Any, Optional

DB_PATH = "inferenceos.db"

_db_initialized = False

async def ensure_db():
    global _db_initialized
    if not _db_initialized:
        await init_db()
        _db_initialized = True

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                model TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                provider TEXT,
                latency_ms REAL,
                created_at REAL NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        await db.commit()

async def create_conversation(title: str, model: str) -> Dict[str, Any]:
    await ensure_db()
    conv_id = str(uuid.uuid4())
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at, model) VALUES (?, ?, ?, ?, ?)",
            (conv_id, title, now, now, model)
        )
        await db.commit()
    return {"id": conv_id, "title": title, "created_at": now, "updated_at": now, "model": model}

async def list_conversations() -> List[Dict[str, Any]]:
    await ensure_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM conversations ORDER BY updated_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    await ensure_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            conv = dict(row)
        
        async with db.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conv_id,)) as cursor:
            msg_rows = await cursor.fetchall()
            conv["messages"] = [dict(m) for m in msg_rows]
            return conv

async def delete_conversation(conv_id: str) -> bool:
    await ensure_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        await db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        await db.commit()
    return True

async def add_message(
    conversation_id: str,
    role: str,
    content: str,
    model: str = "",
    provider: str = "",
    latency_ms: float = 0.0
) -> Dict[str, Any]:
    await ensure_db()
    msg_id = str(uuid.uuid4())
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO messages (id, conversation_id, role, content, model, provider, latency_ms, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (msg_id, conversation_id, role, content, model, provider, latency_ms, now)
        )
        await db.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id)
        )
        await db.commit()
    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "model": model,
        "provider": provider,
        "latency_ms": latency_ms,
        "created_at": now
    }
