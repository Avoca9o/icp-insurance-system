from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_approve_access_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm personal data access", callback_data='confirm_personal_data'),
        ],
        [
            InlineKeyboardButton("❌ Cancel", callback_data='cancel_personal_data')
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
