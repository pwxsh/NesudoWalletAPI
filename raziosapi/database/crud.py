from typing import Type

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from raziosapi.database.models import BaseModel


class CRUD:
    def __init__(self, model: Type[BaseModel], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> Type[BaseModel]:
        model = self.model(**kwargs)
        self.session.add(model)
        await self.session.commit()
        return model

    async def is_exist(self, **kwargs) -> bool:
        stmt = select(self.model).filter_by(**kwargs)
        result = (await self.session.scalar(stmt)).unique()
        return result is not None

    async def get(self, **kwargs) -> Type[BaseModel]:
        stmt = select(self.model).filter_by(**kwargs)
        result = (await self.session.scalar(stmt)).unique()
        return result

    async def order_by(
        self,
        column,
        limit: int,
        use_desc: bool = True
    ) -> list[Type[BaseModel]]:
        stmt = (
            select(self.model)
            .order_by(desc(column) if use_desc else column)
            .limit(limit)
        )
        results = await(self.session.scalars()).unique()
        return results

    async def update(self, model: Type[BaseModel]) -> Type[BaseModel]:
        self.session.add(model)
        await self.session.commit()
        return await self.get(id=model.id)

    async def delete(self, model: Type[BaseModel]) -> None:
        self.session.delete(model)
        await self.session.commit()
