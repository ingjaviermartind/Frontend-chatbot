from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters

from Controllers.AuthController import AuthController

from Models.Crew import CrewService
from Models.Technician import TechnicianService
from Models.Worker import Worker


class ContractorController:
    # cuadrillas
    OBTENER_NOMBRE_C = range(1)
    OBTENER_CUADRILLA = range(1)
    #tecnicos
    CT_OBT_CUADRILLA, CT_OBT_NOMBRE, CT_OBT_APELLIDO, CT_OBT_CC, CT_OBT_NUMERO = range(5)
    BT_OBT_CUADRILLA, BT_OBT_TECNICO = range(2)
    @staticmethod
    async def ListarCuadrillas(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return    
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return 
        worker : Worker = context.user_data.get("worker")
        try:
            crews = CrewService.read_crew(worker.ContractorID,True)
            crewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(crews, start=1)])
            await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{crewsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END     
    #
    # Conversación para crear cuadrillas
    #
    @staticmethod
    async def CancelConversation(update : Update, context : ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⭕ operación cancelada")
        return ConversationHandler.END
    
    @staticmethod
    async def PreguntarNombreCuadrilla(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        await update.message.reply_text("¿cuál es el nombre de la cuadrilla?")
        return ContractorController.OBTENER_NOMBRE_C
    
    @staticmethod
    async def ObtenerNombreCuadrilla(update : Update, context : ContextTypes.DEFAULT_TYPE):
        new_name = update.message.text
        try:
            worker : Worker = context.user_data.get("worker")
            crews = CrewService.read_crew(worker.ContractorID,True)
            existing_names = {
                crew["name"].strip().lower()
                for crew in crews
                if "name" in crew
            }
            if new_name.strip().lower() in existing_names:
                await update.message.reply_text("❌ Ya existe una cuadrilla con ese nombre en tu empresa")
                return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END
        try:
            CrewService.create_crew(worker.ContractorID, new_name)
            await update.message.reply_text("✅ Cuadrilla creada exitosamente")
            crews = CrewService.read_crew(worker.ContractorID,True)
            crewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(crews, start=1)])
            await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{crewsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END     

    create_crew_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_cuadrilla", PreguntarNombreCuadrilla)],
        states={
            OBTENER_NOMBRE_C:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCuadrilla)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)] 
    )
    #
    # Conversación para borrar cuadrillas
    #
    @staticmethod
    async def PreguntarNombreCuadrillaDelete(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        worker : Worker = context.user_data.get("worker")

        try:
            crews = CrewService.read_crew(worker.ContractorID,True)
            crewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(crews, start=1)])
            await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{crewsMsg}")
            context.user_data['crews'] = crews
            await update.message.reply_text(f"¿cuál de las cuadrillas quieres eliminar?")
            return ContractorController.OBTENER_CUADRILLA
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END
    
    @staticmethod
    async def ObtenerNombreCuadrillaDelete(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            crews = context.user_data.get("crews", [])
            if choice < 1 or choice > len(crews):
                raise ValueError
            selected_crew = crews[choice - 1]
            crew_id = selected_crew["crewid"]
            context.user_data["crew"] = selected_crew
            await update.message.reply_text(
                f"Cuadrilla seleccionada: {selected_crew['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ContractorController.OBTENER_CUADRILLA
        try:
            CrewService.update_crew(crew_id)
            await update.message.reply_text("✅ Cuadrilla borrada exitosamente")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error borrando cuadrilla. {e}")
            return ConversationHandler.END

    delete_crew_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_cuadrilla", PreguntarNombreCuadrillaDelete)],
        states={
            OBTENER_CUADRILLA:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCuadrillaDelete)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)] 
    )
    #
    # conversación para activar técnicos
    #
    @staticmethod
    async def PreguntarCedulaAT(update : Update, context : ContextTypes.DEFAULT_TYPE):

        return ConversationHandler.END
    #
    # conversación para crear tecnicos
    #
    @staticmethod
    async def PreguntarCuadrillaCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        worker : Worker = context.user_data.get("worker")
        
        if worker.Contractor == "Azteca Comunicaciones Colombia":
            context.user_data["crewid"] = 1
            await update.message.reply_text(
                text="A continuación, te pediré la información del técnico\nEscribe el *nombre* (posterior me darás su apellido)",
                parse_mode="Markdown"
            )
            return ContractorController.CT_OBT_NOMBRE

        try:
            crews = CrewService.read_crew(worker.ContractorID,True)
            crewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(crews, start=1)])
            await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{crewsMsg}")
            context.user_data['crews'] = crews
            await update.message.reply_text(f"¿cuál de las cuadrillas va a pertenecer el técnico?")
            return ContractorController.CT_OBT_CUADRILLA
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END

    @staticmethod
    async def ObtenerCuadrillaCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            crews = context.user_data.get("crews", [])
            if choice < 1 or choice > len(crews):
                raise ValueError
            selected_crew = crews[choice - 1]
            context.user_data["crewid"] = selected_crew.get("crewid")
            await update.message.reply_text(
                f"Cuadrilla seleccionada: {selected_crew['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ContractorController.CT_OBT_CUADRILLA
        await update.message.reply_text(
            text="A continuación, te pediré la información del técnico\nEscribe el *nombre* (posterior me darás su apellido)",
            parse_mode="Markdown"
        )
        return ContractorController.CT_OBT_NOMBRE

    @staticmethod
    async def ObtenerNombreCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        firstname = update.message.text
        context.user_data["firstname"] = firstname
        await update.message.reply_text(f"✅ Nombre adquirido: {firstname}")
        await update.message.reply_text(
            text="Escribe el *apellido*",
            parse_mode="Markdown"
        )
        return ContractorController.CT_OBT_APELLIDO
    
    @staticmethod
    async def ObtenerApellidoCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        lastname = update.message.text
        context.user_data["lastname"] = lastname
        await update.message.reply_text(f"✅ Apellido adquirido: {lastname}")
        await update.message.reply_text(
            text="Escribe la *cedula de ciudadanía* sin puntos ni comas",
            parse_mode="Markdown"
        )
        return ContractorController.CT_OBT_CC
    
    @staticmethod
    async def ObtenerCedulaCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def normalize_cc(cc: str) -> str:
            cc_clean = (
                cc.replace(".", "")
                .replace(",", "")
                .replace(" ", "")
                .strip()
            )
            if not cc_clean.isdigit():
                raise ValueError("La cédula debe contener solo números")
            return cc_clean   
        cc = update.message.text
        try:
            clean_cc = normalize_cc(cc)
            context.user_data["cc"] = clean_cc
            await update.message.reply_text(f"✅ Cédula de ciudadanía adquirida: {clean_cc}")
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {e}.\nPor favor escribe la *cedula de ciudadanía* sin puntos ni comas."
            )
            return ContractorController.CT_OBT_CC
        await update.message.reply_text(
            text="Escribe el *número de celular* de sin espacios",
            parse_mode="Markdown"
        )
        return ContractorController.CT_OBT_NUMERO

    @staticmethod
    async def ObtenerNumeroCT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def normalize_num(num: str) -> str:
            num_clean = (
                num.replace(".", "")
                .replace(",", "")
                .replace(" ", "")
                .strip()
            )
            if not num_clean.isdigit():
                raise ValueError("El número telefónico debe contener solo números")
            if len(num_clean) != 10:
                raise ValueError("El número telefónico debe contener 10 dígitos")
            return num_clean   
        num = update.message.text
        try:
            clean_num = normalize_num(num)
            await update.message.reply_text(f"✅ Número telefónico adquirido: {clean_num}")
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {e}.\nPor favor escribe el *número de celular* sin espacios."
            )
            return ContractorController.CT_OBT_NUMERO
        payload = {
            "firstname" : context.user_data["firstname"],
            "lastname": context.user_data["lastname"],
            "cc": context.user_data["cc"],
            "cellphone": clean_num,
            "crewid": context.user_data["crewid"]
        }
        try:
            req = TechnicianService.create_technician(payload)
            tech = req.get("technician")
            await update.message.reply_text(f"✅ Técnico creado exitosamente")
            await update.message.reply_text(f"Nombre: {tech.get("firstname")} {tech.get("lastname")}\nCuadrilla: {tech.get("crew")}\nUsuario: {tech.get("username")}\nContraseña: {tech.get("password")}")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}.")
        finally:
            return ConversationHandler.END
        
    create_tech_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_tecnico", PreguntarCuadrillaCT)],
        states={
            CT_OBT_CUADRILLA : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerCuadrillaCT)],
            CT_OBT_NOMBRE : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCT)],
            CT_OBT_APELLIDO : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerApellidoCT)],
            CT_OBT_CC : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerCedulaCT)],
            CT_OBT_NUMERO : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNumeroCT)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)] 
    )
    #
    # conversación para borrar tecnicos
    #
    @staticmethod
    async def PreguntarCuadrillaBT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        worker : Worker = context.user_data.get("worker")
        if worker.Contractor == "Azteca Comunicaciones Colombia":
            try:
                worker : Worker = context.user_data.get("worker")
                technicians = TechnicianService.read_technician(worker.ContractorID, 1, True)
                techniciansMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}\tCC: {b['cc']}" for i, b in enumerate(technicians, start=1)])
                await update.message.reply_text(f"Los técnicos que constituyen la cuadrilla son:\n{techniciansMsg}")
                context.user_data["technicians"] = technicians
                await update.message.reply_text("¿Cuál técnico vas a borrar?")
                return ContractorController.BT_OBT_TECNICO
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error consultando técnicos. {e}")
                return ConversationHandler.END
        try:
            crews = CrewService.read_crew(worker.ContractorID,True)
            crewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(crews, start=1)])
            await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{crewsMsg}")
            context.user_data['crews'] = crews
            await update.message.reply_text(f"¿cuál de las cuadrillas pertenece el técnico que vas a borrar?")
            return ContractorController.BT_OBT_CUADRILLA
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
            return ConversationHandler.END

    @staticmethod       
    async def ObtenerCuadrillaBT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            crews = context.user_data.get("crews", [])
            if choice < 1 or choice > len(crews):
                raise ValueError
            selected_crew = crews[choice - 1]
            crewid = selected_crew.get("crewid")
            context.user_data["crew"] = selected_crew
            await update.message.reply_text(
                f"Cuadrilla seleccionada: {selected_crew['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ContractorController.BT_OBT_CUADRILLA
        try:
            worker : Worker = context.user_data.get("worker")
            technicians = TechnicianService.read_technician(worker.ContractorID, crewid, True)
            techniciansMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}\tCC: {b['cc']}" for i, b in enumerate(technicians, start=1)])
            await update.message.reply_text(f"Los técnicos que constituyen la cuadrilla son:\n{techniciansMsg}")
            context.user_data["technicians"] = technicians
            await update.message.reply_text("¿Cuál técnico vas a borrar?")
            return ContractorController.BT_OBT_TECNICO
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando técnicos. {e}")
            return ConversationHandler.END

    @staticmethod
    async def ObtenerTecnicoBT(update : Update, context : ContextTypes.DEFAULT_TYPE):
        techid : int = 0
        try:
            choice = int(update.message.text)
            technicians = context.user_data.get("technicians", [])
            if choice < 1 or choice > len(technicians):
                raise ValueError
            selected_technician = technicians[choice - 1]
            techid = selected_technician["id"]
            await update.message.reply_text(
                f"✅ Técnico seleccionado/a: {selected_technician['firstname']} {selected_technician['lastname']}"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Selección inválida. Por favor ingresa un número de la lista. {e}"
            )
        try:
            TechnicianService.update_technician(techid)
            await update.message.reply_text("✅ Técnico borrado exitosamente")
        except Exception as e:
            await update.message.reply_text("⚠️ Error borrando el técnico seleccionado.")
        finally:
            return ConversationHandler.END
    
    delete_tech_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_tecnico", PreguntarCuadrillaBT)],
        states={
            BT_OBT_CUADRILLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerCuadrillaBT)],
            BT_OBT_TECNICO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerTecnicoBT)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)] 
    )
#
# eof
#