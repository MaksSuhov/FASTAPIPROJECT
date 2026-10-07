from typing import Any, AsyncIterator

from app.config.config import DEFAULT_MODEL
from app.mcp_client import openai_client


class OpenAIChatGateway:
    async def stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        request = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "stream": True,
            "extra_body": {"reasoning": {"enabled": False}},
        }

        if tools:
            request["tools"] = tools
            request["tool_choice"] = "auto"

        stream = await openai_client.chat.completions.create(**request)

        async for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                yield {"type": "token", "text": delta.content}

            if delta.tool_calls:
                yield {
                    "type": "tool_call_delta",
                    "tool_calls": delta.tool_calls,
                }