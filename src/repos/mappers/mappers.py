from src.models.messages import MessageOrm
from src.models.users import UserOrm
from src.repos.mappers.base import DataMapper
from src.schemas.messages import Message
from src.schemas.users import User


class UserDataMapper(DataMapper):
    db_model = UserOrm
    schema = User


class MessageDataMapper(DataMapper):
    db_model = MessageOrm
    schema = Message
