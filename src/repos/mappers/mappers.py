from src.models.users import UserOrm
from src.repos.mappers.base import DataMapper
from src.schemas.users import User


class UserDataMapper(DataMapper):
    db_model = UserOrm
    schema = User
