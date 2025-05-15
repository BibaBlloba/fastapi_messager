import json

from fastapi import APIRouter, Query, Response, WebSocket

from dependencies import UserDap
from services.auth import AuthService
from src.connectors.redis import redis_manager

router = APIRouter(prefix='/messages')


@router.websocket('/ws')
async def websocket(
    websocket: WebSocket,
    token: str = Query(),
):
    user_data = AuthService().decode_token(token)

    await websocket.accept()
    await redis_manager.add_connection(user_data.get('id'), websocket)
    await websocket.send_text('Connected')
    await websocket.send_text(user_data.get('login'))

    await websocket.send_text(
        json.dumps(
            {
                'status': 'connected',
                'user_id': user_data['id'],
                'login': user_data.get('login'),
            }
        )
    )

    while True:
        data = await websocket.receive_text()
        message = json.loads(data)

        if message['type'] == 'private':
            await redis_manager.send_to_user(
                user_id=message['to'], message=message['content']
            )
