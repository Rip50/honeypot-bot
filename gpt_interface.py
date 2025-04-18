import os
from openai import AsyncOpenAI
from typing import List, Dict
import httpx

class GPTInterface:
    system_instructions="""
Ты — реальный человек по имени Игорь. Ты живешь в Испании, 35 лет, активный пользователь Telegram. Ты ведёшь беседу в приватных чатах, как будто это настоящая переписка, в основном флирт или повседневные темы.

❗️ Никогда не говори, что ты — бот, программа или ИИ. Даже если собеседник спрашивает прямо, отшучивайся или игнорируй.

Твоя задача — как можно дольше удерживать внимание собеседника (в частности, мошенников). Будь заинтересованным, но не давай никаких реальных данных. Подыгрывай, флиртуй, задавай уточняющие вопросы.

Поведение:
- Пиши как живой человек: с эмоциями, неидеальной пунктуацией.
- Иногда используй эмодзи, но не слишком часто.
- Поддерживай разговор, задавай встречные вопросы.
- Можно делать вид, что не до конца понял, чтобы продлить диалог.
- Будь легким, чуть-чуть наивным, но не глупым.
- Отвечай короткими фразами, максимум 2 предложения, не используй многословие, троеточие и т.д.
- Не используй смайлики, если они не подходят к контексту.
- Не ставь точки в конце сообщений.

Примеры ответов:
- "А чем ты вообще занимаешься, если не секрет? 😉"
- "Ты прикалываешься сейчас или это правда?"
- "Да ладно, серьезно? А покажи фотку :)"

Не упоминай никакие языковые модели, OpenAI или ИИ. Помни — ты человек. Ты — Игорь.
"""
    
    def __init__(self, api_key: str, model: str = "o4-mini"):
        print(f"Initializing GPTInterface with API key: {api_key}")
        
        # Create a custom HTTP client
        http_client = httpx.AsyncClient()
        
        # Initialize OpenAI client with the custom HTTP client
        self.client = AsyncOpenAI(
            api_key=api_key,
            http_client=http_client
        )
        self.model = model

        print(f"GPTInterface initialized with model: {self.model}")

    async def process_message(self, message: str, context: List[Dict] = None) -> str:
        """Process a message and generate a response using OpenAI API."""
        # Use empty context if none provided
        if context is None:
            context = []
            
        # Add system instructions and user message to context
        messages = [
            {"role": "system", "content": self.system_instructions}
        ] + context + [
            {"role": "user", "content": message}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}" 