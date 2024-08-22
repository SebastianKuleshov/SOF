from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.exc import IntegrityError

from app.common.services.aws_s3 import S3Service
from app.dependencies import get_password_hash
from app.roles.models import RoleModel
from app.roles.repositories import RoleRepository
from app.users.repositories import UserRepository
from app.users.schemas import UserCreateSchema, UserOutSchema, \
    UserUpdateSchema, UserUpdatePayloadSchema


class UserService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            role_repository: Annotated[RoleRepository, Depends()],
            s3_service: Annotated[S3Service, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.s3_service = s3_service

    async def create_user(
            self,
            user: UserCreateSchema
    ) -> UserOutSchema:
        if await self.user_repository.get_one(
                {'email': user.email}
        ) is not None:
            raise HTTPException(
                status_code=400,
                detail='Email already exists'
            )
        user.password = await get_password_hash(user.password)
        user_model = await self.user_repository.create(user)

        roles = await self.role_repository.get_roles_by_name(['user'])
        await self.user_repository.attach_roles_to_user(
            user_model.id,
            roles
        )

        return UserOutSchema.model_validate(user_model)

    async def get_user(
            self,
            user_id: int
    ) -> UserOutSchema:
        user_model = await self.user_repository.get_by_id(user_id)
        avatar_url = await self.s3_service.generate_presigned_url(
            user_model.avatar_key
        ) if user_model.avatar_key else None

        return UserOutSchema.model_validate(
            {
                **user_model.__dict__,
                'avatar_url': avatar_url
            }
        )

    async def get_users(
            self,
            skip: int,
            limit: int
    ) -> list[UserOutSchema]:
        users = await self.user_repository.get_multi(skip, limit)
        return [
            UserOutSchema.model_validate(
                {
                    **user.__dict__,
                    'avatar_url': await self.s3_service.generate_presigned_url(
                        user.avatar_key
                    ) if user.avatar_key else None
                }
            ) for user in users
        ]

    async def update_user(
            self,
            target_user_id: int,
            requesting_user_id: int,
            user_schema: UserUpdateSchema,
            file: UploadFile
    ) -> UserOutSchema:
        user = await self.user_repository.get_entity_if_exists(target_user_id)
        if user.id != requesting_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this user'
            )

        if file:
            avatar_key = await self.s3_service.upload_file(
                user,
                file
            )
        else:
            avatar_key = None

        user_schema = UserUpdatePayloadSchema(
            **user_schema.model_dump(exclude_unset=True),
            avatar_key=avatar_key
        )

        try:
            await self.user_repository.update(
                target_user_id,
                user_schema
            )
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail=f'Email already exists {e}'
            )

        user_model = await self.user_repository.get_by_id(
            target_user_id
        )

        avatar_url = await self.s3_service.generate_presigned_url(
            user_model.avatar_key
        ) if user_model.avatar_key else None

        return UserOutSchema.model_validate(
            {
                **user_model.__dict__,
                'avatar_url': avatar_url
            }
        )

    async def delete_user(
            self,
            target_user_id: int,
            requesting_user_id: int
    ) -> bool:
        user = await self.user_repository.get_entity_if_exists(target_user_id)
        if user.id != requesting_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this user'
            )
        return await self.user_repository.delete(target_user_id)

    async def __check_if_roles_already_attached(
            self,
            user_id: int,
            roles: list[RoleModel]
    ) -> bool:
        user = await self.user_repository.get_by_id_with_roles(user_id)
        if any(role in user.roles for role in roles):
            raise HTTPException(
                status_code=400,
                detail='User already has one of the roles'
            )
        return False

    async def ban_user(
            self,
            requesting_user_id: int,
            target_user_id: int
    ) -> bool:
        await self.user_repository.get_entity_if_exists(
            target_user_id
        )
        if requesting_user_id == target_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to ban yourself'
            )

        roles = await self.role_repository.get_roles_by_name(['banned'])
        await self.__check_if_roles_already_attached(
            target_user_id,
            roles
        )

        await self.user_repository.attach_roles_to_user(
            target_user_id,
            roles
        )

        return True

    async def unban_user(
            self,
            target_user_id: int
    ) -> bool:
        await self.user_repository.get_entity_if_exists(
            target_user_id
        )

        roles = await self.role_repository.get_roles_by_name(['banned'])
        await self.user_repository.detach_roles_from_user(
            target_user_id,
            roles
        )

        return True

    async def get_user_permissions(
            self,
            user_id: int
    ) -> set[str]:
        user = await self.user_repository.get_by_id_with_joins(user_id)
        user_permissions = {
            permission.name for role in user.roles
            for permission in role.permissions
        }

        return user_permissions

    async def check_and_update_user_role(
            self,
            user_id: int,
            increase: bool
    ) -> bool:
        roles = await self.role_repository.get_roles_by_name(
            ['advanced_user']
        )
        if increase:
            await self.user_repository.attach_roles_to_user(
                user_id,
                roles
            )
        else:
            await self.user_repository.detach_roles_from_user(
                user_id,
                roles
            )
        return True
