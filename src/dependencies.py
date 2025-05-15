from typing import Annotated

from fastapi import Depends

from src.database import async_session_maker
from utils.db_manager import DbManager


async def get_db():
    async with DbManager(session_factory=async_session_maker) as db:
        yield db


DbDep = Annotated[DbManager, Depends(get_db)]
