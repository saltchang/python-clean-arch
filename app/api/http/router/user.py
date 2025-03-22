from fastapi import APIRouter
from starlette import status

from api.http.dependencies.user import UserServiceDependency
from api.http.schema.user import CreateUserRequestModel, RetrieveUserModel, UpdateUserRequestModel
from core.error import NotFoundError
from core.type import IDType

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('', response_model=RetrieveUserModel, status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequestModel, user_service: UserServiceDependency):
    user = await user_service.create_user(request.to_core())

    return RetrieveUserModel.from_core(user)


@router.get('', response_model=list[RetrieveUserModel])
async def get_all_users(user_service: UserServiceDependency):
    users = await user_service.get_all_users()

    return [RetrieveUserModel.from_core(user) for user in users]


@router.get('/{user_id}', response_model=RetrieveUserModel)
async def get_user(user_id: IDType, user_service: UserServiceDependency):
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise NotFoundError('User not found')

    return RetrieveUserModel.from_core(user)


@router.patch('/{user_id}', response_model=RetrieveUserModel)
async def update_user(user_id: IDType, request: UpdateUserRequestModel, user_service: UserServiceDependency):
    user = await user_service.update_user(user_id, request.to_core())

    return RetrieveUserModel.from_core(user)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: IDType, user_service: UserServiceDependency):
    await user_service.delete_user(user_id)
