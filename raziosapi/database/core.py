from typing import Iterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from raziosapi.config import DB_URL
from raziosapi.database.models import BaseModel


engine = create_async_engine(DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> Iterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session
                                                                   
async def create_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

async def drop_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
