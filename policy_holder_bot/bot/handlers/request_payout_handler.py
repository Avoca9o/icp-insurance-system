import json
from datetime import datetime, date
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.clients.db_client import DBClient
from bot.clients.icp_client import ICPClient
from bot.clients.open_banking_client import OpenBankingClient
from bot.config.diagnosis_config import DIAGNOSIS_LIST
from bot.config.prometheus_config import FAILURE_COUNTER, SUCCESS_COUNTER
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.keyboards.approve_access_keyboard import get_approve_access_keyboard
from bot.models.payout import Payout
from bot.utils.logger import logger

db_client = DBClient()
icp_client = ICPClient()
open_banking_client = OpenBankingClient()

APPROVE_ACCESS, REQUEST_POLICY_NUMBER, REQUEST_DIAGNOSIS_CODE, REQUEST_DIAGNOSIS_TIME, REQUEST_CRYPTO_WALLET = range(5)

async def request_payout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    reply_markup = get_main_menu_keyboard()
    try:
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
        
        reply_markup = get_approve_access_keyboard()

        await query.edit_message_text(
            'To process payout request, please confirm that you provide access to your personal information:',
            reply_markup=reply_markup,
        )
        return APPROVE_ACCESS
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while request payout: {str(e)}')
        await query.edit_message_text('Error while request payout. Try again later', reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END

async def approve_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    oauth_token = await open_banking_client.get_oauth_token()
    context.user_data['oauth_token'] = oauth_token

    if query.data == 'confirm_personal_data':
        await query.edit_message_text('Personal data access confirmed. ✅\n\nPlease enter your policy number:')
        return REQUEST_POLICY_NUMBER
    else:
        reply_markup = get_main_menu_keyboard()
        await query.edit_message_text('Payout request canceled. ❌', reply_markup=reply_markup)
        return ConversationHandler.END


async def request_policy_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    policy_number = update.message.text
    
    context.user_data['policy_number'] = policy_number

    await update.message.reply_text('Please enter the diagnosis code:')
    return REQUEST_DIAGNOSIS_CODE


async def request_diagnosis_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    diagnosis_code = update.message.text

    if diagnosis_code not in DIAGNOSIS_LIST:
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

    return await process_payout(update=update, context=context)


async def process_payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    policy_number = context.user_data['policy_number']
    diagnosis_code = context.user_data['diagnosis_code']
    diagnosis_date = context.user_data['diagnosis_date']
    if isinstance(diagnosis_date, str):
        diagnosis_date = datetime.strptime(diagnosis_date, '%Y-%m-%d').date()
    elif isinstance(diagnosis_date, datetime):
        diagnosis_date = diagnosis_date.date()
    elif not isinstance(diagnosis_date, date):
        raise ValueError("Invalid date format")
    
    crypto_wallet = context.user_data['crypto_wallet']
    telegram_id = context.user_data['telegram_id']
    oauth_token = context.user_data['oauth_token']
    reply_markup = get_main_menu_keyboard()

    try:
        user = db_client.get_user_by_telegram_id(telegram_id=telegram_id)

        if user.sign_date.date() > diagnosis_date or user.expiration_date.date() < diagnosis_date:
            await update.message.reply_text(
                'The insured event is not relevant for the current contract by date.',
                reply_markup=reply_markup,
            )
            return ConversationHandler.END

        transaction = db_client.get_payout(user_id=user.id, diagnosis_code=diagnosis_code, diagnosis_date=diagnosis_date)
        if transaction:
            await update.message.reply_text(
                'Transfer was already made.',
                reply_markup=reply_markup,
            )
            return ConversationHandler.END
        
        if user.secondary_filters:
            secondary_filters = json.loads(user.secondary_filters.replace('\'', '\"'))
        else:
            secondary_filters = {}

        coefficient = 0
        if diagnosis_code in secondary_filters:
            coefficient = secondary_filters.get(diagnosis_code)
        else:
            schema = json.loads(db_client.get_insurer_scheme(user.insurer_id, user.schema_version).diagnoses_coefs)
            coefficient = schema.get(diagnosis_code, 0)
        
        amount = user.insurance_amount * coefficient
        insurer_crypto_wallet = db_client.get_insurance_company_by_id(user.insurer_id).pay_address

        is_valid = icp_client.payout_request(
            amount=amount,
            policy_number=policy_number,
            diagnosis_code=diagnosis_code,
            diagnosis_date=diagnosis_date,
            crypto_wallet=crypto_wallet,
            insurer_crypto_wallet=insurer_crypto_wallet,
            oauth_token=oauth_token,
        )

        if is_valid:
            db_client.add_payout(payout=Payout(transaction_id='999', amount=amount, user_id=user.id, date=datetime.now(), company_id=user.insurer_id, diagnosis_code=diagnosis_code, diagnosis_date=diagnosis_date))
            logger.info(f'Successfull insurance case validation. Client ID: {user.id}')
            await update.message.reply_text(
                f'Your claim is approved! 🎉\n\n',
                reply_markup=reply_markup,
            )
        else:
            logger.info(f'Failed insurance case validation. Client ID: {user.id}')
            await update.message.reply_text(
                f'Your claim is denied. ❌\n\n',
                reply_markup=reply_markup,
            )
        SUCCESS_COUNTER.inc()
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while processing request: {e}', exc_info=True)
        await update.message.reply_text(
            'An error occurred while processing your request. Please try again later.',
            reply_markup=reply_markup
        )
    
    return ConversationHandler.END
