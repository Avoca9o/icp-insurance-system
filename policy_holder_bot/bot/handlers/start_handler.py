from telegram import Update
from telegram.ext import ContextTypes

from keyboards.authorization_keyboard import get_authorization_keyboard

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name if user.first_name else 'User'

    welcome_message = (
        f'Hello, {user_name}! 👋\n\n'
        'Welcome to our insurance assistant. I will help you find your insurance company, '
        'check the contract, and perform other useful actions. \n\n'
        'Are you ready to start?'
    )

    reply_markup = get_authorization_keyboard()

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
