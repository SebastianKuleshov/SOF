from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile
from keycloak import KeycloakError

from app.common.repositories import StorageItemRepository
from app.common.schemas import StorageItemCreateSchema
from app.common.services import StorageItemService, KeycloakService, \
    ReportService
from app.dependencies import get_settings
from app.roles.models import RoleModel
from app.roles.repositories import RoleRepository
from app.users.repositories import UserRepository
from app.users.schemas import UserOutSchema, \
    UserUpdateSchema, UserUpdatePayloadSchema


class UserService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            role_repository: Annotated[RoleRepository, Depends()],
            storage_item_service: Annotated[StorageItemService, Depends()],
            keycloak_service: Annotated[KeycloakService, Depends()],
            storage_item_repository: Annotated[
                StorageItemRepository, Depends()],
            report_service: Annotated[ReportService, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.storage_item_service = storage_item_service
        self.keycloak_service = keycloak_service
        self.storage_item_repository = storage_item_repository
        self.report_service = report_service

    async def get_user(
            self,
            user_id: int
    ) -> UserOutSchema:
        user_model = await self.user_repository.get_by_id(user_id)

        settings = get_settings()

        item_model = await self.storage_item_repository.get_by_id(
            user_model.avatar_file_storage_id
        )

        avatar_url = await self.storage_item_service.generate_presigned_url(
            settings.AWS_BUCKET_NAME,
            item_model.storage_path
        ) if item_model else None

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

        settings = get_settings()

        users_with_avatar_url = []

        for user in users:
            item_model = await self.storage_item_repository.get_by_id(
                user.avatar_file_storage_id
            )
            avatar_url = await self.storage_item_service.generate_presigned_url(
                settings.AWS_BUCKET_NAME,
                item_model.storage_path
            ) if item_model else None

            user_with_avatar_url = UserOutSchema.model_validate(
                {
                    **user.__dict__,
                    'avatar_url': avatar_url
                }
            )
            users_with_avatar_url.append(
                user_with_avatar_url
            )

        return users_with_avatar_url

    async def update_user(
            self,
            target_user_id: int,
            requesting_user_id: int,
            user_schema: UserUpdateSchema,
            file: UploadFile
    ) -> UserOutSchema:
        user_model = await self.user_repository.get_entity_if_exists(
            target_user_id
        )
        if user_model.id != requesting_user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this user'
            )

        settings = get_settings()

        if user_schema.email is not None:
            try:
                await self.keycloak_service.update_account(
                    user_model.external_id,
                    {'email': user_schema.email}
                )
            except KeycloakError:
                raise HTTPException(
                    status_code=400,
                    detail='Email already exists'
                )

        if file:
            stored_file_path = await self.storage_item_service.upload_file(
                settings.AWS_BUCKET_NAME,
                f'avatars/{target_user_id}',
                file
            )

            stored_file_name = stored_file_path.split('/')[-1]

            new_item_model = await (
                self.storage_item_repository.create(
                    StorageItemCreateSchema(
                        original_file_name=file.filename,
                        stored_file_name=stored_file_name,
                        storage_path=stored_file_path
                    )
                ))

            if user_model.avatar_file_storage_id:
                old_item_model = await (
                    self.storage_item_repository.get_by_id(
                        user_model.avatar_file_storage_id
                    )
                )

                await self.storage_item_service.delete_file(
                    settings.AWS_BUCKET_NAME,
                    old_item_model.storage_path
                )

                await self.storage_item_repository.delete(
                    user_model.avatar_file_storage_id
                )

            user_schema = UserUpdatePayloadSchema(
                **user_schema.model_dump(exclude_unset=True),
                avatar_file_storage_id=new_item_model.id
            )

        await self.user_repository.update(
            target_user_id,
            user_schema
        )

        item_model = await self.storage_item_repository.get_by_id(
            user_model.avatar_file_storage_id
        )
        avatar_url = await self.storage_item_service.generate_presigned_url(
            settings.AWS_BUCKET_NAME,
            item_model.storage_path
        ) if item_model else None

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
