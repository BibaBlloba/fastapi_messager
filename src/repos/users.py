from models.users import UserOrm
from repos.base import BaseRepository
from repos.mappers.mappers import UserDataMapper


class UserRepository(BaseRepository):
    model = UserOrm
    mapper = UserDataMapper
