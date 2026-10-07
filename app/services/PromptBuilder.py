from app.models.chatmodel import ChatMessage


class PromptBuilder:
    def build_llm_messages(self, history: list[ChatMessage]) -> list[dict]:
        return [
            {
                "role": "system",
                "content": "Ты полезный ассистент. Всегда отвечай на русском языке.",
            },
            *[
                {"role": message.role, "content": message.content}
                for message in history
            ],
        ]