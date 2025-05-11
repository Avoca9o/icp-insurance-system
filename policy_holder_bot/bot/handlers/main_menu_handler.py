from telegram import Update
from telegram.ext import ContextTypes

from bot.clients.db_client import DBClient
from bot.config.prometheus_config import FAILURE_COUNTER, SUCCESS_COUNTER
from bot.keyboards.action_menu_keyboard import get_action_menu_keyboard
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.utils.logger import logger

db_client = DBClient()

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id
    try:
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
        SUCCESS_COUNTER.inc()
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while main menu action: {str(e)}')
        await query.edit_message_text('Error while main menu action. Try again later', reply_markup=get_main_menu_keyboard)