from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_sessionmaker_


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker_ as session:
        yield session
