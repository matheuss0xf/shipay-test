import string
from http import HTTPStatus
from random import choice
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.database import get_session
from app.models.user_management_models import Role, User
from app.schemas.user_schemas import RoleByUserPublic, UserPublic, UserSchema

router = APIRouter(prefix='/users', tags=['users'])
Session = Annotated[Session, Depends(get_session)]


def generate_random_password(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(choice(characters) for _ in range(length))
    return password


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session):
    db_role = session.query(Role).filter(Role.description == user.role.value).first()
    if not db_role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Papel informado não existe.'
        )

    password = user.password if user.password else generate_random_password()

    user_instance = User(
        name=user.name,
        email=user.email,
        password=password,
        role_id=db_role.id,
    )

    try:
        session.add(user_instance)
        session.commit()
        session.refresh(user_instance)
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Erro ao criar usuário: e-mail já existe ou dados inválidos.',
        )

    return user_instance


@router.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=RoleByUserPublic)
def get_role_by_user(user_id: int, session: Session):
    user = session.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='User not found')
    user_role = user.role
    if not user_role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Role not found for this user'
        )

    return RoleByUserPublic(user_id=user_id, role=user_role.description)
