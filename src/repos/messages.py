from sqlalchemy import and_, case, func, or_, select

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
        query = select(
            self.model,
            case(
                (MessageOrm.sender_id == sender_id, 'outgoing'),
                (MessageOrm.sender_id == user_id, 'incoming'),
                else_=None,
            ).label('direction'),
        ).where(
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

        messages = []
        for row in result:
            message = row[0]
            message.direction = row.direction
            messages.append(message)

        return messages
