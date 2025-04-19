#!/bin/bash

# Stop the service if it exists
if systemctl is-active --quiet honeypot-bot; then
    systemctl stop honeypot-bot
    systemctl disable honeypot-bot
fi

# Install Python 3.12 if not already installed
if ! command -v python3.12 &> /dev/null; then
    dnf install -y python3.12
fi

# Install pip if not already installed
if ! command -v pip3 &> /dev/null; then
    dnf install -y python3-pip
fi

# Create project directory
mkdir -p /opt/honeypot-bot 