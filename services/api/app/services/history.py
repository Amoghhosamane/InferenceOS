import time
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete, desc
from app.services.db import AsyncSessionLocal, ConversationModel, MessageModel, init_db

_db_initialized = False

async def ensure_db():
    global _db_initialized
    if not _db_initialized:
        await init_db()
        _db_initialized = True

async def create_conversation(title: str, model: str) -> Dict[str, Any]:
    await ensure_db()
    conv_id = str(uuid.uuid4())
    now = time.time()
    async with AsyncSessionLocal() as session:
        conv = ConversationModel(
            id=conv_id,
            title=title,
            model=model,
            created_at=now,
            updated_at=now,
        )
        session.add(conv)
        await session.commit()
    return {"id": conv_id, "title": title, "created_at": now, "updated_at": now, "model": model}

async def list_conversations() -> List[Dict[str, Any]]:
    await ensure_db()
    async with AsyncSessionLocal() as session:
        stmt = select(ConversationModel).order_by(desc(ConversationModel.updated_at))
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "id": c.id,
                "title": c.title,
                "model": c.model,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in rows
        ]

async def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    await ensure_db()
    async with AsyncSessionLocal() as session:
        stmt = select(ConversationModel).where(ConversationModel.id == conv_id)
        result = await session.execute(stmt)
        conv = result.scalar_one_or_none()
        if not conv:
            return None

        # Fetch ordered messages
        msg_stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conv_id)
            .order_by(MessageModel.created_at.asc())
        )
        msg_result = await session.execute(msg_stmt)
        messages = msg_result.scalars().all()

        return {
            "id": conv.id,
            "title": conv.title,
            "model": conv.model,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "messages": [
                {
                    "id": m.id,
                    "conversation_id": m.conversation_id,
                    "role": m.role,
                    "content": m.content,
                    "model": m.model,
                    "provider": m.provider,
                    "latency_ms": m.latency_ms,
                    "created_at": m.created_at,
                }
                for m in messages
            ],
        }

async def delete_conversation(conv_id: str) -> bool:
    await ensure_db()
    async with AsyncSessionLocal() as session:
        stmt = delete(ConversationModel).where(ConversationModel.id == conv_id)
        await session.execute(stmt)
        await session.commit()
    return True

async def add_message(
    conversation_id: str,
    role: str,
    content: str,
    model: str = "",
    provider: str = "",
    latency_ms: float = 0.0,
) -> Dict[str, Any]:
    await ensure_db()
    msg_id = str(uuid.uuid4())
    now = time.time()
    async with AsyncSessionLocal() as session:
        # Create message record
        msg = MessageModel(
            id=msg_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            provider=provider,
            latency_ms=latency_ms,
            created_at=now,
        )
        session.add(msg)

        # Update parent conversation timestamp
        conv_stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conv_res = await session.execute(conv_stmt)
        conv = conv_res.scalar_one_or_none()
        if conv:
            conv.updated_at = now

        await session.commit()

    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "model": model,
        "provider": provider,
        "latency_ms": latency_ms,
        "created_at": now,
    }
