from datetime import datetime
from dateutil.relativedelta import relativedelta
from telegram import Update
from telegram.ext import ContextTypes

from bot.clients.db_client import DBClient
from bot.clients.icp_client import ICPClient
from bot.config.prometheus_config import FAILURE_COUNTER, SUCCESS_COUNTER
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.utils.checksum import find_checksum
from bot.utils.logger import logger

db_client = DBClient()
icp_client = ICPClient()

async def approve_contract_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    reply_markup = get_main_menu_keyboard()

    try:
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
            insurer_scheme = db_client.get_insurer_scheme(user.insurer_id, user.schema_version)
            insurer = db_client.get_insurance_company_by_id(user.insurer_id)
            special_conditions = user.secondary_filters if user.secondary_filters else '{}'
            checksum = find_checksum(insurer_scheme.diagnoses_coefs, special_conditions)
            response = icp_client.add_approved_client(insurer.pay_address, user.id, checksum)

            if not response:
                logger.error(f'Error while sending checksum to smart-contract')
                await query.edit_message_text('Error while approving your data. Try again later...', reply_markup=reply_markup)
                return

            user.is_approved = True
            user.sign_date = datetime.now()
            user.expiration_date = user.sign_date + relativedelta(years=1)
            db_client.update_user_info(user)

            approve_message = (
                'Your information has been successfully approved! ✅\n\n'
                'Use the button below to return to the main menu.'
            )

            await query.edit_message_text(approve_message, reply_markup=reply_markup)
            SUCCESS_COUNTER.inc()
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while approving data: {str(e)}')
        await query.edit_message_text('Error while approving data. Try again later', reply_markup=reply_markup)
