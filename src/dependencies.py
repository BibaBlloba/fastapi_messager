from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request

from src.database import async_session_maker
from src.schemas.users import User
from src.services.auth import AuthService
from src.utils.db_manager import DbManager


async def get_db():
    async with DbManager(session_factory=async_session_maker) as db:
        yield db


DbDep = Annotated[DbManager, Depends(get_db)]


async def get_current_token(request: Request):
    token = request.cookies.get('access_token', None)
    if token is None:
        try:
            credentials = request.headers['Authorization']
            scheme, token = credentials.split()
            if scheme.lower() != 'bearer':
                raise HTTPException(401)
        except KeyError:
            raise HTTPException(401)
    return token


async def get_current_user(token: str = Depends(get_current_token)):
    try:
        decoded_data = AuthService().decode_token(token)
        user = User(
            id=decoded_data.get('id'),
            login=decoded_data.get('login'),
            username=decoded_data.get('username'),
            created_at=decoded_data.get('created_at'),
        )
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail='Токен не действителен.')
    except KeyError as e:
        raise HTTPException(
            status_code=401, detail=f'Недостаточно данных в токене: {str(e)}'
        )
    return user


UserDap = Annotated[User, Depends(get_current_user)]
