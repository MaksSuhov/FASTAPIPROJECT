from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependences import get_post_service
from app.database.database import get_db
from app.models.postmodel import Post
from app.repositories.postrepository import PostRepository
from app.schemas.postschemas import PostSchema, PostCreateSchema, PostUpdateSchema
from app.services.postservice import PostService

router = APIRouter()

@router.get('/posts', response_model=list[PostSchema])
async def get_all(db:AsyncSession = Depends(get_db)) -> list[Post]:
    repository = PostRepository(db)
    return await repository.get_all()

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