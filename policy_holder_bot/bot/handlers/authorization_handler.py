import random
import re
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.clients.db_client import DBClient
from bot.clients.mailgun_client import MailgunClient
from bot.config.prometheus_config import FAILURE_COUNTER, SUCCESS_COUNTER
from bot.keyboards.main_menu_keyboard import get_main_menu_keyboard
from bot.keyboards.authorization_keyboard import get_authorization_keyboard
from bot.utils.logger import logger

db_client = DBClient()
mailgun_client = MailgunClient()

REQUEST_EMAIL, REQUEST_VERIFICATION_CODE = range(2)

async def authorization_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    await query.edit_message_text('Please, enter your email address for authorization:')
    return REQUEST_EMAIL

async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text

    try:
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
    except Exception as e:
        FAILURE_COUNTER.inc()
        logger.error(f'Error while authorizing by email: {str(e)}')
        await update.message.reply_text('Error while authorizing by email. Try again later', reply_markup=get_authorization_keyboard())
        return ConversationHandler.END

async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_code = update.message.text.strip()
    correct_code = context.user_data.get('verification_code')

    if user_code == correct_code:
        try:
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
        except Exception as e:
            logger.error(f'Error while code verification: {str(e)}')
            await update.message.reply_text('Error while code verification. Try again later', reply_markup=get_authorization_keyboard())
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
    SUCCESS_COUNTER.inc()
    return ConversationHandler.END
        