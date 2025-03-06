from telegram import Update
from telegram.ext import ContextTypes

from clients.db_client import DBClient
from keyboards.back_keyboard import get_back_keyboard

db_client = DBClient()

async def insurers_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    top_companies = db_client.get_most_popular_insurers()
    message = 'Below are the 7 most popular companies among users:\n'

    for company, client_count in top_companies:
        message += f"""
Title 🛡️: {company.name}
Email 📧: {company.email}
Clients count 👥: {client_count}

"""
    message += 'To log in, click on'
    reply_markup = get_back_keyboard()

    await query.edit_message_text(message, reply_markup=reply_markup)