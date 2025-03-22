from typing import Self

from pydantic import BaseModel

from core.model.user import CreateUserPayload, UpdateUserPayload, User
from core.type import IDType


class CreateUserRequestModel(BaseModel):
    username: str
    email: str
    password: str

    def to_core(self) -> CreateUserPayload:
        return CreateUserPayload(
            username=self.username,
            email=self.email,
            password=self.password,
        )


class RetrieveUserModel(BaseModel):
    id: IDType
    username: str
    email: str
    is_verified: bool

    @classmethod
    def from_core(cls, user: User) -> Self:
        return cls.model_validate(user.__dict__)


class UpdateUserRequestModel(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_verified: bool | None = None
    role_ids: list[IDType] | None = None

    def to_core(self) -> UpdateUserPayload:
        return UpdateUserPayload(
            username=self.username,
            email=self.email,
            password=self.password,
            is_verified=self.is_verified,
            role_ids=self.role_ids,
        )
