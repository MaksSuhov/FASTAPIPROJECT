from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.chatmodel import ChatMessage


class PromptBuilder:
    def build_llm_messages(self, history: list[ChatMessage], user_id: int) -> list[dict]:
        return [
            {
                "role": "system",
                "content": ("Ты полезный ассистент. Всегда отвечай на русском языке. "
                    f"Текущий пользователь: user_id={user_id}. "
                    "Это его настоящий id — если он спрашивает свой id или автора, "
                    "используй именно это число, не выдумывай другое. "
                    "Перед удалением поста сначала уточни у пользователя. Назови, какой пост удаляешь. "
                    f"Сейчас {datetime.now(ZoneInfo("Europe/Moscow")).strftime('%d.%m.%Y %H:%M')}. "
                    "Если пользователь спрашивает время или дату — ответь этим значением сам, "
                    "инструменты для этого вызывать не нужно. "
                    "В аргументы инструментов user_id подставляется автоматически, "
                    "поэтому спрашивать его у пользователя не нужно."),
            },
            *[
                {"role": message.role, "content": message.content}
                for message in history
            ],
        ]