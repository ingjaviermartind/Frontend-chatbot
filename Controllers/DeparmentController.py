from telegram import Update
from telegram.ext import ContextTypes
from Controllers.AuthController import AuthController
from Models.Builder import BuilderService

API_BASE = "http://127.0.0.1:8000/api/Deparmentbuilder/"

class DeparmentController:
    @staticmethod
    async def list_deparments(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("❌ No tienes privilegios para esta acción.")
            return
        try:
            result = BuilderService.list_builders()
            builders = builders = "\n".join([f"{b['builderid']}. {b['name']}" for b in result])
            await update.message.reply_text(f"📋 Lista de contratistas:\n{builders}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")