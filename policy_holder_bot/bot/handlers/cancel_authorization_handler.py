from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config.prometheus_config import SUCCESS_COUNTER

async def cancel_authorization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Authorization process canceled. If you need help, use /start.')
    SUCCESS_COUNTER.inc()
    return ConversationHandler.END
