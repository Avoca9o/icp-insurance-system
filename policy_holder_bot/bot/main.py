import logging
from telegram.ext import Application
from bot.config import get_bot_token
from bot.utils.register_handlers import register_handlers
from bot.utils.logger import logger

def main():
    """Initialize and start the bot."""
    # Build application
    application = Application.builder().token(get_bot_token()).build()

    # Register handlers
    register_handlers(application=application)

    # Start the bot
    logger.info("Bot is running!")
    application.run_polling()


if __name__ == "__main__":
    main()
