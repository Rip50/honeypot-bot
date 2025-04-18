# HoneyPot Telegram Userbot

A Telegram userbot that uses OpenAI's GPT models to generate responses to messages. The bot maintains conversation history and uses message buffering to optimize API usage.

## Features

- Uses Telethon to run as a Telegram user (not a bot)
- Maintains conversation history using SQLite
- Implements message buffering to reduce API calls
- Uses OpenAI's GPT models for response generation
- Excludes group chats from processing
- Automatically cleans up old messages

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `config.json` file with the following structure:
```json
{
    "telegram": {
        "api_id": "YOUR_API_ID",
        "api_hash": "YOUR_API_HASH",
        "session_name": "honeypot_bot"
    },
    "openai": {
        "api_key": "YOUR_OPENAI_API_KEY",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "message_buffering": {
        "buffer_timeout": 5,
        "max_buffer_size": 5
    },
    "database": {
        "db_path": "messages.db",
        "cleanup_days": 7,
        "max_history_messages": 10
    }
}
```

3. Get your Telegram API credentials:
   - Go to https://my.telegram.org
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application to get your API ID and API Hash

4. Get your OpenAI API key:
   - Go to https://platform.openai.com
   - Create an account or log in
   - Generate an API key

## Usage

1. Run the bot:
```bash
python main.py
```

2. On first run, you'll need to authenticate with Telegram by entering your phone number and the verification code sent to your Telegram account.

3. The bot will now listen for incoming messages and respond using the configured GPT model.

## Configuration

The bot can be configured by modifying the `config.json` file:

- `telegram`: Telegram API credentials and session settings
- `openai`: OpenAI API settings including model selection and generation parameters
- `message_buffering`: Settings for message buffering to optimize API usage
- `database`: Database settings including cleanup and history limits

## Notes

- The bot runs as a user account, not a bot account
- It will only respond to private messages, not group chats
- Message history is stored locally in an SQLite database
- API keys and credentials should be kept secure and never shared 