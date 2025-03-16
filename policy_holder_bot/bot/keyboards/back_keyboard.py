from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_back_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('🔘 Authorize', callback_data='authorize'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
