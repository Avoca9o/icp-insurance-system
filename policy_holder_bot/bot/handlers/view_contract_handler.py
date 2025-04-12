import json
import os
from telegram import Update
from telegram.ext import ContextTypes

from bot.clients.db_client import DBClient
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.utils.docx_creator import create_docx_file

db_client = DBClient()

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

        special_conditions_flag = False
        special_conditions = None
        if user.secondary_filters:
            special_conditions = user.secondary_filters.replace('\'', '\"')
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
            create_docx_file(f'{telegram_id}-insurer-scheme', json.loads(insurer_scheme.diagnoses_coefs))
            with open(f'{telegram_id}-insurer-scheme.docx', 'rb') as file:
                await query.message.reply_document(document=file, filename='insurer_scheme.docx')
            os.remove(f'{telegram_id}-insurer-scheme.docx')
        if special_conditions_flag:
            create_docx_file(f'{telegram_id}-special-conditions', json.loads(special_conditions))
            with open(f'{telegram_id}-special-conditions.docx', 'rb') as file:
                await query.message.reply_document(document=file, filename='special_conditions.docx')
            os.remove(f'{telegram_id}-special-conditions.docx')
        await query.message.reply_text('Return to main menu', reply_markup=reply_markup)