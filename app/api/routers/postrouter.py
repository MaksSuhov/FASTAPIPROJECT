from fastapi import APIRouter, Query, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependences import get_like_service, get_post_service
from app.database.database import get_db
from app.models.authmodel import User
from app.models.likesmodel import Like
from app.models.postmodel import Post
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostSchema, PostCreateSchema, PostUpdateSchema
from app.services.CredService import CredService
from app.services.likeservice import LikeService
from app.services.postservice import PostService
from app.schemas.LikeSchema import LikeCreateSchema, LikeStateSchema

router = APIRouter()

@router.get('/posts', response_model=list[PostSchema])
async def get_all(limit: int = Query(20, ge=1, le=100, description='сколько постов вернуть'),
                  offset: int = Query(0, ge=0, description='сколько пропустить'),
                  current_user: User | None = Depends(CredService.get_optional_user),
                  db: AsyncSession = Depends(get_db)) -> list[Post]:
    repository = PostRepository(db)
    viewer_id = current_user.user_id if current_user else None
    return await repository.get_all(limit=limit, offset=offset, viewer_id=viewer_id)

@router.post('/posts', response_model=PostSchema)
async def create_new_post(payload:PostCreateSchema,
                          post_service:PostService=Depends(get_post_service))->Post:
    return await post_service.create_post(payload)

@router.patch('/posts/{post_id}', response_model=PostSchema)
async def update_post(
        payload: PostUpdateSchema,
        post_id: int = Path(...,detail='айди поста'),
        post_service:PostService=Depends(get_post_service))->Post:
    return await post_service.update_post(post_id, payload)

@router.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id:int = Path(...,detail='айди поста'),
        post_service:PostService=Depends(get_post_service))->None:
    return await post_service.delete(post_id)

@router.get('/posts/{post_id}/like', response_model=LikeStateSchema)
async def get_post_like_state(post_id: int = Path(..., detail='айди поста'),
                              like_service: LikeService = Depends(get_like_service)) -> LikeStateSchema:
    return await like_service.get_state(post_id)

@router.post('/posts/{post_id}/like', response_model=LikeStateSchema)
async def add_post_like(post_id: int = Path(..., detail='айди поста'),
                        like_service: LikeService = Depends(get_like_service)) -> LikeStateSchema:
    return await like_service.add_like(post_id)

@router.delete('/posts/{post_id}/like', response_model=LikeStateSchema)
async def delete_post_like(post_id: int = Path(..., detail='айди поста'),
                           like_service: LikeService = Depends(get_like_service)) -> LikeStateSchema:
    return await like_service.delete_like(post_id)