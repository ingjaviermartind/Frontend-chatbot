from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationBuilder, MessageHandler, \
ConversationHandler, CallbackQueryHandler, filters
# --------------------- Controllers --------------------- #
from Controllers.DefaultController import DefaultController
from Controllers.AuthController import AuthController
from Controllers.ActivityController import ActivityController
from Controllers.ContractorController import ContractorController
from Controllers.OperationController import OperationController
# - test - #
async def show_chat_id(update, context):
    chat = update.effective_chat
    await update.message.reply_text(
        f"chat_id: {chat.id}\n"
        f"tipo: {chat.type}\n"
        f"titulo: {chat.title}"
    )

 
Token = "8457868045:AAFzAPMEPKlrZylBpusJh6b1-N4IiegTpkU"
Application = ApplicationBuilder().token(Token).build()
Application.bot_data["alarmas_requests"] = {}
# -- main -- #
Application.add_handler(ActivityController.Entry_conversation_handler)
Application.add_handler(ActivityController.Exit_conversation_handler)
Application.add_handler(MessageHandler(filters.PHOTO & filters.Chat(ActivityController.GROUP_ID), ActivityController.RecibirFotosAlarmas))
# -- auth -- #
Application.add_handler(CommandHandler("login", AuthController.Login))
Application.add_handler(CommandHandler("logout", AuthController.Logout))
Application.add_handler(CommandHandler("admin", DefaultController.AdminCommand))
Application.add_handler(AuthController.change_password_conversation_handler)
# -- contractor -- #
Application.add_handler(ContractorController.create_crew_conversation_handler)
Application.add_handler(ContractorController.delete_crew_conversation_handler)
Application.add_handler(ContractorController.create_tech_conversation_handler)
Application.add_handler(ContractorController.delete_tech_conversation_handler)
Application.add_handler(CommandHandler("listar_cuadrillas", ContractorController.ListarCuadrillas))
# -- operation control -- #
Application.add_handler(OperationController.create_analyst_conversation_handler)
Application.add_handler(OperationController.read_analyst_conversation_handler)
Application.add_handler(OperationController.delete_analyst_conversation_handler)
Application.add_handler(OperationController.read_municipality_conversation_handler)
Application.add_handler(OperationController.create_municipality_conversation_handler)
Application.add_handler(OperationController.update_municipality_conversation_handler)
Application.add_handler(OperationController.create_contractor_conversation_handler)
Application.add_handler(OperationController.delete_contractor_conversation_handler)
Application.add_handler(OperationController.create_node_conversation_handler)
Application.add_handler(OperationController.read_node_conversation_handler)
Application.add_handler(OperationController.delete_node_conversation_handler)
Application.add_handler(CommandHandler("listar_contratistas", OperationController.ListarContratistas))

# -- test -- #
Application.add_handler(CommandHandler("chatid", show_chat_id))
Application.add_handler(CommandHandler("token", DefaultController.TestTokenCommand))

Application.run_polling(allowed_updates = Update.ALL_TYPES)

# hupper -m main

#
# EOF
#
