from src.models.messages import MessageOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import MessageDataMapper


class MessageRepository(BaseRepository):
    model = MessageOrm
    mapper = MessageDataMapper
