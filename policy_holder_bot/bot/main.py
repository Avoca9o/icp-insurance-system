from telegram.ext import Application

from config import BOT_TOKEN
from handlers import register_handlers
from utils import logger

def main():
    application =  Application.builder().token(BOT_TOKEN).build()

    register_handlers(application=application)

    logger.info("Bot is running!")
    application.run_polling()


if __name__ == "__main__":
    main()