import logging
from dataclasses import asdict, replace

from core.constant.user import DEFAULT_ROLE_KEY
from core.error import DuplicateError, NotFoundError
from core.model.user import CreateUserPayload, Role, UpdateUserPayload, User
from core.protocol.repository.role import RoleRepository
from core.protocol.repository.user import UserRepository
from core.type import IDType
from core.utility.user import hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository):
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def create_user(self, payload: CreateUserPayload) -> User:
        default_role = await self.role_repository.get_by_key(DEFAULT_ROLE_KEY)
        if not default_role:
            logger.error(f"Default role with key '{DEFAULT_ROLE_KEY}' not found in database")
            raise NotFoundError('Default role not found')

        existing_user = await self.user_repository.get_by_username_or_email(payload.username, payload.email)
        if existing_user:
            if existing_user.username == payload.username:
                raise DuplicateError(f"User with username '{payload.username}' already exists")
            else:
                raise DuplicateError(f"User with email '{payload.email}' already exists")

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
            roles=[default_role],
        )

        try:
            return await self.user_repository.create(user)
        except Exception as e:
            logger.error(f'Failed to create user: {str(e)}')
            raise

    async def get_all_users(self) -> list[User]:
        try:
            return await self.user_repository.get_all()
        except Exception as e:
            logger.error(f'Failed to retrieve all users: {str(e)}')
            raise

    async def get_user_by_id(self, user_id: IDType) -> User | None:
        try:
            return await self.user_repository.get_by_id(user_id)
        except Exception as e:
            logger.error(f'Failed to retrieve user with ID {user_id}: {str(e)}')
            raise

    async def _validate_user_exists(self, user_id: IDType) -> User:
        """Validate and return a user if it exists, otherwise raise NotFoundError."""
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise NotFoundError(f'User with ID {user_id} not found')
        return existing_user

    async def _validate_unique_username(self, username: str, current_username: str) -> None:
        """Validate that a username is unique (if changed)."""
        if username == current_username:
            return

        duplicate = await self.user_repository.get_by_username_or_email(username, None)
        if duplicate:
            raise DuplicateError(f"Username '{username}' is already taken")

    async def _validate_unique_email(self, email: str, current_email: str) -> None:
        """Validate that an email is unique (if changed)."""
        if email == current_email:
            return

        duplicate = await self.user_repository.get_by_username_or_email(None, email)
        if duplicate:
            raise DuplicateError(f"Email '{email}' is already registered")

    async def _get_validated_roles(self, role_ids: list[IDType]) -> list:
        """Get and validate roles from role IDs."""
        if not role_ids:
            raise ValueError('User must have at least one role')

        roles = await self.role_repository.get_by_ids(role_ids)

        if len(roles) != len(role_ids):
            found_ids = {role.id for role in roles}
            missing_ids = [str(rid) for rid in role_ids if rid not in found_ids]

            logger.error(f'Role IDs not found in database: {", ".join(missing_ids)}')
            raise NotFoundError(f'Role(s) with ID(s) {", ".join(missing_ids)} not found')

        return roles

    async def _prepare_user_update_params(self, existing_user: User, payload: UpdateUserPayload) -> dict:
        """Prepare update parameters based on payload and validate when needed."""
        update_params = {k: v for k, v in asdict(payload).items() if v is not None}

        if 'username' in update_params:
            await self._validate_unique_username(update_params['username'], existing_user.username)

        if 'email' in update_params:
            await self._validate_unique_email(update_params['email'], existing_user.email)

        if 'password' in update_params:
            update_params['password_hash'] = hash_password(update_params.pop('password'))

        roles: list[Role] = existing_user.roles
        if 'role_ids' in update_params:
            role_ids = update_params.pop('role_ids')
            roles = await self._get_validated_roles(role_ids)
            update_params['roles'] = roles

        return update_params

    async def update_user(self, user_id: IDType, payload: UpdateUserPayload) -> User:
        existing_user = await self._validate_user_exists(user_id)

        update_params = await self._prepare_user_update_params(existing_user, payload)

        updated_user = replace(existing_user, **update_params)

        try:
            return await self.user_repository.update(updated_user)
        except Exception as e:
            logger.error(f'Failed to update user with ID {user_id}: {str(e)}')
            raise

    async def delete_user(self, user_id: IDType) -> None:
        await self._validate_user_exists(user_id)

        try:
            await self.user_repository.delete(user_id)
        except Exception as e:
            logger.error(f'Failed to delete user with ID {user_id}: {str(e)}')
            raise
