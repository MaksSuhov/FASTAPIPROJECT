import asyncio
import json
import token
from typing import AsyncIterator

from pydantic.dataclasses import dataclass
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from mcp.client.sse import sse_client
from mcp import ClientSession

from app.config.config import DEFAULT_MODEL
from app.mcp_client import convert_mcp_tools_to_openai, openai_client
from app.repositories.chatrepository import ChatRepository
from app.services.OpenAIChatGateway import OpenAIChatGateway
from app.services.PromptBuilder import PromptBuilder


@dataclass
class ChatEvent:
    name: str
    data: dict


class ConversationNotFound(Exception):
    pass


class LlmUnavailableError(Exception):
    pass


class ChatService:
    def __init__(self,
                 chat_repository: ChatRepository,
                 llm: OpenAIChatGateway,
                 prompt_builder: PromptBuilder):
        self.chat_repository = chat_repository
        self.llm = llm
        self.prompt_builder = prompt_builder

    async def stream_reply(self, conversation_id: int | None, payload: str, user_id: int) -> AsyncIterator[ChatEvent]:
        is_new = conversation_id is None

        if is_new:
            conversation = await self.chat_repository.create_new_conversation(user_id=user_id)
        else:
            conversation = await self.chat_repository.get_owned_conversation(conversation_id, user_id)

            if conversation is None:
                raise ConversationNotFound()

        await self.chat_repository.add_message(
            conversation.conversation_id,
            'user',
            payload)
        await self.chat_repository.commit()

        history = await self.chat_repository.get_recent_message(conversation.conversation_id)
        messages = self.prompt_builder.build_llm_messages(history, user_id=user_id)

        assistant_parts: list[str] = []

        if is_new:
            yield ChatEvent('conversation', {'conversation_id': conversation.conversation_id})
        try:
            async with sse_client("http://127.0.0.1:8001/sse") as (read, write):
                async with ClientSession(read, write) as mcp_session:
                    await mcp_session.initialize()

                    mcp_tools = await mcp_session.list_tools()
                    openai_tools = convert_mcp_tools_to_openai(mcp_tools.tools)

                    current_user_tools = {"mcp_create_post",'update_my_post', 'get_my_profile'}

                    for tool in openai_tools:
                        if tool["function"]["name"] not in current_user_tools:
                            continue

                        parameters = tool["function"]["parameters"]
                        parameters["properties"].pop("user_id", None)
                        parameters["required"] = [
                            argument
                            for argument in parameters.get("required", [])
                            if argument != "user_id"
                        ]

                    built_tool_calls = {}

                    async for chunk in self.llm.stream(messages, tools=openai_tools):
                        if chunk["type"] == "token":
                            token_text = chunk["text"]
                            assistant_parts.append(token_text)
                            yield ChatEvent("token", {"text": token_text})
                        elif chunk["type"] == "tool_call_delta":
                            for tool_call in chunk["tool_calls"]:
                                idx = tool_call.index
                                if idx not in built_tool_calls:
                                    built_tool_calls[idx] = {
                                        "id": tool_call.id,
                                        "name": tool_call.function.name,
                                        "arguments": ""
                                    }
                                if tool_call.function.arguments:
                                    built_tool_calls[idx]["arguments"] += tool_call.function.arguments

                    if built_tool_calls:
                        yield ChatEvent("token", {"text": "\n*Запрашиваю данные из БД...*\n"})

                        openai_assistant_tool_calls = []
                        tool_results_messages = []

                        for idx, tool_data in built_tool_calls.items():
                            tool_name = tool_data["name"]
                            tool_args = json.loads(
                                tool_data["arguments"]) if tool_data["arguments"] else {}

                            if tool_name in current_user_tools:
                                tool_args["user_id"] = user_id

                            mcp_result = await mcp_session.call_tool(tool_name, arguments=tool_args)

                            openai_assistant_tool_calls.append({
                                "id": tool_data["id"],
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_data["arguments"]
                                }
                            })

                            tool_results_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_data["id"],
                                "name": tool_name,
                                "content": mcp_result.content[0].text if isinstance(mcp_result.content, list) else mcp_result.content.text
                            })

                        messages.append({
                            "role": "assistant",
                            "tool_calls": openai_assistant_tool_calls
                        })
                        messages.extend(tool_results_messages)

                        async for chunk in self.llm.stream(messages):
                            if chunk["type"] == "token":
                                token_text = chunk["text"]
                                assistant_parts.append(token_text)
                                yield ChatEvent("token", {"text": token_text})
                                
            answer = "".join(assistant_parts).strip()

            if answer:
                await self.chat_repository.add_message(
                    conversation.conversation_id,
                    role='assistant',
                    content=answer)
                await self.chat_repository.commit()

            yield ChatEvent('done',{})

        except asyncio.CancelledError:
            raise

        except LlmUnavailableError:
            yield ChatEvent("error", {"message": "Сервис генерации недоступен."})

        except SQLAlchemyError:
            await self.chat_repository.rollback()
            yield ChatEvent("error", {"message": "Не удалось сохранить ответ."})

    def sse(self, event: str, data: dict) -> str:
        return (
            f"event: {event}\n"
            f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        )
