from enum import Enum


class RoleEnum(str, Enum):
    admin = 'Admin'
    user = 'Edit'
    manager = 'Member'
