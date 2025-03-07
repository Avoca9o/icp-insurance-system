import random
import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from clients.db_client import DBClient
from clients.mailgun_client import MailgunClient
from keyboards.main_menu_keyboard import get_main_menu_keyboard

db_client = DBClient()
mailgun_client = MailgunClient()

REQUEST_EMAIL, REQUEST_VERIFICATION_CODE = range(2)

async def authorization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text('Please, enter your email address for authorization:')
    return REQUEST_EMAIL

async def request_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        await update.message.reply_text('The email you entered is not valid. Please try again.')
        return REQUEST_EMAIL

    user = db_client.get_user_by_email(email)
    if user:
        verification_code = random.randint(100000, 999999)

        email_sent = mailgun_client.send_email(
            email,
            'Policy Holder Verification',
            verification_code
        )

        if email_sent:
            context.user_data['verification_code'] = str(verification_code)
            context.user_data['attempts_left'] = 3
            context.user_data['email'] = email
            
            db_client.update_user_info(user)

            await update.message.reply_text(
                f'We have sent a 6-digit verification code to {email}. Please enter it here:'
            )
            return REQUEST_VERIFICATION_CODE
        else:
            await update.message.reply_text('Failed to send verification code. Please contact support. Write /start to try again')
            return ConversationHandler.END
    else:
        await update.message.reply_text(
            'No user was found with this email. Please try again with a different email or contact support.'
        )
        return REQUEST_EMAIL

async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_code = update.message.text.strip()
    correct_code = context.user_data.get('verification_code')

    if user_code == correct_code:
        email = context.user_data.get('email')
        user = db_client.get_user_by_email(email)
        telegram_id = update.effective_user.id
        user.telegram_id = telegram_id
        db_client.update_user_info(user)
        
        welcome_message = (
            f'Authorization successful! 🎉 Your account is now linked to Telegram.\n\n'
            f'Welcome!!! You can go to main actions.'
        )
        reply_markup = get_main_menu_keyboard()

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        return ConversationHandler.END
    else:
        context.user_data['attempts_left'] -= 1
        attempts_left = context.user_data['attempts_left']

        if attempts_left > 0:
            await update.message.reply_text(
                f'Incorrect code. Please try again. Attempts left: {attempts_left}'
            )
            return REQUEST_VERIFICATION_CODE
        else:
            await update.message.reply_text(
                'You have exceeded the number of attempts. Please start the authorization process again via /start'
            )
            context.user_data.clear()
            return ConversationHandler.END
        