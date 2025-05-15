from models.messages import MessageOrm
from repos.base import BaseRepository
from repos.mappers.mappers import MessageDataMapper


class MessageRepository(BaseRepository):
    model = MessageOrm
    mapper = MessageDataMapper
