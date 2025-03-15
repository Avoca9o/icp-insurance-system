from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters

from handlers.approve_contract_handler import approve_contract_handler
from handlers.authorization_handler import authorization_handler, request_email, verify_code, REQUEST_EMAIL, REQUEST_VERIFICATION_CODE
from handlers.cancel_authorization_handler import cancel_authorization_handler
from handlers.cancel_payout_handler import cancel_payout_handler
from handlers.help_handler import help_handler
from handlers.insurers_list_handler import insurers_list_handler
from handlers.main_menu_handler import main_menu_handler
from handlers.request_payout_handler import request_payout_handler, approve_access, request_policy_number, request_crypto_wallet, request_diagnosis_code, request_diagnosis_date, APPROVE_ACCESS, REQUEST_CRYPTO_WALLET, REQUEST_DIAGNOSIS_CODE, REQUEST_DIAGNOSIS_TIME, REQUEST_POLICY_NUMBER
from handlers.start_handler import start_handler
from handlers.view_contract_handler import view_contract_handler

def register_handlers(application: Application):
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('help', help_handler))

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(authorization_handler, pattern='^authorize$')],
        states={
            REQUEST_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_email)],
            REQUEST_VERIFICATION_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel_authorization_handler)],
    )

    application.add_handler(conversation_handler)

    application.add_handler(CallbackQueryHandler(insurers_list_handler, pattern='^insurers_list$'))

    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern='^main_menu$'))

    application.add_handler(CallbackQueryHandler(approve_contract_handler, pattern='^approve_contract$'))

    application.add_handler(CallbackQueryHandler(view_contract_handler, pattern='^view_contract$'))

    payout_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(request_payout_handler, pattern='^request_payout$')],
        states={
            APPROVE_ACCESS: [CallbackQueryHandler(approve_access, pattern='^(confirm_personal_data|cancel_personal_data)$')],
            REQUEST_POLICY_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_policy_number)],
            REQUEST_DIAGNOSIS_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_diagnosis_code)],
            REQUEST_DIAGNOSIS_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_diagnosis_date)],
            REQUEST_CRYPTO_WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, request_crypto_wallet)],
        },
        fallbacks=[CommandHandler('cancel', cancel_payout_handler)],
    )

    application.add_handler(payout_handler)