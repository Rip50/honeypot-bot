import os
import asyncio
import json
import random
import time
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction
from telethon.tl.types import User
# from db import Database
from gpt_interface import GPTInterface
from message_buffer import MessageBuffer

"""
TODO:
- Add logging
- Diferentiate btw users
"""

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    API_ID = int(config['telegram']['api_id'])
    API_HASH = config['telegram']['api_hash']
    OPENAI_API_KEY = config['openai']['api_key']
    
    # Create sessions directory if it doesn't exist
    SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sessions')
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    SESSION_NAME = os.path.join(SESSIONS_DIR, config['telegram']['session_name'])
    
except FileNotFoundError:
    print("Error: config.json not found in project root")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON in config.json")
    exit(1)
except KeyError as e:
    print(f"Error: Missing required configuration key: {e}")
    exit(1)

class HoneyPotBot:
    def __init__(self):
        self.telegram_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

        # self.db = Database(config['database']['db_path'])
        self.gpt = GPTInterface(
            api_key=OPENAI_API_KEY,
            model=config['openai']['model'],
            temperature=config['openai']['temperature'],
            max_tokens=config['openai']['max_tokens']
        )
        self.message_buffer = MessageBuffer(
            buffer_timeout=config['message_buffering']['buffer_timeout']
        )
        
        # Register event handlers
        self.telegram_client.on(events.NewMessage(incoming=True))(self.handle_message)

    async def log_response(self, message):
        # Send message to me
        await self.telegram_client.send_message("me", message)
        print(message)

    async def start(self):
        """Initialize and start the bot."""
        # await self.db.init_db()
        await self.telegram_client.start()
        print("Honeypot bot started successfully!")
        await self.telegram_client.run_until_disconnected()

    async def handle_message(self, event):
        """Handle incoming messages."""
        try:
            # Skip if no chat or not a user chat
            if not event.is_private:
                return

            user_id = event.chat_id
            message = event.message.text

            # Skip if no message text
            if not message:
                return
            
            time.sleep(random.randint(1, 3))

            # Acknowledge the message
            await event.client.send_read_acknowledge(event.chat_id)
            
            # Send typing action
            await event.client(SetTypingRequest(
                peer=event.chat_id,
                action=SendMessageTypingAction()
            ))
            
            # Add message to buffer and get the timer task
            self.message_buffer.add_message(user_id, message)
            timer_task = self.message_buffer.timers[user_id]
            
            # Wait for the timer to complete
            buffered_message = await timer_task
            
            if buffered_message:
                # Send typing action
                await event.client(SetTypingRequest(
                    peer=event.chat_id,
                    action=SendMessageTypingAction()
                ))

                # Generate response without context
                response = await self.gpt.process_message(buffered_message, user_id)

                # Parse the response
                response_text = response['text']
                has_potential_scam = response['hasPotentialScam']
                is_suspicious = response['isSuspicious']
                should_wait = response['shouldWait']
                is_action_required = response['isActionRequired']

                if is_suspicious:
                    await self.log_response(f"User {user_id} sent suspicious message: {buffered_message}")
                elif has_potential_scam:
                    await self.log_response(f"User {user_id} sent potential scam message: {buffered_message}")
                elif should_wait:
                    await self.log_response(f"User {user_id} should wait: {buffered_message}")  
                elif is_action_required:
                    await self.log_response(f"User {user_id} is waiting for an action: {buffered_message}")
                
                # Send response
                await self.telegram_client.send_message(user_id, response_text)

        except Exception as e:
            print(f"Error handling message: {str(e)}")
            # Don't re-raise the exception to prevent bot from crashing

    # async def cleanup(self):
    #     """Cleanup old messages from database."""
    #     while True:
    #         await self.db.cleanup_old_messages(config['database']['cleanup_days'])
    #         await asyncio.sleep(86400)  # Run once per day

async def main():
    bot = HoneyPotBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main()) 