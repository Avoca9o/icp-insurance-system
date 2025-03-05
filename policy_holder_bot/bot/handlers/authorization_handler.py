import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from clients.db_client import DBClient
from keyboards.main_menu_keyboard import get_main_menu_keyboard

db_client = DBClient()

REQUEST_EMAIL = 0

async def authorization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text('Please, enter your email address for authorization:')
    return REQUEST_EMAIL

async def request_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        await update.message.reply_text('The email you entered is not valid. Please try again.')
        return REQUEST_EMAIL

    user = db_client.get_user_by_email(email)
    if user:
        telegram_id = update.effective_user.id
        user.telegram_id = telegram_id
        db_client.update_user_info(user)
        
        welcome_message = (
            f'Authorization successful! 🎉 Your account is now linked to Telegram.\n\n'
            f'Welcome!!! You can go to main actions.'
        )
        reply_markup = get_main_menu_keyboard()

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            'No user was found with this email. Please try again with a different email or contact support.'
        )
        return REQUEST_EMAIL