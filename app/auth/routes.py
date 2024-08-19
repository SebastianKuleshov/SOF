from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import schemas
from app.auth.services import AuthService

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
