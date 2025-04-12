from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_authorization_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('🔘 Sign in', callback_data='authorize'),
        ],
        [
            InlineKeyboardButton('🔘 Insurers List', callback_data='insurers_list'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
