from typing import Dict, List
from datetime import datetime
import asyncio

class MessageBuffer:
    def __init__(self, buffer_timeout: int = 5):
        self.buffer_timeout = buffer_timeout
        self.message_buffers: Dict[int, List[str]] = {}
        self.last_processing: Dict[int, datetime] = {}
        self.timers: Dict[int, asyncio.Task] = {}

    def add_message(self, user_id: int, message: str):
        """Add a message to the buffer for a specific user and restart the timer."""
        if user_id not in self.message_buffers:
            self.message_buffers[user_id] = []
            self.last_processing[user_id] = datetime.now()
        
        self.message_buffers[user_id].append(message)
        
        # Cancel existing timer if any
        if user_id in self.timers:
            self.timers[user_id].cancel()
        
        # Start new timer
        self.timers[user_id] = asyncio.create_task(self._wait_timeout(user_id))

    async def _wait_timeout(self, user_id: int):
        """Wait for timeout and return buffered messages."""
        await asyncio.sleep(self.buffer_timeout)
        if user_id in self.message_buffers and self.message_buffers[user_id]:
            return self.process_buffered_messages(user_id)
        return None

    def process_buffered_messages(self, user_id: int) -> str:
        """Process all buffered messages for a user."""
        if user_id not in self.message_buffers or not self.message_buffers[user_id]:
            return None
        
        # Combine all messages in buffer
        combined_message = "\n".join(self.message_buffers[user_id])
        self.message_buffers[user_id] = []
        self.last_processing[user_id] = datetime.now()
        
        return combined_message

    def get_time_since_last(self, user_id: int) -> float:
        """Get time in seconds since last processing for a user."""
        if user_id not in self.last_processing:
            return float('inf')
        return (datetime.now() - self.last_processing[user_id]).total_seconds() 