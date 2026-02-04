from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from Controllers.AuthController import AuthController
from Models.Worker import Worker

import requests
from Models.Config import Configuration

class DefaultController:

    @staticmethod
    async def AdminCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ No estás autenticado. Usa /login primero.")
            return
        worker : Worker = context.user_data.get("worker")
        await update.message.reply_text(f"✅ Usuario autenticado como *{worker.Role}* en *{worker.Contractor}* ({worker.ContractorID}).",
                                        parse_mode="Markdown")
        

    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/test"

    @staticmethod
    async def TestTokenCommand(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ No estás autenticado. Usa /login primero.")
            return
        token = context.user_data["token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            DefaultController.API_BASE,
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            await update.message.reply_text(f"ERROR: {response.status_code}")
            return
        await update.message.reply_text(response.json()["msg"])
        return
#
# eof
#