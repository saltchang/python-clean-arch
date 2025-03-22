from dataclasses import dataclass
from typing import Protocol

from core.model.user import User
from core.type import IDType


@dataclass
class UserRepository(Protocol):
    async def create(self, user: User) -> User: ...

    async def get_all(self) -> list[User]: ...

    async def get_by_id(self, user_id: IDType) -> User | None: ...

    async def get_by_username_or_email(self, username: str | None, email: str | None) -> User | None: ...

    async def update(self, user: User) -> User: ...

    async def delete(self, user_id: IDType) -> None: ...
