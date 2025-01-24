import json
import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters

from clients import DBClient, ICPClient
from keyboards import get_action_menu_keyboard, get_authorization_keyboard, get_main_menu_keyboard
from models import Transaction
from utils import logger, validate_diagnosis_code

REQUEST_EMAIL = 0
REQUEST_DIAGNOSIS_CODE, REQUEST_DIAGNOSIS_TIME, REQUEST_CRYPTO_WALLET = range(3)

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


async def view_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    reply_markup = get_main_menu_keyboard()

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

        special_conditions = user.secondary_filters
        special_conditions_flag = False
        if user.secondary_filters:
            special_conditions_flag = True
        
        insurer_scheme = db_client.get_insurer_scheme(insurer_id=insurer_id, global_version_num=global_version_num)
        insurer_scheme_flag = False
        if insurer_scheme and insurer_scheme.diagnoses_coefs:
            insurer_scheme_flag = True
    
        info_message = (
            f'Insurance amount: 💰 {insurance_amount}\n'
            f'Insurance company: 🏢 {company_name}\n'
            f'User approval status: {is_approved}'
        )

        if not insurer_scheme_flag:
            info_message += f'Payout coefficients: 📊 N/A\n'
        if not special_conditions_flag:
            f'Special conditions: 📝 No special conditions\n'

        if not (insurer_scheme_flag or special_conditions_flag):
            await query.edit_message_text(info_message, reply_markup=reply_markup)
            return
        
        await query.edit_message_text(info_message)
        if insurer_scheme_flag:
            with open(f'{telegram_id}-insurer-scheme.json', 'w', encoding='utf-8') as file:
                file.write(insurer_scheme.diagnoses_coefs)
            with open(f'{telegram_id}-insurer-scheme.json', 'rb') as file:
                await query.message.reply_document(document=file, filename='insurer_scheme.json')
        if special_conditions_flag:
            with open(f'{telegram_id}-special-conditions.json', 'w', encoding='utf-8') as file:
                file.write(special_conditions)
            with open(f'{telegram_id}-special-conditions.json', 'rb') as file:
                await query.message.reply_document(document=file, filename='special_conditions.json')
        await query.message.reply_text('Return to main menu', reply_markup=reply_markup)


async def request_payout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    reply_markup = get_main_menu_keyboard()

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)
    context.user_data['telegram_id'] = telegram_id

    if not user:
        await query.edit_message_text(
            'You are not authorized. Please authorize using the /start command.'
        )
        return ConversationHandler.END
    
    if not user.is_approved:
        await query.edit_message_text(
            'Your contract information is not approved yet. Please confirm your information before requesting a payout.',
            reply_markup=reply_markup,
        )
        return ConversationHandler.END
    
    await query.edit_message_text('Please enter your diagnosis code:')
    return REQUEST_DIAGNOSIS_CODE


async def request_diagnosis_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    diagnosis_code = update.message.text

    if not validate_diagnosis_code(diagnosis_code=diagnosis_code):
        await update.message.reply_text(
            'Invalid diagnosis code. Try again using this source: https://www.cito-priorov.ru/cito/files/telemed/Perechen_kodov_MKB.pdf'
        )
        return REQUEST_DIAGNOSIS_CODE

    context.user_data['diagnosis_code'] = diagnosis_code

    await update.message.reply_text('Please enter the registration time of the diagnosis (YYYY-MM-DD):')
    return REQUEST_DIAGNOSIS_TIME


async def request_diagnosis_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    diagnosis_date = update.message.text

    try:
        diagnosis_date = datetime.strptime(diagnosis_date, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            'Invalid date format. Please use the format YYYY-MM-DD HH:MM'
        )
        return REQUEST_DIAGNOSIS_TIME

    context.user_data['diagnosis_date'] = diagnosis_date

    await update.message.reply_text('Please enter the cryptowallet address principal:')
    return REQUEST_CRYPTO_WALLET


async def request_crypto_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crypto_wallet = update.message.text

    context.user_data['crypto_wallet'] = crypto_wallet

    await update.message.reply_text('Processing payout request. Please wait...')
    return await process_payout(update=update, context=context)


async def process_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    diagnosis_code = context.user_data['diagnosis_code']
    diagnosis_date = context.user_data['diagnosis_date']
    crypto_wallet = context.user_data['crypto_wallet']
    telegram_id = context.user_data['telegram_id']
    reply_markup = get_main_menu_keyboard()

    user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)

    transaction = db_client.get_transaction(user_id=user.id, code=diagnosis_code, date=diagnosis_date)
    if transaction:
        await update.message.reply_text(
            'Transfer was already made.',
            reply_markup=reply_markup,
        )
        return ConversationHandler.END
    
    if user.secondary_filters:
        secondary_filters = json.loads(user.secondary_filters)
    else:
        secondary_filters = {}
    coefficient = 0
    if diagnosis_code in secondary_filters:
        coefficient = secondary_filters.get(diagnosis_code)
    else:
        schema = json.loads(db_client.get_insurer_scheme(user.insurer_id, user.schema_version).diagnoses_coefs)
        coefficient = schema.get(diagnosis_code)
    amount = user.insurance_amount * coefficient
    insurer_crypto_wallet = db_client.get_insurance_company_by_id(user.insurer_id).pay_address

    try:
        is_valid = icp_client.payout_request(
            amount=amount,
            diagnosis_code=diagnosis_code,
            diagnosis_date=diagnosis_date,
            crypto_wallet=crypto_wallet,
            insurer_crypto_wallet=insurer_crypto_wallet
        )

        if is_valid:
            db_client.add_transaction(transaction=Transaction(amount=amount, user_id=user.id, diagnosis_code=diagnosis_code, diagnosis_date=diagnosis_date))
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
    reply_markup = get_main_menu_keyboard()
    await update.message.reply_text('Payout request process canceled.', reply_markup=reply_markup)
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
            REQUEST_DIAGNOSIS_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_diagnosis_code)],
            REQUEST_DIAGNOSIS_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_diagnosis_date)],
            REQUEST_CRYPTO_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_crypto_wallet)],
        },
        fallbacks=[CommandHandler('cancel', cancel_payout)],
    )

    application.add_handler(payout_handler)
