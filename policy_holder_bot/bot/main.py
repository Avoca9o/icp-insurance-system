from telegram.ext import Application

from config.bot_config import BOT_TOKEN
from utils.register_handlers import logger, register_handlers

def main():
    application =  Application.builder().token(BOT_TOKEN).build()

    register_handlers(application=application)

    logger.info("Bot is running!")
    application.run_polling()


if __name__ == "__main__":
    main()