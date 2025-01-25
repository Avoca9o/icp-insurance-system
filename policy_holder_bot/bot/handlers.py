import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters

from clients import DBClient, ICPClient
from keyboards import get_action_menu_keyboard, get_authorization_keyboard, get_main_menu_keyboard
from utils import logger, validate_policy_number, validate_trauma_code

REQUEST_EMAIL = 0
REQUEST_INSURANCE_POLICY, REQUEST_TRAUMA_CODE, REQUEST_TRAUMA_TIME, REQUEST_CRYPTO_WALLET = range(4)

db_client = DBClient()
icp_client = ICPClient()

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


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_path = os.path.join('media', 'help_video_extra.mp4')

    try:
        await update.message.reply_video(
            video=open(video_path, 'rb'),
            caption='Here is a help video. 🎥 If you have further questions, let us know!',
        )
    except Exception as e:
        logger.error(f'Failed to send help video: {e}')
        await update.message.reply_text('Sorry, I could not send the help video. Please try again later.')


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


async def request_payout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id
    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    if not user:
        await query.edit_message_text(
            'You are not authorized. Please authorize using the /start command.'
        )
        return ConversationHandler.END
    
    if not user.is_approved:
        await query.edit_message_text(
            'Your contract information is not approved yet. Please confirm your information before requesting a payout.'
        )
        return ConversationHandler.END
    
    await query.edit_message_text('Please enter your insurance policy number:')
    return REQUEST_INSURANCE_POLICY


async def request_insurance_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    policy_number = update.message.text

    if not validate_policy_number(policy_number=policy_number):
        await update.message.reply_text(
            'Invalid insurance policy number. Try again:'
        )
        return REQUEST_INSURANCE_POLICY
    
    context.user_data['policy_number'] = policy_number

    await update.message.reply_text('Please enter the trauma code:')
    return REQUEST_TRAUMA_CODE


async def request_trauma_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trauma_code = update.message.text

    if not validate_trauma_code(trauma_code=trauma_code):
        await update.message.reply_text(
            'Invalid trauma code. Try again using this source: https://www.cito-priorov.ru/cito/files/telemed/Perechen_kodov_MKB.pdf'
        )
        return REQUEST_TRAUMA_CODE

    context.user_data['trauma_code'] = trauma_code

    await update.message.reply_text('Please enter the registration time of the trauma (YYYY-MM-DD HH:MM):')
    return REQUEST_TRAUMA_TIME


async def request_trauma_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trauma_time = update.message.text

    try:
        trauma_time = datetime.strptime(trauma_time, '%Y-%m-%d %H:%M')
    except ValueError:
        await update.message.reply_text(
            'Invalid date format. Please use the format YYYY-MM-DD HH:MM'
        )
        return REQUEST_TRAUMA_TIME

    context.user_data['trauma_time'] = trauma_time

    await update.message.reply_text('Please enter the cryptowallet address principal:')
    return REQUEST_CRYPTO_WALLET


async def request_crypto_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto_wallet = update.message.text

    context.user_data['crypto_wallet'] = crypto_wallet

    await update.message.reply_text('Processing payout request. Please wait...')
    return await process_payout(update, context)


async def process_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    policy_number = context.user_data['policy_number']
    trauma_code = context.user_data['trauma_code']
    trauma_time = context.user_data['trauma_time']
    crypto_wallet = context.user_data['crypto_wallet']

    try:
        is_valid = icp_client.payout_request(
            policy_number=policy_number,
            trauma_code=trauma_code,
            trauma_time=trauma_time,
            crypto_wallet=crypto_wallet,
        )

        reply_markup = get_main_menu_keyboard()
        if is_valid:
            await update.message.reply_text(
                f'Your claim is approved! 🎉\n\n',
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text(
                f'Your claim is denied. ❌\n\n',
                reply_markup=reply_markup,
            )
    except Exception as e:
        logger.error(f'Error while validating payout: {e}', exc_info=True)
        await update.message.reply_text(
            'An error occurred while processing your request. Please try again later.',
            reply_markup=reply_markup
        )
    
    return ConversationHandler.END
        

async def cancel_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Payout request process canceled.')
    return ConversationHandler.END

def register_handlers(application: Application):
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('help', help_handler))

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

    payout_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(request_payout_start, pattern='^request_payout$')],
        states={
            REQUEST_INSURANCE_POLICY: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_insurance_policy)],
            REQUEST_TRAUMA_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_trauma_code)],
            REQUEST_TRAUMA_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_trauma_time)],
            REQUEST_CRYPTO_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_crypto_wallet)],
        },
        fallbacks=[CommandHandler('cancel', cancel_payout)],
    )

    application.add_handler(payout_handler)
