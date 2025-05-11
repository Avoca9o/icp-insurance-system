from telegram import Update
from telegram.ext import ContextTypes

from bot.clients.db_client import DBClient
from bot.config.prometheus_config import FAILURE_COUNTER, SUCCESS_COUNTER
from bot.keyboards.back_keyboard import get_back_keyboard
from bot.utils.logger import logger

db_client = DBClient()

async def insurers_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        top_companies = db_client.get_most_popular_insurers()
        message = 'Below are the most popular companies among users:\n'

        for company, client_count in top_companies:
            message += f"""
Title 🛡️: {company.name}
Email 📧: {company.email}
Clients count 👥: {client_count}

"""
        message += 'To log in, click on'
        reply_markup = get_back_keyboard()

        SUCCESS_COUNTER.inc()
        await query.edit_message_text(message, reply_markup=reply_markup)
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while searching insurers: {str(e)}')
        await query.edit_message_text('Error while searching insurers. Try again later', reply_markup=get_back_keyboard())