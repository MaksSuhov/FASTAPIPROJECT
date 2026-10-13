from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependences import get_chat_service
from app.database.database import get_db
from app.models.authmodel import User
from app.models.chatmodel import Conversation, ChatMessage
from app.models.postmodel import Post
from app.repositories.chatrepository import ChatRepository
from app.schemas.ChatSchema import ChatRequest, ConversationSchema
from app.schemas.postschemas import PostSchema, PostUpdateSchema
from app.services.CredService import CredService
from app.services.chatservice import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])



@router.post("/stream")
async def stream_chat(
    payload: ChatRequest,
    current_user: User = Depends(CredService.get_current_user),
    chat_service: ChatService =Depends(get_chat_service),
):

    async def event_stream():
        async for event in chat_service.stream_reply(conversation_id=payload.conversation_id,
                                                     user_id=current_user.user_id,
                                                     payload=payload.content):
            yield chat_service.sse(event.name, event.data)

    return StreamingResponse(
         event_stream(),
         media_type="text/event-stream",
         headers={
            "Cache-Control": "no-cache",
             "X-Accel-Buffering": "no",
         },
     )


@router.get('/conversations', response_model=list[ConversationSchema])
async def get_my_conversations(current_user: User = Depends(CredService.get_current_user),
                               db:AsyncSession = Depends(get_db)
                               )->list[Conversation]:
    repository = ChatRepository(db)
    return await repository.get_all(current_user.user_id)

@router.delete('/conversations/{conversation_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_conversation(
    conversation_id: int = Path(..., detail='айди поста'),
    current_user: User = Depends(CredService.get_current_user),
    chat_service: ChatService =Depends(get_chat_service)
    )->None:
    return await chat_service.delete_conversation(conversation_id=conversation_id, user_id=current_user.user_id)