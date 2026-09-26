from fastapi import APIRouter, Depends, Response

from app.api.dependences import get_auth_service
from app.models.authmodel import User
from app.schemas.userschemas import UserSchema, Credentials, CurrentUserSchema
from app.services.CredService import CredService
from app.services.authservice import AuthService

router = APIRouter()

@router.post('/register', response_model=UserSchema)
async def register(cred:Credentials,
                   auth_service: AuthService = Depends(get_auth_service))->User:
    return await auth_service.register(cred)

@router.post('/login', response_model=UserSchema)
async def login(cred:Credentials,
                response:Response,
                auth_service: AuthService = Depends(get_auth_service)
                )->User:
    return await auth_service.login(cred, response)

@router.post('/api/auth/logout')
async def logout(response:Response)->None:
    response.delete_cookie(key='access_token', path='/')

@router.get('/api/auth/me',response_model=CurrentUserSchema)
async def read_my_profile(current_user: User = Depends(CredService.get_current_user))->User:
    return current_user

