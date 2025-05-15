from sqlalchemy import select

from src.models.users import UserOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import UserDataMapper


class UserRepository(BaseRepository):
    model = UserOrm
    mapper = UserDataMapper

    async def get_uesr_with_hashedPwd(
        self,
        login: str,
        password: str,
    ):
        query = select(self.model).filter_by(login=login)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()
