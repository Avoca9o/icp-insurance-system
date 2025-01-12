from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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