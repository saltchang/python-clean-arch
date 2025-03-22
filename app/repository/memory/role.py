from core.constant.user import (
    DEFAULT_ROLE_KEY,
    DEFAULT_ROLE_NAME,
)
from core.model.user import Role
from core.protocol.repository.role import RoleRepository
from core.type import IDType
from utility.decorator import singleton


@singleton
class InMemoryRoleRepository(RoleRepository):
    def __init__(self):
        self.next_id_counter = 2

        self.data: dict[IDType, Role] = {
            IDType(1): Role(
                id=IDType(1),
                key=DEFAULT_ROLE_KEY,
                name=DEFAULT_ROLE_NAME,
            ),
        }

    def reset(self):
        self.__init__()

    async def get_by_key(self, key: str) -> Role | None:
        return next((role for role in self.data.values() if role.key == key), None)

    async def get_by_ids(self, ids: list[IDType]) -> list[Role]:
        return [role for role in self.data.values() if role.id in ids]
