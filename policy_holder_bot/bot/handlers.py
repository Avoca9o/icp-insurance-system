from random import randint
from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f'Hello, {user.first_name}! I am icppp-insurance-system bot. How can I help you?')


async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(
        f'I got "{text}"\n'
        'Diman is Chepunshnilla\n'
        f'Random number: {randint(1, 1000000)}'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'I can handle next commands:\n'
        '/start - Start work with bot\n'
        '/help - Writing this message'
    )