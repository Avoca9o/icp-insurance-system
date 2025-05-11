from telegram import Update
from telegram.ext import ContextTypes

from bot.config.prometheus_config import SUCCESS_COUNTER

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SUCCESS_COUNTER.inc()
    await update.message.reply_text('Contact your insurance company for help.')
