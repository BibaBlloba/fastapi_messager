from sqlalchemy import and_, func, select
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
        last_msg_subq = (
            select(
                MessageOrm.sender_id,
                func.max(MessageOrm.id).label('last_msg_id'),
            )
            .where(MessageOrm.recipient_id == user_id)
            .group_by(MessageOrm.sender_id)
            .subquery()
        )

        last_msg = aliased(MessageOrm)

        query = (
            select(
                UserOrm,
                last_msg.content.label('last_message'),
                last_msg.created_at.label('last_message_time'),
            )
            .outerjoin(last_msg_subq, last_msg_subq.c.sender_id == UserOrm.id)
            .outerjoin(last_msg, last_msg.id == last_msg_subq.c.last_msg_id)
            .where(UserOrm.id != user_id)
            .order_by(UserOrm.username)
        )

        result = await self.session.execute(query)

        return [
            {
                'user': user,
                'last_message': last_msg,
                'last_message_time': last_msg_time,
            }
            for user, last_msg, last_msg_time in result.all()
        ]
