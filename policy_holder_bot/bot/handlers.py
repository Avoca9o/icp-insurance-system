import re
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters

from clients import DBClient
from keyboards import get_action_menu_keyboard, get_authorization_keyboard, get_main_menu_keyboard

REQUEST_EMAIL = 0

db_client = DBClient()

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


async def handle_authorize_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Authorization process canceled. If you need help, use /start.')
    return ConversationHandler.END


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


async def approve_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    if not user:
        await query.edit_message_text(
            'You are not authorized or your data is missing. Please authorize again using the /start command'
        )
    elif user.is_approved:
        await query.edit_message_text(
            'Your information is already approved! ✅\n\n'
            'Use the buttton below to return to the main menu.',
            reply_markup=get_main_menu_keyboard()
        )
    else:
        user.is_approved = True
        db_client.update_user_info(user)

        approve_message = (
            'Your information has been successfully approved! ✅\n\n'
            'Use the button below to return to the main menu.'
        )
        reply_markup = get_main_menu_keyboard()

        await query.edit_message_text(approve_message, reply_markup=reply_markup)


async def view_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    if not user:
        await query.edit_message_text(
            'You are not authorized or your data is missing. Please authorize again using the /start command.'
        )
    else:
        insurance_amount = user.insurance_amount
        insurer_id = user.insurer_id
        global_version_num = user.schema_version
        is_approved = '✅ Confirmed' if user.is_approved else '❌ Not confirmed'

        insurance_company = db_client.get_insurance_company_by_id(insurer_id)
        company_name = insurance_company.name if insurance_company else 'Unknown'

        payout_coefficients = 'N/A'
        special_conditions = user.secondary_filters if user.secondary_filters else 'No special conditions.'
        insurer_scheme = db_client.get_insurer_scheme(insurer_id=insurer_id, global_version_num=global_version_num)
        if insurer_scheme and insurer_scheme.diagnoses_coefs:
            payout_coefficients = insurer_scheme.diagnoses_coefs
    
        info_message = (
            f'Insurance amount: 💰 {insurance_amount}\n'
            f'Insurance company: 🏢 {company_name}\n'
            f'Payout coefficients: 📊 {payout_coefficients}\n'
            f'Special conditions: 📝 {special_conditions}\n'
            f'User approval status: {is_approved}'
        )
        reply_markup = get_main_menu_keyboard()

        await query.edit_message_text(info_message, reply_markup=reply_markup)


def register_handlers(application: Application):
    application.add_handler(CommandHandler("start", start_handler))

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_authorize_button, pattern='^authorize$')],
        states={
            REQUEST_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_email)],
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)],
    )

    application.add_handler(conversation_handler)

    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern='^main_menu$'))

    application.add_handler(CallbackQueryHandler(approve_contract_handler, pattern='^approve_contract$'))

    application.add_handler(CallbackQueryHandler(view_contract_handler, pattern='^view_contract$'))
