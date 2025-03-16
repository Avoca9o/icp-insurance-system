from telegram import Update
from telegram.ext import ContextTypes

from clients.db_client import DBClient
from keyboards.action_menu_keyboard import get_action_menu_keyboard

db_client = DBClient()

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    if user:
        message = (
            'Welcome to Main Menu! Here are your available options:\n\n'
            'Choose an action below:'
        )
        reply_markup = get_action_menu_keyboard()
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await query.edit_message_text(
            'You are not authorized yet. Please go through the authorization process first by using /start command.'
        )