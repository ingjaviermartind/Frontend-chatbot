import requests
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from Models.Worker import Worker
from Models.WorkerFactory import WorkerFactory
from Models.Analiyst import AnalystWorker
from Models.Config import Configuration

class AuthController:

    #API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    API_URL = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/login/"
    OBT_C_PASSWORD, OBT_N_PASSWORD, REPEAT_N_PASSWORD = range(3)

    @staticmethod
    async def Login(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if AuthController.IsAuthenticated(context):
            await update.message.reply_text("Ya estás autenticado...")
            return
        try:
            args = update.message.text.split()
            if len(args) != 3:
                await update.message.reply_text("Uso correcto: login <usuario> <contraseña>")
                return
            _, username, password = args
            response = requests.post(
                AuthController.API_URL,
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code != 200:
                if response.status_code == 401:
                    await update.message.reply_text("❌ Credenciales inválidas.")
                elif response.status_code == 403:
                    await update.message.reply_text("🚫 Acceso denegado")
                else:
                    await update.message.reply_text(
                        f"⚠️ Error del servidor ({response.status_code})"
                    )
                return      
            payload = response.json()
            role = payload.get("object_type")
            data = payload.get("item")
            token = payload.get("access")
            refresh = payload.get("refresh")
            if not role or not data or not token or not refresh:
                await update.message.reply_text("⚠️ Respuesta inválida del servidor.")
                return
            context.user_data.clear()
            context.user_data["authenticated"] = True
            context.user_data["token"] = token
            context.user_data["refresh"] = refresh
            worker : Worker = WorkerFactory.create(role, data)
            if isinstance(worker,AnalystWorker):
                if worker.Contractor == "Azteca Comunicaciones Colombia":
                    context.user_data["permission"] = "admin"
                else:
                    context.user_data["permission"] = "basic"
            else:
                context.user_data["permission"] = "user"
            context.user_data["worker"] = worker
            await update.message.reply_text( f"✅ Login correcto. Bienvenido, {worker.Firstname}." )

        except Exception as e:
            await update.message.reply_text(f"⚠️ Error al intentar loguearse: {e}")
        finally:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
            except:
                pass
    
    @staticmethod
    async def Logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if AuthController.IsAuthenticated(context):
            worker = context.user_data["worker"]
            context.user_data.clear()
            await update.message.reply_text(f"👋 Sesión cerrada correctamente. Adiós, {worker.Firstname}.")
        else:
            await update.message.reply_text("⚠️ No hay ninguna sesión activa.")

    @staticmethod
    def IsAuthenticated(context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not context.user_data.get("authenticated"):
            return False
        return True

    @staticmethod
    async def CancelConversation(update : Update, context : ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⭕ operación cancelada")
        return ConversationHandler.END
    
    @staticmethod
    async def AskCurrentPassword(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ No estás autenticado. Usa /login primero.")
            return
        
        await update.message.reply_text(
            text="Escribe la contraseña actual",
            parse_mode="Markdown"
        )
        return AuthController.OBT_C_PASSWORD
    
    @staticmethod
    async def ObtainCurrentPassword(update : Update, context : ContextTypes.DEFAULT_TYPE):
        password = update.message.text
        context.user_data["old_password"] = password
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass
        await update.message.reply_text(
            text="Escribe la nueva contraseña",
            parse_mode="Markdown"
        )
        return AuthController.OBT_N_PASSWORD
    
    @staticmethod
    async def ObtainNewPassword(update : Update, context : ContextTypes.DEFAULT_TYPE):
        password = update.message.text
        context.user_data["new_password"] = password
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass
        await update.message.reply_text(
            text="Repite la nueva contraseña",
            parse_mode="Markdown"
        )
        return AuthController.REPEAT_N_PASSWORD
    
    @staticmethod
    async def RepeatNewPassword(update : Update, context : ContextTypes.DEFAULT_TYPE):
        new_password_2 = update.message.text
        new_password_1 = context.user_data["new_password"]
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
        except:
            pass
        if new_password_1 != new_password_2:
            await update.message.reply_text(
                text="❌ Las contraseñas no coinciden",
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        token = context.user_data["token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/change-password/",
            json={
                "old_password": context.user_data["old_password"],
                "new_password": context.user_data["new_password"]
            },
            headers=headers,
            timeout=10
        )
        data = response.json()
        if response.status_code != 200:
            await update.message.reply_text(f"ERROR: {response.status_code}\n{data.get('error') or data.get('detail')}")
            ConversationHandler.END
            return        
        await update.message.reply_text(
            text="la contraseña ha sido cambiada... Vuelve a loguearte",
            parse_mode="Markdown"
        )
        if AuthController.IsAuthenticated(context):
            worker = context.user_data["worker"]
            context.user_data.clear()
            await update.message.reply_text(f"👋 Sesión cerrada correctamente. Adiós, {worker.Firstname}.")
        else:
            await update.message.reply_text("⚠️ No hay ninguna sesión activa.")
        return ConversationHandler.END
     
    change_password_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("change_password", AskCurrentPassword)],
        states={
            OBT_C_PASSWORD : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtainCurrentPassword)],
            OBT_N_PASSWORD : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtainNewPassword)],
            REPEAT_N_PASSWORD : [MessageHandler(filters.TEXT & ~filters.COMMAND, RepeatNewPassword)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
#
# EOF
#