from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound

from database import Base
from repos.mappers.base import DataMapper
from src.utils.exceptions import ObjectNotFoundException


class BaseRepository:
    model = Base
    mapper: DataMapper = None

    def __init__(self, session) -> None:
        self.session = session

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def add(self, data: BaseModel):
        add_data_stmt = (
            insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        try:
            result = await self.session.execute(add_data_stmt)
        except IntegrityError:
            raise ObjectNotFoundException
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def edit(
        self,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by,
    ) -> None:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        try:
            result = await self.session.execute(update_stmt)
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)
        result = await self.session.execute(delete_stmt)
        return result
