from dataclasses import replace

from core.model.user import User
from core.protocol.repository.user import UserRepository
from core.type import IDType
from utility.decorator import singleton


@singleton
class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for testing"""

    def __init__(self):
        self.next_id = 1
        self.data: dict[IDType, User] = {}

    def reset(self):
        self.__init__()

    async def create(self, user: User) -> User:
        """Create a new user"""
        user_id = IDType(self.next_id)
        self.next_id += 1

        new_user = replace(user, id=user_id)

        self.data[user_id] = new_user
        return new_user

    async def get_all(self) -> list[User]:
        """Get all users"""
        return list(self.data.values())

    async def get_by_id(self, user_id: IDType) -> User | None:
        """Get a user by ID"""
        return self.data.get(user_id)

    async def get_by_username_or_email(self, username: str | None, email: str | None) -> User | None:
        """Get a user by username or email"""
        for user in self.data.values():
            if (username and user.username == username) or (email and user.email == email):
                return user
        return None

    async def update(self, user: User) -> User:
        """Update a user"""
        if user.id not in self.data:
            raise ValueError(f'User with ID {user.id} not found')

        self.data[user.id] = user
        return user

    async def delete(self, user_id: IDType) -> None:
        """Delete a user"""
        if user_id in self.data:
            del self.data[user_id]
