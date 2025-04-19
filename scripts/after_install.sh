#!/bin/bash

# Create virtual environment
python3.12 -m venv /opt/honeypot-bot/venv
source /opt/honeypot-bot/venv/bin/activate

# Install dependencies
pip install -r /opt/honeypot-bot/requirements.txt

# Create systemd service
cat > /etc/systemd/system/honeypot-bot.service << 'SERVICE'
[Unit]
Description=HoneyPot Telegram Bot
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/honeypot-bot
Environment="PATH=/opt/honeypot-bot/venv/bin"
ExecStart=/opt/honeypot-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Reload systemd
systemctl daemon-reload

# Start the service
systemctl enable honeypot-bot
systemctl start honeypot-bot 