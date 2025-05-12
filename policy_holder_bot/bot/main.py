from prometheus_client import start_http_server
from telegram.ext import Application

from bot.config.bot_config import BOT_TOKEN
from bot.utils.logger import logger
from bot.utils.register_handlers import register_handlers

def main():
    application =  Application.builder().token(BOT_TOKEN).build()

    register_handlers(application=application)

    logger.info("Bot is running!")
    start_http_server(8005)
    application.run_polling()


if __name__ == "__main__":
    main()