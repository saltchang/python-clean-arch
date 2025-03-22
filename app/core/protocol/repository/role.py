from dataclasses import dataclass
from typing import Protocol

from core.model.user import Role
from core.type import IDType


@dataclass
class RoleRepository(Protocol):
    async def get_by_key(self, key: str) -> Role | None: ...

    async def get_by_ids(self, ids: list[IDType]) -> list[Role]: ...
