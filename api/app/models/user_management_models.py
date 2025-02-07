from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship
from sqlalchemy.sql import func

table_registry = registry()


@table_registry.mapped_as_dataclass
class Role:
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String, nullable=False)


@table_registry.mapped_as_dataclass
class Claim:
    __tablename__ = 'claims'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    user_claims: Mapped['UserClaim'] = relationship('UserClaim', back_populates='claim')
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default='true')


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True, init=False
    )

    user_claims: Mapped['UserClaim'] = relationship('UserClaim', back_populates='user', init=False)
    role: Mapped['Role'] = relationship('Role', backref='users', init=False)


@table_registry.mapped_as_dataclass
class UserClaim:
    __tablename__ = 'user_claims'
    __table_args__ = (UniqueConstraint('user_id', 'claim_id', name='user_claims_un'),)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'), primary_key=True)
    claim_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('claims.id'), primary_key=True)

    user: Mapped['User'] = relationship('User', back_populates='user_claims')
    claim: Mapped['Claim'] = relationship('Claim', back_populates='user_claims')
