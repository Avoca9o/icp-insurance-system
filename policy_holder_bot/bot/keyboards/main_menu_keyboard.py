from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('🔘 Main Menu', callback_data='main_menu'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
