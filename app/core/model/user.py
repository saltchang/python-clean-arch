from dataclasses import dataclass, field

from core.type import IDType


@dataclass(frozen=True)
class Role:
    key: str
    name: str
    id: IDType = IDType(0)  # should be set by the repository


@dataclass(frozen=True)
class User:
    username: str
    email: str
    password_hash: str
    is_verified: bool = False
    roles: list[Role] = field(default_factory=list)
    id: IDType = IDType(0)  # should be set by the repository


@dataclass(frozen=True)
class CreateUserPayload:
    username: str
    email: str
    password: str


@dataclass(frozen=True)
class UpdateUserPayload:
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_verified: bool | None = None
    role_ids: list[IDType] | None = None
