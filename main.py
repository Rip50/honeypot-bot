from datetime import datetime
import os
import asyncio
import json
from telethon import TelegramClient, events
from telethon.tl.types import User
# from db import Database
from gpt_interface import GPTInterface
from message_buffer import MessageBuffer

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    API_ID = int(config['telegram']['api_id'])
    API_HASH = config['telegram']['api_hash']
    OPENAI_API_KEY = config['openai']['api_key']
    SESSION_NAME = config['telegram']['session_name']
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
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.client.send_message('me', 'Hello, myself!')

        # self.db = Database(config['database']['db_path'])
        self.gpt = GPTInterface(
            api_key=OPENAI_API_KEY,
            model=config['openai']['model']
        )
        self.message_buffer = MessageBuffer(
            buffer_timeout=config['message_buffering']['buffer_timeout']
        )
        
        # Register event handlers
        self.client.on(events.NewMessage(incoming=True))(self.handle_message)

    async def start(self):
        """Initialize and start the bot."""
        # await self.db.init_db()
        await self.client.start()
        print("Bot started successfully!")
        await self.client.run_until_disconnected()

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

            # Add message to buffer and get the timer task
            self.message_buffer.add_message(user_id, message)
            timer_task = self.message_buffer.timers[user_id]
            
            # Wait for the timer to complete
            buffered_message = await timer_task
            
            if buffered_message:
                # Generate response without context
                response = await self.gpt.process_message(buffered_message)
                
                # Send response
                await self.client.send_message(user_id, response)

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