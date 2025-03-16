from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_action_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton('🔘 View information about the contract', callback_data='view_contract'),
        ],
        [
            InlineKeyboardButton('🔘 Approve information about the contract', callback_data='approve_contract'),
        ],
        [
            InlineKeyboardButton('🔘 Request a payout', callback_data='request_payout'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
