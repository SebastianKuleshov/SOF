from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import schemas
from app.auth.services import AuthService
from app.common.schemas_mixins import PasswordCreationMixin

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post(
    '/login',
    response_model=schemas.TokenBaseSchema
)
async def login(
        auth_service: Annotated[AuthService, Depends()],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    return await auth_service.login(form_data)


@router.post(
    '/refresh',
    response_model=schemas.TokenBaseSchema
)
async def refresh(
        request: Request,
        auth_service: Annotated[AuthService, Depends()],
        refresh_token: str
):
    return await auth_service.refresh(request, refresh_token)


@router.post(
    '/logout',
    dependencies=[Depends(AuthService.get_user_from_jwt)],
)
async def logout(
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        auth_service: Annotated[AuthService, Depends()]
) -> bool:
    return await auth_service.auth_repository.delete_user_tokens(user_id)


@router.post(
    '/forgot-password',
)
async def forgot_password(
        auth_service: Annotated[AuthService, Depends()],
        email_schema: schemas.EmailCreateSchema
) -> bool:
    return await auth_service.forgot_password(email_schema)


@router.post(
    '/reset-password',
)
async def reset_password(
        auth_service: Annotated[AuthService, Depends()],
        verification_token: str,
        new_password_data: PasswordCreationMixin
) -> bool:
    return await auth_service.reset_password(
        verification_token,
        new_password_data
    )
