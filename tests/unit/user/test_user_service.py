from unittest.mock import patch

import pytest

from core.constant.user import DEFAULT_ROLE_KEY
from core.error import DuplicateError, NotFoundError
from core.model.user import CreateUserPayload, Role, UpdateUserPayload, User
from core.type import IDType
from repository.memory.role import InMemoryRoleRepository
from repository.memory.user import InMemoryUserRepository
from service.user import UserService


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    repo = InMemoryUserRepository()
    repo.reset()
    return repo


@pytest.fixture
def role_repository() -> InMemoryRoleRepository:
    repo = InMemoryRoleRepository()
    repo.reset()
    return repo


@pytest.fixture
def admin_role() -> Role:
    return Role(id=IDType(2), name='Admin', key='admin')


TEST_USER_1_NAME = 'Test User'
TEST_USER_2_NAME = 'Test User 2'
TEST_USER_3_NAME = 'Test User 3'
TEST_USER_4_NAME = 'Test User 4'


async def insert_user_1(user_service: UserService) -> User:
    return await user_service.create_user(
        payload=CreateUserPayload(username=TEST_USER_1_NAME, email='test@test.com', password='password')
    )


async def insert_user_2(user_service: UserService) -> User:
    return await user_service.create_user(
        payload=CreateUserPayload(username=TEST_USER_2_NAME, email='test2@test.com', password='password')
    )


async def insert_user_3(user_service: UserService) -> User:
    return await user_service.create_user(
        payload=CreateUserPayload(username=TEST_USER_3_NAME, email='test3@test.com', password='password')
    )


async def insert_user_4(user_service: UserService) -> User:
    return await user_service.create_user(
        payload=CreateUserPayload(username=TEST_USER_4_NAME, email='test4@test.com', password='password')
    )


class TestUserService:
    @pytest.mark.asyncio
    async def test_get_empty_user_list(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        users = await user_service.get_all_users()

        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        await insert_user_1(user_service)
        await insert_user_2(user_service)

        users = await user_service.get_all_users()

        assert len(users) == 2
        assert users[0].username == TEST_USER_1_NAME
        assert users[1].username == TEST_USER_2_NAME

    @pytest.mark.asyncio
    async def test_get_user_list(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        await insert_user_1(user_service)
        await insert_user_2(user_service)
        await insert_user_3(user_service)

        users = await user_service.get_all_users()

        assert len(users) == 3
        assert users[0].username == TEST_USER_1_NAME
        assert users[1].username == TEST_USER_2_NAME
        assert users[2].username == TEST_USER_3_NAME

    @pytest.mark.asyncio
    async def test_update_user(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        user_4 = await insert_user_4(user_service)

        UPDATE_USER_NAME = 'Updated User'
        UPDATE_USER_EMAIL = 'updated@test.com'

        await user_service.update_user(
            user_4.id,
            payload=UpdateUserPayload(username=UPDATE_USER_NAME, email=UPDATE_USER_EMAIL),
        )
        user = await user_service.get_user_by_id(user_4.id)

        assert user is not None
        assert user.username == UPDATE_USER_NAME
        assert user.email == UPDATE_USER_EMAIL

    @pytest.mark.asyncio
    async def test_delete_user(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        user1 = await insert_user_1(user_service)
        await insert_user_2(user_service)
        await insert_user_3(user_service)
        await insert_user_4(user_service)

        users = await user_service.get_all_users()
        assert len(users) == 4

        await user_service.delete_user(user1.id)
        user = await user_service.get_user_by_id(user1.id)

        assert user is None

        users = await user_service.get_all_users()
        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_get_user_by_id(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        user1 = await insert_user_1(user_service)

        retrieved_user = await user_service.get_user_by_id(user1.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user1.id
        assert retrieved_user.username == TEST_USER_1_NAME

        non_existent_id = IDType(999)
        non_existent_user = await user_service.get_user_by_id(non_existent_id)
        assert non_existent_user is None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        await insert_user_1(user_service)

        with pytest.raises(DuplicateError) as exc_info:
            await user_service.create_user(
                payload=CreateUserPayload(
                    username=TEST_USER_1_NAME,
                    email='different@test.com',
                    password='password',
                )
            )

        assert f"User with username '{TEST_USER_1_NAME}' already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        user1 = await insert_user_1(user_service)

        with pytest.raises(DuplicateError) as exc_info:
            await user_service.create_user(
                payload=CreateUserPayload(username='different_username', email=user1.email, password='password')
            )

        assert f"User with email '{user1.email}' already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_missing_default_role(
        self,
        user_repository: InMemoryUserRepository,
    ):
        empty_role_repository = InMemoryRoleRepository()
        empty_role_repository.data = {}

        user_service = UserService(user_repository, empty_role_repository)

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.create_user(
                payload=CreateUserPayload(username=TEST_USER_1_NAME, email='test@test.com', password='password')
            )

        assert 'Default role not found' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_nonexistent(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        non_existent_id = IDType(999)

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.update_user(non_existent_id, payload=UpdateUserPayload(username='new_username'))

        assert f'User with ID {non_existent_id} not found' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_duplicate_username(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        await insert_user_1(user_service)
        user2 = await insert_user_2(user_service)

        with pytest.raises(DuplicateError) as exc_info:
            await user_service.update_user(user2.id, payload=UpdateUserPayload(username=TEST_USER_1_NAME))

        assert f"Username '{TEST_USER_1_NAME}' is already taken" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_duplicate_email(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        user1 = await insert_user_1(user_service)
        user2 = await insert_user_2(user_service)

        with pytest.raises(DuplicateError) as exc_info:
            await user_service.update_user(user2.id, payload=UpdateUserPayload(email=user1.email))

        assert f"Email '{user1.email}' is already registered" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_with_roles(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
        admin_role: Role,
    ):
        role_repository.data[admin_role.id] = admin_role

        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        default_role_id = next(role.id for role in role_repository.data.values() if role.key == DEFAULT_ROLE_KEY)

        updated_user = await user_service.update_user(
            user1.id, payload=UpdateUserPayload(role_ids=[default_role_id, admin_role.id])
        )

        assert len(updated_user.roles) == 2
        role_keys = [role.key for role in updated_user.roles]
        assert DEFAULT_ROLE_KEY in role_keys
        assert 'admin' in role_keys

    @pytest.mark.asyncio
    async def test_update_user_with_invalid_roles(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        non_existent_role_id = IDType(999)

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.update_user(user1.id, payload=UpdateUserPayload(role_ids=[non_existent_role_id]))

        assert f'Role(s) with ID(s) {non_existent_role_id} not found' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_with_empty_roles(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        with pytest.raises(ValueError) as exc_info:
            await user_service.update_user(user1.id, payload=UpdateUserPayload(role_ids=[]))

        assert 'User must have at least one role' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_nonexistent(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        non_existent_id = IDType(999)

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.delete_user(non_existent_id)

        assert f'User with ID {non_existent_id} not found' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_password(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        old_password_hash = user1.password_hash

        updated_user = await user_service.update_user(user1.id, payload=UpdateUserPayload(password='new_password'))

        assert updated_user.password_hash != old_password_hash

    @pytest.mark.asyncio
    async def test_update_user_same_username_email(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        updated_user = await user_service.update_user(
            user1.id,
            payload=UpdateUserPayload(username=user1.username, email=user1.email),
        )

        assert updated_user.username == user1.username
        assert updated_user.email == user1.email

    @pytest.mark.asyncio
    async def test_update_user_partial_payload(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        updated_user = await user_service.update_user(
            user1.id,
            payload=UpdateUserPayload(username=user1.username, email=user1.email),
        )

        assert updated_user.is_verified == user1.is_verified
        assert updated_user.username == user1.username
        assert updated_user.email == user1.email
        assert updated_user.roles == user1.roles

    @pytest.mark.asyncio
    async def test_create_user_repository_exception(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        with patch.object(user_repository, 'create', side_effect=Exception('Test exception')):
            with pytest.raises(Exception) as exc_info:
                await user_service.create_user(
                    payload=CreateUserPayload(
                        username=TEST_USER_1_NAME,
                        email='test@test.com',
                        password='password',
                    )
                )

            assert 'Test exception' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_all_users_repository_exception(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        with patch.object(user_repository, 'get_all', side_effect=Exception('Test exception')):
            with pytest.raises(Exception) as exc_info:
                await user_service.get_all_users()

            assert 'Test exception' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_by_id_repository_exception(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)

        with patch.object(user_repository, 'get_by_id', side_effect=Exception('Test exception')):
            with pytest.raises(Exception) as exc_info:
                await user_service.get_user_by_id(IDType(1))

            assert 'Test exception' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_repository_exception(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        with patch.object(user_repository, 'update', side_effect=Exception('Test exception')):
            with pytest.raises(Exception) as exc_info:
                await user_service.update_user(
                    user1.id, payload=UpdateUserPayload(username=user1.username, email=user1.email)
                )

            assert 'Test exception' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_repository_exception(
        self,
        user_repository: InMemoryUserRepository,
        role_repository: InMemoryRoleRepository,
    ):
        user_service = UserService(user_repository, role_repository)
        user1 = await insert_user_1(user_service)

        with patch.object(user_repository, 'delete', side_effect=Exception('Test exception')):
            with pytest.raises(Exception) as exc_info:
                await user_service.delete_user(user1.id)

            assert 'Test exception' in str(exc_info.value)
