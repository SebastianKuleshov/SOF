from typing import Annotated

from fastapi import APIRouter, Depends, Request, Security
from fastapi.security import OAuth2PasswordRequestForm, \
    HTTPAuthorizationCredentials, HTTPBearer

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
        auth_service: Annotated[AuthService, Depends()],
        refresh_token: HTTPAuthorizationCredentials = Security(
            HTTPBearer(scheme_name="Refresh token")
        )
):
    return await auth_service.refresh(
        refresh_token.credentials
    )


@router.post(
    '/logout'
)
async def logout(
        auth_service: Annotated[AuthService, Depends()],
        refresh_token: HTTPAuthorizationCredentials = Security(
            HTTPBearer(scheme_name="Refresh token")
        )
) -> bool:
    return await auth_service.logout(refresh_token.credentials)


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
        new_password_data: PasswordCreationMixin,
        user_id: int = Depends(AuthService.get_user_id_from_reset_password_jwt)
) -> bool:
    return await auth_service.reset_password(
        user_id,
        new_password_data
    )
