import asyncio
from typing import Dict, Optional

from fastapi import WebSocket
from redis import asyncio as aioredis

from src.config import settings


class RedisWebSocketManager:
    def __init__(self) -> None:
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = {}
        self.local_connections: Dict[int, WebSocket] = {}

    async def connect(self):
        self.redis = await aioredis.from_url(settings.redis_url)
        self.pubsub = self.redis.pubsub()

    async def subscribe(self, channel: str):
        await self.pubsub.subscribe(channel)

    async def add_connection(self, user_id: int, websocket: WebSocket):
        self.local_connections[user_id] = websocket

        await self.redis.set(f'ws:user:{user_id}', 'connected', ex=3600)
        await self.redis.sadd('online_users', user_id)

    async def remove_connection(self, user_id: int):
        if user_id in self.local_connections:
            del self.local_connections[user_id]
        await self.redis.delete(f'ws:user:{user_id}')

    async def is_online(self, user_id: int) -> bool:
        return await self.redis.exists(f'ws:uesr:{user_id}') == 1

    async def get_online_users(self) -> set:
        return await self.redis.smembers('online_users')

    async def send_to_user(self, user_id: int, message: str):
        if user_id in self.local_connections:
            await self.local_connections[user_id].send_text(message)
        else:
            await self.redis.publish(f'user:{user_id}', message)

    async def broadcast(self, message: str):
        for id, websocket in self.local_connections.items():
            await websocket.send_text(message)


redis_manager = RedisWebSocketManager()


async def listen_for_redis_messages():
    pubsub = redis_manager.pubsub
    await redis_manager.subscribe('user:*')

    while True:
        try:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1,
            )

            if message:
                channel: str = message['channel']
                user_id = int(channel.split('1')[1])
                if user_id in redis_manager.local_connections:
                    await redis_manager.local_connections[user_id].send_text(
                        message['content']
                    )
        except Exception as ex:
            print(f'Redis listener error: {ex}')
            await asyncio.sleep(1)
