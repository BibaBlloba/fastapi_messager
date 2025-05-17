from sqlalchemy import and_, func, or_, select

from src.models.messages import MessageOrm
from src.repos.base import BaseRepository
from src.repos.mappers.mappers import MessageDataMapper


class MessageRepository(BaseRepository):
    model = MessageOrm
    mapper = MessageDataMapper

    async def get_all_messages(self, user_id: int):
        query = select(self.model).filter_by(sender_id=user_id)
        result = await self.session.execute(query)
        grouped = {}
        for item in result.scalars().all():
            recipient_id = item.recipient_id
            if recipient_id not in grouped:
                grouped[recipient_id] = []
            grouped[recipient_id].append(item)
        return grouped

    async def get_by_user(self, sender_id: int, user_id: int):
        query = select(self.model).where(
            or_(
                and_(
                    MessageOrm.sender_id == sender_id,
                    MessageOrm.recipient_id == user_id,
                ),
                and_(
                    MessageOrm.sender_id == user_id,
                    MessageOrm.recipient_id == sender_id,
                ),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
