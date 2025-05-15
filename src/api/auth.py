from fastapi import APIRouter, HTTPException

from src.dependencies import DbDep
from src.schemas.users import UserAdd, UserRequestAdd
from src.services.auth import AuthService
from src.utils.exceptions import ObjectNotFoundException

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register')
async def register_user(
    db: DbDep,
    data: UserRequestAdd,
):
    hashed_password = AuthService().hash_password(data.password)
    hashed_user_data = UserAdd(
        login=data.login,
        username=data.username,
        hashed_password=hashed_password,
    )
    try:
        result = await db.users.add(hashed_user_data)
    except ObjectNotFoundException as ex:
        raise HTTPException(409, ex.details)
    await db.commit()
    return result
