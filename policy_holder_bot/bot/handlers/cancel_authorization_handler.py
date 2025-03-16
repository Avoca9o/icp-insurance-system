from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel_authorization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Authorization process canceled. If you need help, use /start.')
    return ConversationHandler.END
