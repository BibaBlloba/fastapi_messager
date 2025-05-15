from fastapi import APIRouter, HTTPException, Response

from src.dependencies import DbDep, UserDap, ValidateUserDap
from src.schemas.users import User, UserAdd, UserRequestAdd
from src.services.auth import AuthService
from src.utils.exceptions import ObjectExists

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
    except ObjectExists as ex:
        raise HTTPException(409, ex.detail)
    await db.commit()
    return result


@router.post('/login')
async def login(
    response: Response,
    user: User = ValidateUserDap,
):
    jwt_payload = {
        'id': user.id,
        'login': user.login,
        'username': user.login,
        'created_at': user.created_at.isoformat(),
    }
    access_token = AuthService().create_access_token(jwt_payload)
    response.set_cookie(
        'access_token', access_token, secure=False, samesite='lax', httponly=False
    )
    return {'access_token': access_token}


@router.get('/me')
async def get_me(
    user: UserDap,
):
    return user


@router.post('/logout')
async def logout(
    user: UserDap,
    response: Response,
):
    response.delete_cookie('access_token')
    return {'status': 'ok'}
