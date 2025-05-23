from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from src.config import settings
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXIPRE_MINUTES
        )
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    # FIX: Fix empty except and HTTPException
    def decode_token(self, to_decode) -> dict:
        try:
            data = jwt.decode(
                to_decode, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
            )
        except:
            raise HTTPException(status_code=401)
        return data
