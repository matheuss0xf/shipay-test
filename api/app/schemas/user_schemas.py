from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, constr

from app.schemas.role_enum import RoleEnum


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: Optional[constr(min_length=8)] = None
    role: RoleEnum

    class Config:
        orm_mode = True


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    model_config = ConfigDict(from_attributes=True)


class RoleByUserPublic(BaseModel):
    user_id: int
    role: str
