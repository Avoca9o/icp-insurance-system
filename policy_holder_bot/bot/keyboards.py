from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def cancel_keyboard():
    '''Creates keyboard to cancel action'''
    keyboard = [
        [
            InlineKeyboardButton('Cancel', callback_data='cancel')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def sign_in_keyboard():
    '''Creates keyboard for sign-in'''
    keyboard = [
        [
            InlineKeyboardButton('Sign in', callback_data='sign_in'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
 

def main_menu_keyboard():
    '''Creates keyborad for main menu'''
    keyboard = [
        [
            InlineKeyboardButton('Get Info', callback_data='get_info'),
            InlineKeyboardButton('Help', callback_data='help'),
        ],
        [
            InlineKeyboardButton('Set ICP Address', callback_data='set_icp_address'),
            InlineKeyboardButton('Show ICP Address', callback_data='show_icp_address')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)