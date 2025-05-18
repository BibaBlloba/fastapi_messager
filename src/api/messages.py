import json

from fastapi import APIRouter, Query, Response, WebSocket, WebSocketDisconnect

from dependencies import DbDep, UserDap
from schemas.messages import MessageAdd
from services.auth import AuthService
from src.connectors.redis import redis_manager

router = APIRouter(prefix='/messages')


@router.websocket('/ws')
async def websocket(
    websocket: WebSocket,
    db: DbDep,
    token: str = Query(),
):
    try:
        user_data = AuthService().decode_token(token)
        user_id: int = user_data.get('id')
        user_login: str = user_data.get('login')

        await websocket.accept()
        await redis_manager.add_connection(user_data.get('id'), websocket)

        # await websocket.send_text(
        #     json.dumps(
        #         {
        #             'status': 'connected',
        #             'user_id': user_id,
        #             'login': user_login,
        #         }
        #     )
        # )

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            db_message_data = MessageAdd(
                sender_id=user_id,
                recipient_id=message['to'],
                content=message['content'],
            )
            result = await db.messages.add(db_message_data)

            if message['type'] == 'private':
                await redis_manager.send_to_user(message=result)

            await db.commit()

    except WebSocketDisconnect:
        await redis_manager.remove_connection(user_id)
    except Exception as e:
        try:
            print(e)
            await websocket.close(code=1011)
        except RuntimeError:
            pass


@router.get('')
async def get_all_messages(
    db: DbDep,
    user: UserDap,
):
    result = await db.messages.get_all_messages(user_id=user.id)
    return result


@router.get('/users')
async def get_users_list(
    db: DbDep,
    user: UserDap,
):
    return await db.users.get_all_with_last_message(user.id)


@router.get('/friends')
async def get_friends_list(
    db: DbDep,
    user: UserDap,
):
    return await db.users.get_all_with_last_message()


@router.get('/{user_id}')
async def get_messages_by_id(user_id: int, db: DbDep, user: UserDap):
    sender_id = user.id
    return await db.messages.get_by_user(sender_id, user_id)
