from fastapi import APIRouter, HTTPException

from dependencies import DbDep, UserDap

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/{user_id}')
async def get_user_by_id(db: DbDep, user: UserDap, user_id: int):
    result = await db.users.get_filtered(id=user_id)
    if result == []:
        raise HTTPException(404, detail='User not found')
    user_from_res = result[0]
    user_from_res.login = f'@{user_from_res.login}'
    return user_from_res
