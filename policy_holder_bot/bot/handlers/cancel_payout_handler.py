from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.config.prometheus_config import SUCCESS_COUNTER
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard

async def cancel_payout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_menu_keyboard()
    await update.message.reply_text('Payout request process canceled.', reply_markup=reply_markup)
    SUCCESS_COUNTER.inc()
    return ConversationHandler.END