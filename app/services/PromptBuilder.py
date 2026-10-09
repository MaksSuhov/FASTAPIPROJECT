from app.models.chatmodel import ChatMessage


class PromptBuilder:
    def build_llm_messages(self, history: list[ChatMessage], user_id: int) -> list[dict]:
        return [
            {
                "role": "system",
                "content": ("Ты полезный ассистент. Всегда отвечай на русском языке."
                    f"Текущий пользователь: user_id={user_id}. "
                    "Это его настоящий id — если он спрашивает свой id или автора, "
                    "используй именно это число, не выдумывай другое. "
                    "В аргументы инструментов user_id подставляется автоматически, "
                    "поэтому спрашивать его у пользователя не нужно."),
            },
            *[
                {"role": message.role, "content": message.content}
                for message in history
            ],
        ]