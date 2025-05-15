from datetime import date

from pydantic import BaseModel, Field


class UserRequestAdd(BaseModel):
    login: str
    username: str | None
    password: str


class UserAdd(BaseModel):
    login: str
    username: str | None
    hashed_password: str


class User(BaseModel):
    id: int
    login: str
    username: str | None
    created_at: date


class UserUpdateRequest(BaseModel):
    login: str | None = Field(None)
    username: str | None = Field(None)
    password: str | None = Field(None)


class UserUpdate(BaseModel):
    login: str | None = Field(None)
    username: str | None = Field(None)
    hashed_password: str | None = Field(None)
