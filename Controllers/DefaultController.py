from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
from Controllers.AuthController import AuthController
from Models.Worker import Worker

import requests
from Models.Config import Configuration

from ApiClient.ApiClient import SessionExpired
import httpx

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

    @staticmethod
    def select_from_context(context, key: str, index: int):
        items = context.user_data.get(key, [])
        if index < 1 or index > len(items):
            raise ValueError("Selección fuera de rango")
        return items[index - 1]
    
    @staticmethod
    def build_numbered_list(items, label_fn):
        return "\n".join(
            f"{i}. {label_fn(item)}"
            for i, item in enumerate(items, start=1)
        )
    
    @staticmethod
    async def require_auth(update, context, *, admin=False, basic=False):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return False
        if context.user_data.get("permission") == "admin":
            return True
        if context.user_data.get("permission") == "basic":
            if admin:
                await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
                return False
        if context.user_data.get("permission") == "user":
             if admin or basic:
                await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
                return False
        return True
    
    @staticmethod
    async def safe_request(update, coro):
        try:
            return await coro
        except SessionExpired:
            await update.message.reply_text(
                "🔒 Tu sesión ha expirado. Por favor inicia sesión nuevamente."
            )
            return ConversationHandler.END
        except httpx.HTTPError:
            await update.message.reply_text(
                "⚠️ No fue posible comunicarse con el servidor. Intenta más tarde."
            )
            return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(
                f"⚠️ Ocurrió un error inesperado consultando los departamentos.\n {e}"
            )
            return ConversationHandler.END 
#
# eof
#