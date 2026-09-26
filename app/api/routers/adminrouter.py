from fastapi import APIRouter, Depends, Path

from app.api.dependences import get_admin_service
from app.models.postmodel import Post
from app.schemas.postschemas import PostUpdateSchema, PostSchema
from app.services.adminservice import AdminService


router = APIRouter()


@router.patch('/admin/posts/{post_id}', response_model=PostSchema)
async def update_post(
        payload: PostUpdateSchema,
        post_id: int = Path(..., description='айди поста'),
        admin_service: AdminService = Depends(get_admin_service)
        ) -> Post:

    return await admin_service.admin_update(post_id, payload)

@router.delete('/admin_posts/{post_id}')
async def delete_post(
        post_id: int = Path(...,description='айди поста'),
        admin_service: AdminService = Depends(get_admin_service)
        )->None:
    await admin_service.admin_delete(post_id)