import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()


class Config:
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    # DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"  # noqa E501
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@db:5432/{DB_NAME}"  # noqa E501


engine = create_async_engine(Config.DATABASE_URL, echo=True)
async_sessionmaker_ = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
