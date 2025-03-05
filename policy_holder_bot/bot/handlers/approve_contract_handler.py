from telegram import Update
from telegram.ext import ContextTypes

from clients.db_client import DBClient
from keyboards.main_menu_keyboard import get_main_menu_keyboard

db_client = DBClient()

async def approve_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    reply_markup = get_main_menu_keyboard()

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    if not user:
        await query.edit_message_text(
            'You are not authorized or your data is missing. Please authorize again using the /start command'
        )
    elif user.is_approved:
        await query.edit_message_text(
            'Your information is already approved! ✅\n\n'
            'Use the buttton below to return to the main menu.',
            reply_markup=reply_markup,
        )
    else:
        user.is_approved = True
        db_client.update_user_info(user)

        approve_message = (
            'Your information has been successfully approved! ✅\n\n'
            'Use the button below to return to the main menu.'
        )

        await query.edit_message_text(approve_message, reply_markup=reply_markup)