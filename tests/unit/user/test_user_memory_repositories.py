import pytest

from core.constant.user import DEFAULT_ROLE_KEY
from core.model.user import User
from core.type import IDType
from repository.memory.role import InMemoryRoleRepository
from repository.memory.user import InMemoryUserRepository


class TestMemoryRepositories:
    @pytest.mark.asyncio
    async def test_memory_user_repository(self):
        repo = InMemoryUserRepository()
        repo.reset()

        user = User(
            username='test_memory_user',
            email='test_memory@example.com',
            password_hash='hashed_password',
        )
        created_user = await repo.create(user)
        assert created_user.id is not None
        assert created_user.username == 'test_memory_user'

        retrieved_user = await repo.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == 'test_memory_user'

        all_users = await repo.get_all()
        assert len(all_users) >= 1
        assert any(u.username == 'test_memory_user' for u in all_users)

        user_by_username = await repo.get_by_username_or_email('test_memory_user', None)
        assert user_by_username is not None
        assert user_by_username.username == 'test_memory_user'

        user_by_email = await repo.get_by_username_or_email(None, 'test_memory@example.com')
        assert user_by_email is not None
        assert user_by_email.email == 'test_memory@example.com'

        updated_user = User(
            id=created_user.id,
            username='updated_memory_user',
            email='updated_memory@example.com',
            password_hash='hashed_password',
            is_verified=True,
            roles=[],
        )
        result = await repo.update(updated_user)
        assert result.username == 'updated_memory_user'
        assert result.email == 'updated_memory@example.com'

        await repo.delete(created_user.id)
        deleted_user = await repo.get_by_id(created_user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_memory_user_repository_exceptions(self):
        repo = InMemoryUserRepository()
        repo.reset()

        result = await repo.get_by_id(IDType(999))
        assert result is None

        result = await repo.get_by_username_or_email('nonexistent', 'nonexistent@example.com')
        assert result is None

    @pytest.mark.asyncio
    async def test_memory_role_repository(self):
        repo = InMemoryRoleRepository()
        repo.reset()

        default_role = await repo.get_by_key(DEFAULT_ROLE_KEY)
        assert default_role is not None
        assert default_role.key == DEFAULT_ROLE_KEY

        non_existent_role = await repo.get_by_key('non_existent')
        assert non_existent_role is None

        roles_by_id = await repo.get_by_ids([IDType(1)])
        assert len(roles_by_id) == 1
        assert roles_by_id[0].id == IDType(1)

        empty_roles_by_id = await repo.get_by_ids([])
        assert len(empty_roles_by_id) == 0

        non_existent_roles_by_id = await repo.get_by_ids([IDType(999)])
        assert len(non_existent_roles_by_id) == 0
