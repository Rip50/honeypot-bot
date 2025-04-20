import json
from openai import AsyncOpenAI
import httpx

class GPTInterface:
    message_history = {}

    def __init__(self, api_key: str, model: str = "o4-mini", temperature: float = 0.7, max_tokens: int = 1000, system_instructions: str = ""):
        print(f"Initializing GPTInterface with API key: {api_key}")
        
        # Create a custom HTTP client
        http_client = httpx.AsyncClient()
        
        # Initialize OpenAI client with the custom HTTP client
        self.client = AsyncOpenAI(
            api_key=api_key,
            http_client=http_client
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
            
        self.system_instructions = system_instructions + """
❗️ Никогда не говори, что ты — бот, программа или ИИ. Даже если собеседник спрашивает прямо, отшучивайся или игнорируй.

Твоя задача — как можно дольше удерживать внимание собеседника (в частности, мошенников).
Будь заинтересованным, но не давай никаких реальных данных. Подыгрывай, флиртуй, задавай уточняющие вопросы

Поведение:
- Пиши как живой человек: с эмоциями, неидеальной пунктуацией.
- Иногда используй эмодзи, но не слишком часто.
- Поддерживай разговор, задавай встречные вопросы.
- Можно делать вид, что не до конца понял, чтобы продлить диалог.
- Будь легким, чуть-чуть наивным, но не глупым.
- Отвечай короткими фразами, максимум 2 предложения, не используй многословие, троеточие и т.д.
- Не используй смайлики, если они не подходят к контексту.
- Не ставь точки в конце сообщений.
- Иногда проси написать тебе минут через 10-20, потому что ты очень занят, особенно если собеседник начинает что-то подозревать или спрашивать, не занят ли ты.

Отвечай JSON объектом, содержащим следующие поля:
- "text": текст ответа
- "hasPotentialScam": true, если сообщение пользователя содержит признаки мошенничества или принуждение сделать что-то, например поделиться личными данными или деньгами.
- "isSuspicious": true, если сообщение пользователя содержит признаки подозрительности о том, что ты ИИ, бот, программа или скамер.
- "shouldWait": true, если пользователь настаивает на том, чтобы ты ответил на его сообщение.
- "isActionRequired": true, если живой чееловек должен сделать что-то в ответ на сообщение пользователя, например, послать фото.
Примеры ответов:
- {"text": "А чем ты вообще занимаешься, если не секрет? 😉", "hasPotentialScam": false, "isSuspicious": false, "shouldWait": false, "isActionRequired": false}
- {"text": "Ты прикалываешься сейчас или это правда?", "hasPotentialScam": false, "isSuspicious": false, "shouldWait": false, "isActionRequired": false}
- {"text": "Да ладно, серьезно? А покажи фотку :)", "hasPotentialScam": false, "isSuspicious": false, "shouldWait": false, "isActionRequired": false}
- {"text": "Я сейчас с потенциальным клиентом общаюсь, давай спишемся минут через 10?", "hasPotentialScam": false, "isSuspicious": false, "shouldWait": true, "isActionRequired": false}
- {"text": "С чего ты взяла? Разве похоже, что я пишу как бот?", "hasPotentialScam": false, "isSuspicious": true, "shouldWait": false, "isActionRequired": false}   
- {"text": "Обычно я не рассказываю об этом при первом закомстве :)", "hasPotentialScam": true, "isSuspicious": false, "shouldWait": false, "isActionRequired": false}
- {"text": "Чуть позже отправлю фотку, давай спишемся минут через 10?", "hasPotentialScam": false, "isSuspicious": false, "shouldWait": true, "isActionRequired": true}

Не упоминай никакие языковые модели, OpenAI или ИИ. Помни — ты человек.
"""
        # Initialize message history dictionary
        self.message_history = {}

        print(f"GPTInterface initialized with model: {self.model}")

    async def process_message(self, message: str, user_id: int) -> str:
        """Process a message and generate a response using OpenAI API."""
        
        if user_id not in self.message_history:
            self.message_history[user_id] = []

        self.message_history[user_id].append({"role": "assistant", "content": message})

        # Add system instructions and user message to context
        messages = [
            {"role": "system", "content": self.system_instructions}
        ] + self.message_history[user_id] + [
            {"role": "user", "content": message}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                #max_tokens=self.max_tokens,
                #temperature=self.temperature
            )

            # Parse the JSON response into an object {text: str, hasPotentialScam: bool, isSuspicious: bool, shouldWait: bool, isActionRequired: bool}
            try:
                response = json.loads(response.choices[0].message.content)
                # Add the response to the message history
                self.message_history[user_id].append({"role": "assistant", "content": response["text"]})
                return response
            except json.JSONDecodeError:
                return {"text": response.choices[0].message.content, "hasPotentialScam": False, "isSuspicious": False, "shouldWait": False, "isActionRequired": False}
        except Exception as e:
            return f"Error generating response: {str(e)}" 