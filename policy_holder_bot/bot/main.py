import logging
from random import randint
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import handlers
from config import BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.echo_message))
    application.add_handler(CommandHandler("help", handlers.help_command))

    logger.info("Bot is running!")
    application.run_polling()


if __name__ == "__main__":
    main()