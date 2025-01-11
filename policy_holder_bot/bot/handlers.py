from random import randint
from telegram import Message, Update
from telegram.ext import ContextTypes, ConversationHandler

from keyboards import main_menu_keyboard
from utils import is_valid_icp_address

SET_ADDRESS_STATE = range(1)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f'Hello, {user.first_name}! I am icppp-insurance-system bot.\n'
        'Write /menu to see available commands'
    )


async def get_info_command(message: Message, context: ContextTypes.DEFAULT_TYPE):
    await message.reply_text(
        'Diman is Chepunshnilla\n'
        f'Random number: {randint(1, 1000000)}'
    )


async def help_command(message: Message, context: ContextTypes.DEFAULT_TYPE):
    await message.reply_text(
        'I can handle next commands:\n'
        '/menu - Open menu with buttons\n'
        '/help - Show the list of available commands'
    )


async def input_icp_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Get ICP cryptowallet address from user and validate it'''
    wallet_address = update.message.text.strip()

    if is_valid_icp_address(wallet_address):
        context.user_data['wallet_address'] = wallet_address
        await update.message.reply_text(
            f'Thank You! Your ICP cryptowallet address "{wallet_address}" saved. 🚀'
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            'You wrote invalid ICP cryptowallet address. Try again.'
        )
        return SET_ADDRESS_STATE
    
async def cancel_converasation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Cancels current request of ICP cryptowallet address'''
    await update.message.reply_text('You canceled input of ICP cryptowallet address.')
    return ConversationHandler.END


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Outputs main menu with buttons'''
    await update.message.reply_text(
        'Choose the action:',
        reply_markup=main_menu_keyboard(),
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'get_info':
        context.args = ['Here is information, requested by button.']
        await get_info_command(query.message, context)
    elif query.data == 'help':
        await help_command(query.message, context)
    elif query.data == 'set_icp_address':
        await query.message.reply_text('Please, input your ICP cryptowallet address:')
        return SET_ADDRESS_STATE
