from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

engine = create_async_engine(
    "postgresql+asyncpg://ecommerce_user:password@localhost:5432/ecommerce_db",
    echo=True,
)
async_sessionmaker_ = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
