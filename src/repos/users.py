from sqlalchemy import and_, case, func, or_, select, true
from sqlalchemy.orm import aliased

from src.models.messages import MessageOrm
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

    async def get_all_with_last_message(self, user_id: int):
        last_msg_ids_subq = (
            select(
                func.least(MessageOrm.sender_id, MessageOrm.recipient_id).label(
                    'user1'
                ),
                func.greatest(MessageOrm.sender_id, MessageOrm.recipient_id).label(
                    'user2'
                ),
                func.max(MessageOrm.id).label('last_msg_id'),
            )
            .where(
                (MessageOrm.sender_id == user_id) | (MessageOrm.recipient_id == user_id)
            )
            .group_by(
                func.least(MessageOrm.sender_id, MessageOrm.recipient_id),
                func.greatest(MessageOrm.sender_id, MessageOrm.recipient_id),
            )
            .subquery('last_msg_ids')
        )

        last_messages = aliased(MessageOrm, name='last_messages')

        partner_ids = (
            select(
                case(
                    (MessageOrm.sender_id == user_id, MessageOrm.recipient_id),
                    else_=MessageOrm.sender_id,
                ).label('partner_id'),
                MessageOrm.id.label('message_id'),
            )
            .join(last_msg_ids_subq, MessageOrm.id == last_msg_ids_subq.c.last_msg_id)
            .subquery('partner_ids')
        )

        query = (
            select(
                UserOrm,
                last_messages.content.label('last_message'),
                last_messages.created_at.label('last_message_time'),
                case(
                    (last_messages.sender_id == user_id, 'outgoing'),
                    else_='incoming',
                ).label('direction'),
            )
            .select_from(partner_ids)
            .join(last_messages, last_messages.id == partner_ids.c.message_id)
            .join(UserOrm, UserOrm.id == partner_ids.c.partner_id)
            .order_by(last_messages.created_at.desc())
        )

        result = await self.session.execute(query)

        return [
            {
                'user': user,
                'last_message': content,
                'last_message_time': timestamp,
                'direction': direction,
            }
            for user, content, timestamp, direction in result.all()
        ]
