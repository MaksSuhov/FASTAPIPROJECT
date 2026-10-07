"""
Клиент для взаимодействия с MCP сервером погоды через OpenAI GPT-4o-mini
"""
import sys
import os
import asyncio
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config.config import ROUTERAI_API_KEY, ROUTERAI_BASE_URL



openai_client = AsyncOpenAI(
    api_key=ROUTERAI_API_KEY,
    base_url=ROUTERAI_BASE_URL
)

def is_valid_utf8(text: str) -> bool:
    try:
        text.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False

async def main():
    """
    Основная функция для запуска клиента
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.server_MCP"],
        env=None,
    )

    print("🚀 Запуск MCP клиента...")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("✅ Подключено к MCP серверу")
            print("=" * 60)

            tools_list = await session.list_tools()
            print(f"\n📋 Доступные инструменты ({len(tools_list.tools)}):")
            for tool in tools_list.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            openai_tools = convert_mcp_tools_to_openai(tools_list.tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "Ты полезный ассистент, который помогает пользователям "
                        " У тебя есть доступ к инструментам."
                        "Всегда отвечай на русском языке."
                    )
                }
            ]

            print("💬 Чат запущен! Спрашивайте о погоде (введите 'выход' для завершения)")
            print("=" * 60)

            while True:
                user_input = input("\n👤 Вы: ").strip()

                if not is_valid_utf8(user_input):
                    print("❌ В сообщении повреждён символ UTF-8. Введите сообщение ещё раз.")
                    continue

                if user_input.lower() in ["выход", "exit", "quit", "q"]:
                    print("\n👋 До свидания!")
                    break

                if not user_input:
                    continue

                messages.append({
                    "role": "user",
                    "content": user_input
                })

                final_response = await process_conversation(
                    messages,
                    openai_tools,
                    session
                )

                print(f"\n🤖 Ассистент: {final_response}")


async def process_conversation(messages: list, tools: list, session: ClientSession) -> str:
    """
    Обрабатывает разговор с возможными вызовами инструментов

    Args:
        messages: История сообщений
        tools: Список инструментов в формате OpenAI
        session: Сессия MCP клиента

    Returns:
        Финальный ответ ассистента
    """
    max_iterations = 5

    for iteration in range(max_iterations):
        response = openai_client.chat.completions.create(
            model=os.getenv("DEFAULT_MODEL", "qwen/qwen3.7-flash"),  # Используем модель gpt-4o-mini
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": assistant_message.tool_calls
        })

        if not assistant_message.tool_calls:
            return assistant_message.content or "Извините, я не смог сформировать ответ."

        print("\n⚙️ Вызов инструментов...")

        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"  🔧 {function_name}({', '.join(f'{k}={v}' for k, v in function_args.items())})")

            try:
                result = await session.call_tool(function_name, function_args)

                if result.content:
                    tool_result = result.content[0].text if result.content else "Нет результата"

                else:
                    tool_result = "Инструмент выполнен, но результат пуст"

            except Exception as e:
                tool_result = f"Ошибка при вызове инструмента: {str(e)}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

    return "Извините, обработка заняла слишком много времени."


def convert_mcp_tools_to_openai(mcp_tools) -> list:
    """
    Конвертирует MCP инструменты в формат OpenAI

    Args:
        mcp_tools: Список инструментов от MCP сервера

    Returns:
        Список инструментов в формате OpenAI
    """
    openai_tools = []

    for tool in mcp_tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "Инструмент без описания",
                "parameters": tool.input_schema
            }
        }
        openai_tools.append(openai_tool)

    return openai_tools


if __name__ == "__main__":
     try:
        asyncio.run(main())
     except BaseException as e:
         traceback.print_exception(e)
