#!/usr/bin/env bash
set -euo pipefail

# Fresh Telegram Bot Launcher
# Provides foolproof interface for users to interact with the agent system

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is required. Install from https://python-poetry.org/docs/#installation" >&2
  exit 2
fi

# Install dependencies if needed
poetry install --no-interaction --no-root >/dev/null

# Check for required environment variables
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "❌ TELEGRAM_BOT_TOKEN not found in environment"
  echo ""
  echo "To set up the Telegram bot:"
  echo "1. Create a bot with @BotFather on Telegram"
  echo "2. Get your bot token"
  echo "3. Add to .env file:"
  echo "   TELEGRAM_BOT_TOKEN=your_bot_token_here"
  echo ""
  echo "Optional: Restrict access to specific users:"
  echo "   TELEGRAM_AUTHORIZED_USERS=123456789,987654321"
  echo ""
  exit 1
fi

echo "🤖 Starting Fresh Telegram Bot..."
echo "📱 Chat with your bot on Telegram to submit development requests!"
echo ""
echo "Bot Features:"
echo "• Intelligent task analysis by Father agent"
echo "• Automatic agent team deployment" 
echo "• Context-aware from documentation and ADRs"
echo "• Persistent memory across conversations"
echo ""
echo "Commands your users can use:"
echo "• /start - Welcome and introduction"
echo "• /request - Submit development requests"
echo "• /status - Check system status"
echo "• /help - Get detailed help"
echo ""
echo "Press Ctrl+C to stop the bot"
echo "=================================="

# Add python-telegram-bot dependency if not present
if ! poetry show python-telegram-bot >/dev/null 2>&1; then
  echo "📦 Installing Telegram dependencies..."
  poetry add python-telegram-bot
fi

# Run the bot
poetry run python ai/interface/telegram_bot.py
