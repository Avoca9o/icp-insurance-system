import logging
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters

import handlers
from config import BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    address_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.callback_handler, pattern='^set_icp_address$')],
        states={
            handlers.SET_ADDRESS_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.input_icp_address)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel_converasation)],
    )

    application.add_handler(CommandHandler('start', handlers.start_command))
    application.add_handler(CommandHandler('menu', handlers.menu_command))
    application.add_handler(address_conversation_handler)
    application.add_handler(CallbackQueryHandler(handlers.callback_handler))

    logger.info("Bot is running!")
    application.run_polling()


if __name__ == "__main__":
    main()