from telegram import Update
from datetime import datetime
import uuid
import base64

from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters

from Controllers.AuthController import AuthController
from Models.Entry import EntryService
from Models.Municipality import MunicipalityService
from Models.Department import DepartmentService
from Models.Node import NodeService
from Models.Technician import TechnicianWorker, TechnicianService
from Models.Worker import Worker
from Models.Crew import CrewService
from Models.WorkerFactory import WorkerFactory
from Models.Exit import ExitService
from Models.Photo import PhotoService

class ActivityController:

    GROUP_ID = -5011765199

    OBTENER_CUADRILLA       , OBTENER_TECNICO           , \
    OBTENER_DEPT            , OBTENER_MUN               , OBTENER_NODO              , PREGUNTAR_FECHA       , PEDIR_FECHA           , \
    OBTENER_FECHA           , OBTENER_N_TICKET          , OBTENER_N_ORDEN           , OBTENER_N_PERSONAS    , OBTENER_DESCRIPCION   , \
    SOLICITAR_FOTO_ALARMAS  , OBTENER_FOTO_ID           , OBTENER_FOTO_PANORAMICA   , OBTENER_FOTO_CERRADO  , OBTENER_FOTO_ALARMAS  , \
    OBTENER_FOTO_ABIERTO  = range(18)

    OBTENER_INGRESO             , PREGUNTAR_FECHA_CIERRE    , OBTENER_FECHA_CIERRE      , OBTENER_DESCRIPCION_CIERRE    , OBTENER_FOTO_ID_CIERRE    ,\
    OBTENER_FOTO_ABI_CIERRE     , OBTENER_FOTO_CER_CIERRE   , OBTENER_FOTO_PAN_CIERRE   , OBTENER_FOTO_ALARMAS_CIERRE   , = range(9)

    @staticmethod
    async def CancelConversation(update : Update, context : ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⭕ Bitácora cancelada")
        return ConversationHandler.END
        
    @staticmethod
    async def PedirDepartamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END
        worker : Worker = context.user_data.get("worker")
        if worker.Role != "Técnico":
            if worker.Contractor == "Azteca Comunicaciones Colombia":
                try:
                    Technicians = TechnicianService.read_technician(worker.ContractorID, None, True)
                    TechniciansMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}\tCC: {b['cc']}" for i, b in enumerate(Technicians, start=1)])
                    await update.message.reply_text(f"Los técnicos que tu empresa tiene a disposición son:\n{TechniciansMsg}")
                    context.user_data["technicians"] = Technicians
                    await update.message.reply_text("¿Cuál técnico va a desarrollar la actividad?")
                    return ActivityController.OBTENER_TECNICO
                except:
                    await update.message.reply_text("⚠️ Error consultando técnicos.")
                    return ConversationHandler.END
            try:
                Crews = CrewService.read_crew(worker.ContractorID, True)
                CrewsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(Crews, start=1)])
                await update.message.reply_text(f"Las cuadrillas que tu empresa tiene a disposición son:\n{CrewsMsg}")
                context.user_data["crews"] = Crews
                await update.message.reply_text("¿Cuál cuadrilla va a desarrollar la actividad?")
                return ActivityController.OBTENER_CUADRILLA
            except Exception as e:
                await update.message.reply_text(f"⚠️ Error consultando cuadrillas. {e}")
                return ConversationHandler.END
        try:
            worker : Worker = context.user_data.get("worker")
            Departments = DepartmentService.read_department(worker.ContractorID)
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(Departments, start=1)])
            await update.message.reply_text(f"Los departamentos que tu empresa tiene cobertura son:\n{DepartmentsMsg}")
            context.user_data["departments"] = Departments
        except Exception as e:
            await update.message.reply_text("⚠️ Error consultando departamentos.")
            return ConversationHandler.END
        await update.message.reply_text("¿En qué departamento está el nodo?")
        return ActivityController.OBTENER_DEPT

    @staticmethod
    async def ObtenerCuadrilla(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            crews = context.user_data.get("crews", [])
            if choice < 1 or choice > len(crews):
                raise ValueError
            selected_crew = crews[choice - 1]
            crew_id = selected_crew["crewid"]
            context.user_data["crew"] = selected_crew
            await update.message.reply_text(
                f"✅ Cuadrilla seleccionada: {selected_crew['name']}"
            )
            Technicians = TechnicianService.read_technician(Crew=crew_id,isactive=True)
            TechniciansMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}\tCC: {b['cc']}" for i, b in enumerate(Technicians, start=1)])
            await update.message.reply_text(f"Los técnicos que tu empresa tiene a disposición son:\n{TechniciansMsg}")
            context.user_data["technicians"] = Technicians
            await update.message.reply_text("¿Cuál técnico va a desarrollar la actividad?")
            return ActivityController.OBTENER_TECNICO
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.OBTENER_CUADRILLA

    @staticmethod 
    async def ObtenerTecnico(update : Update, context : ContextTypes.DEFAULT_TYPE):
        techid : int = 0
        try:
            choice = int(update.message.text)
            technicians = context.user_data.get("technicians", [])
            if choice < 1 or choice > len(technicians):
                raise ValueError
            selected_technician = technicians[choice - 1]
            techid = selected_technician["id"]
            context.user_data["technicianid"] = techid
            context.user_data["technician"] = selected_technician
            context.user_data["tech"] = WorkerFactory.create("Técnico", selected_technician)
            await update.message.reply_text(
                f"✅ Técnico seleccionado/a: {selected_technician['firstname']} {selected_technician['lastname']}"
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Selección inválida. Por favor ingresa un número de la lista. {e}"
            )
        try:
            Departments = DepartmentService.read_department(context.user_data["technician"].get("contractorid"))
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(Departments, start=1)])
            await update.message.reply_text(f"Los departamentos que tu empresa tiene cobertura son:\n{DepartmentsMsg}")
            context.user_data["departments"] = Departments
        except Exception as e:
            await update.message.reply_text("⚠️ Error consultando departamentos.")
            return ConversationHandler.END
        await update.message.reply_text("¿En qué departamento está el nodo?")
        return ActivityController.OBTENER_DEPT

    @staticmethod
    async def ObtenerDepartamento(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            department_id = selected_department["departmentid"]
            context.user_data["department"] = selected_department
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
            Municipalities = MunicipalityService.read_municipality(department_id)
            MunicipalitiesMsg = "\n".join([f"{i}. {M['name']}" for i, M in enumerate(Municipalities, start=1)])
            await update.message.reply_text(
                f"Los municipios del departamento seleccionado son:\n{MunicipalitiesMsg}"
            )
            context.user_data["municipalities"] = Municipalities
            await update.message.reply_text("¿en qué municipio está el nodo?")
            return ActivityController.OBTENER_MUN
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.OBTENER_DEPT

    @staticmethod
    async def ObtenerMunicipio(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            municipalities = context.user_data.get("municipalities", [])
            if choice < 1 or choice > len(municipalities):
                raise ValueError
            selected_municipality = municipalities[choice - 1]
            municipality_id = selected_municipality["municipalityid"]
            context.user_data["municipality"] = selected_municipality
            await update.message.reply_text(
                f"✅ Municipio seleccionado: {selected_municipality['name']}"
            )
            payload = {
                "municipality": municipality_id,
                "isactive": True
            }
            Nodes = NodeService.read_node(payload)
            if len(Nodes) == 1:
                node = Nodes[0]
                context.user_data["node"] = node
                await update.message.reply_text(
                    f"✅ Nodo seleccionado: {node.get('code')}"
                )
                await update.message.reply_text("¿La hora actual es la hora de inicio de actividad?\n1. Sí\n2. No")
                return ActivityController.PREGUNTAR_FECHA
            
            elif len(Nodes) > 1:
                NodesMsg = "\n".join([f"{i}. {M['code']}" for i, M in enumerate(Nodes, start=1)])
                await update.message.reply_text(
                    f"Los nodos del municipio seleccionado son:\n{NodesMsg}"
                )
                context.user_data["nodes"] = Nodes
                await update.message.reply_text("¿en cuál de los nodos del municipio se realizará la actividad?")
                return ActivityController.OBTENER_NODO
            
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.OBTENER_MUN
    
    @staticmethod
    async def ObtenerNodo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            nodes = context.user_data.get("nodes", [])
            if choice < 1 or choice > len(nodes):
                raise ValueError
            selected_node = nodes[choice - 1]
            node_id = selected_node["nodeid"]
            context.user_data["node"] = selected_node
            await update.message.reply_text(
                f"✅ Nodo seleccionado: {selected_node.get('code')}"
            )
            await update.message.reply_text("¿La hora actual es la hora de inicio de actividad?\n1. Sí\n2. No")
            return ActivityController.PREGUNTAR_FECHA
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.OBTENER_NODO    
    
    @staticmethod
    async def PreguntarFecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            if choice == 1:
                now = datetime.now()
                context.user_data["datetime"] = now
                await update.message.reply_text(
                f"🕒 Hora registrada: {now.strftime('%Y:%m:%d %H:%M')}"
                )
                await update.message.reply_text("Digita el número de ticket")
                return ActivityController.OBTENER_N_TICKET
            elif choice == 2:
                await update.message.reply_text("Digita al hora de inicio de la actividad, ten en cuenta el formato YYYY:MM:DD HH:MM, la hora es formato 24h")
                return ActivityController.OBTENER_FECHA
            else:
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.PREGUNTAR_FECHA        
           
    @staticmethod
    async def ObtenerFecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        try:
            selected_datetime = datetime.strptime(text, "%Y:%m:%d %H:%M")
            context.user_data["datetime"] = selected_datetime
            await update.message.reply_text(
                f"🕒 Hora registrada: {selected_datetime.strftime('%Y:%m:%d %H:%M')}"
            )
            await update.message.reply_text("Digita el número de ticket")
            return ActivityController.OBTENER_N_TICKET
        except ValueError:
            await update.message.reply_text(
            "❌ Formato inválido.\n"
            "Por favor ingresa la fecha y hora en este formato:\n"
            "`YYYY:MM:DD HH:MM`\n"
            "Ejemplo: `2025:12:18 14:30`",
            parse_mode="Markdown"
                )
            return ActivityController.OBTENER_FECHA
    
    @staticmethod
    async def ObtenerNTicket(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            num = int(update.message.text)
            if num < 0 or num > 20e6:
                raise ValueError
            context.user_data["ticket"] = num
            await update.message.reply_text(f"#️⃣ Número de ticket {num} registrado")
            await update.message.reply_text("Digita el número de orden")
            return ActivityController.OBTENER_N_ORDEN
        except ValueError:
            await update.message.reply_text("❌ Dato inválido. ingresa números únicamente\n")
            return ActivityController.OBTENER_N_TICKET
    
    @staticmethod
    async def ObtenerNOrden(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            num = int(update.message.text)
            if num < 0 or num > 20e6:
                raise ValueError
            context.user_data["orden"] = num
            await update.message.reply_text(f"#️⃣ Número de orden {num} registrado")
            await update.message.reply_text("Digita el número de personas que van a realizar la actividad")
            return ActivityController.OBTENER_N_PERSONAS
        except ValueError:
            await update.message.reply_text("❌ Dato inválido. ingresa números únicamente\n")
            return ActivityController.OBTENER_N_ORDEN
    
    @staticmethod
    async def ObtenerNPersonas(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            num = int(update.message.text)
            if num < 0 or num > 20:
                raise ValueError
            context.user_data["n_personas"] = num
            await update.message.reply_text(f"👷{num} personas van a realizar actividades en el nodo")
            await update.message.reply_text("Escribe una descripción de la actividad a realizar")
            return ActivityController.OBTENER_DESCRIPCION
        except ValueError:
            await update.message.reply_text("❌ Dato inválido. ingresa números únicamente\n")
            return ActivityController.OBTENER_N_ORDEN

    @staticmethod
    async def ObtenerDescripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        Description = update.message.text
        await update.message.reply_text("✅ Descripción de actividad adquirida")
        context.user_data["description"] = Description
        bot_data = context.application.bot_data
        request_id = str(uuid.uuid4())
        node = context.user_data["node"]
        department = context.user_data["department"]
        municipality = context.user_data["municipality"]
        msg = (
            f"🚨 *SOLICITUD DE ALARMAS DE RECTIFICADOR INGRESO* 🚨\n\n"
            f"Se requiere pantallazo del rectificador\n"
            f"\t*Departamento*: {department['name']}\n"
            f"\t*Municipio*: {municipality['name']}\n"
            f"\t*Código*: {str(node.get('code')).replace("_", r"\_")}\n"
            f"\t*Dirección de gestión*: {node['ipaddress']}\n"
            "⚠️ *RESPONDE a este mensaje el pantallazo de las alarmas*"
        )
        sent_msg = await context.bot.send_message(
            chat_id=ActivityController.GROUP_ID,
            text= msg,
            parse_mode="Markdown"
        )
        bot_data["alarmas_requests"][request_id] = {
            "chatid": update.effective_chat.id,
            "msgid": sent_msg.message_id,
            "node_code": node['code'],
            "fileid": None,
            "type": "entry",
            "status": "pending",
            "caption": None
        }
        context.user_data["alarmas_request_id"] = request_id
        await update.message.reply_text(
            "📸 Solicitud enviada al grupo con nuestros analistas de red.\n"
            "Esperando pantallazo de alarmas... Procura *NO abrir* el gabinete antes de recibir las alarmas",
            parse_mode='Markdown'
        )
        worker : Worker = context.user_data["worker"]
        await update.message.reply_text("Las siguientes fotos que me envies deben tener georeferenciación junto con las estampas de tiempo y marcas de agua requeridas")
        await update.message.reply_text(f"*1.* Comparteme una foto de tu cédula de ciudadanía o de tu ID de {worker.Contractor}", parse_mode='Markdown')
        return ActivityController.OBTENER_FOTO_ID
    
    @staticmethod
    async def ObtenerFotoID(update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["fotocc_id"] = photo.file_id
        await update.message.reply_text(f"*2.* Comparteme una foto de la panorámica del nodo", parse_mode='Markdown')
        return ActivityController.OBTENER_FOTO_PANORAMICA
    
    @staticmethod
    async def ObtenerFotoPanoramica(update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["fotopanoramica_id"] = photo.file_id
        await update.message.reply_text(f"*3.*Comparteme una foto donde se enfoque el gabinete cerrado del nodo", parse_mode='Markdown') 
        return ActivityController.OBTENER_FOTO_CERRADO
    
    @staticmethod
    async def ObtenerFotoCerrado(update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["cerrado_id"] = photo.file_id
        await update.message.reply_text(f"Por protocolo *NO debes abrir* el gabinete sin recibir el pantallazo de las alarmas del rectificador", parse_mode='Markdown')
        await update.message.reply_text(f"Apenas recibas el pantallazo de las alarmas, *confirma* que te haya llegado", parse_mode='Markdown')
        await update.message.reply_text(f"Puedes preguntarme si ya me enviaron la foto los analistas de operaciones de red 👍")
        return ActivityController.OBTENER_FOTO_ALARMAS
    
    @staticmethod
    async def ObtenerFotoAlarmas(update: Update, context: ContextTypes.DEFAULT_TYPE):
        request_id = context.user_data.get("alarmas_request_id")
        bot_data = context.application.bot_data
        req = bot_data["alarmas_requests"].get(request_id)
        if req and req["fileid"]:
            context.user_data["alarmas_photo_id"] = req["fileid"]
            # Limpieza
            bot_data["alarmas_requests"].pop(request_id, None)
            await update.message.reply_text(f"*4.* Comparteme una foto del gabinete abierto del nodo", parse_mode='Markdown')
            return ActivityController.OBTENER_FOTO_ABIERTO
        await update.message.reply_text("⏳ Aún no se ha recibido la foto.") 
        return ActivityController.OBTENER_FOTO_ALARMAS
    
    @staticmethod
    async def ObtenerFotoAbierto(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⌚ Procesando las fotos, por favor espera.")
        photoid = update.message.photo[-1]
        photo = await context.bot.get_file(photoid)
        photo_bytes = await photo.download_as_bytearray()
        DoorOpen_b64 = base64.b64encode(photo_bytes).decode("utf-8")
        # Alarms
        photoid = context.user_data["alarmas_photo_id"]
        photo = await context.bot.get_file(photoid)
        photo_bytes = await photo.download_as_bytearray()
        RC_b64 = base64.b64encode(photo_bytes).decode("utf-8")
        # close
        photoid = context.user_data["cerrado_id"]
        photo = await context.bot.get_file(photoid)
        photo_bytes = await photo.download_as_bytearray()
        DoorClose_b64 = base64.b64encode(photo_bytes).decode("utf-8")
        # panoramic
        photoid = context.user_data["fotopanoramica_id"]
        photo = await context.bot.get_file(photoid)
        photo_bytes = await photo.download_as_bytearray()
        Panoramic_b64 = base64.b64encode(photo_bytes).decode("utf-8")
        # ID
        photoid = context.user_data["fotocc_id"]
        photo = await context.bot.get_file(photoid)
        photo_bytes = await photo.download_as_bytearray()
        CC_b64 = base64.b64encode(photo_bytes).decode("utf-8")
        try:
            payload_photos={
                "panoramic": Panoramic_b64,
                "dooropen": DoorOpen_b64,
                "doorclose": DoorClose_b64,
                "rectifieralarms": RC_b64,
                "identification": CC_b64,
            }
            req_photo = PhotoService.create_photo(payload_photos)
        except:
            await update.message.reply_text(f"❌ Error almacenando las fotos.")
            return ConversationHandler.END
        await update.message.reply_text(f"✅ Fotos procesadas, enviando bitácora de ingreso...")
        dt = context.user_data["datetime"]
        Tech : TechnicianWorker
        if isinstance(context.user_data.get("worker"), TechnicianWorker):
            Tech = context.user_data.get("worker")
        else:
            Tech = context.user_data.get("tech")
        Node = context.user_data["node"]
        payload = {
            "techid": Tech.getID,
            "crewid": Tech.CuadrillaID,
            "nodeid": Node.get('nodeid'),
            "datetime" : dt.isoformat(),
            "ticketnum": context.user_data["ticket"],
            "ordernum": context.user_data["orden"],
            "description": context.user_data["description"],
            "exitid": None,
            "isactive": True,
            "photoid": req_photo.get('photoid')
        }
        try:
            EntryService.create_Entry(payload)
            await update.message.reply_text("✅ Bitacora diligenciada correctamente.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error creando la bitácora.\n{e}")
        return ConversationHandler.END

    Entry_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("ingreso", PedirDepartamento)],
        states={
            OBTENER_CUADRILLA:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerCuadrilla)],
            OBTENER_TECNICO:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerTecnico)],
            OBTENER_DEPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamento)],#Regex(r"^\d+$")
            OBTENER_MUN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerMunicipio)],
            OBTENER_NODO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNodo)],
            PREGUNTAR_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, PreguntarFecha)],
            OBTENER_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerFecha)],
            OBTENER_N_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNTicket)],
            OBTENER_N_ORDEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNOrden)],
            OBTENER_N_PERSONAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNPersonas)],
            OBTENER_DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDescripcion)],
            OBTENER_FOTO_ID: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoID)],
            OBTENER_FOTO_PANORAMICA: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoPanoramica)],
            OBTENER_FOTO_CERRADO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoCerrado)],
            OBTENER_FOTO_ALARMAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerFotoAlarmas)],
            OBTENER_FOTO_ABIERTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoAbierto)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )

    @staticmethod
    async def RecibirFotosAlarmas(update : Update, context : ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message or not message.reply_to_message or not message.photo:
            return
        reply_to = message.reply_to_message
        bot_data = context.application.bot_data
        for request_id, req in list(bot_data.get("alarmas_requests", {}).items()):
            if reply_to.message_id != req["msgid"]:
                continue
            photo = message.photo[-1]
            req["fileid"] = photo.file_id
            if req.get("type") == "exit" and message.caption is not None:
                req["status"] = "rejected"
                req["caption"] = message.caption
                await context.bot.send_photo(
                    chat_id=req["chatid"],
                    photo=photo.file_id,
                    caption=f"Foto de alarmas recibida\nNodo: {req['node_code']}\n"
                )
                await context.bot.send_message(
                    chat_id=req["chatid"],
                    text=(
                        "❌ *CIERRE RECHAZADO POR TORRE DE CONTROL*\n\n"
                        f"📝 Observación:\n_{message.caption}_\n\n"
                        "Debes corregir las alarmas y volver a realizar el cierre.\n"
                        "Responde recibido a este mensaje para finalizar la conversación"
                    ),
                    parse_mode="Markdown"
                )
                await update.message.reply_text("❌ Cierre rechazado. Se notificó al técnico.")
                return
            req["status"] = "approved"
            await context.bot.send_photo(
                chat_id=req["chatid"],
                photo=photo.file_id,
                caption=f"✅ Foto de alarmas recibida\nNodo: {req['node_code']}\nNotificame con un Recibido que te llegó la foto",
            )
            await update.message.reply_text(
                f"✅ Foto de alarmas recibida correctamente.\nNodo: {req['node_code']}\n"
                "Gracias 👌"
            )
            return     
    
    #
    # cierre
    #
    @staticmethod
    async def PedirIngreso(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def safe_date(value):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except Exception:
                return "N/A"
        def safe_time(value):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime("%H:%M")
            except Exception:
                return "N/A"
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END
        try:
            worker : Worker = context.user_data.get("worker")
            Entries = EntryService.read_Entry(IsActive=True,Contractor=worker.ContractorID)
            context.user_data["entries"] = Entries
            EntriesMsg = "\n".join([f"{i}. {b['node_item']['item']['item']['name']} {b['node_item']['item']['name']}\nTécnico: {b['technician_item']['firstname']} {b['technician_item']['lastname']}\nFecha: {safe_date(b.get('datetime'))}\nHora: {safe_time(b.get('datetime'))}\n" for i, b in enumerate(Entries, start=1)])
            if not EntriesMsg:
                await update.message.reply_text("No hay actividades disponibles para dar cierre.")
                return ConversationHandler.END          
            await update.message.reply_text(f"Las actividades iniciadas por tu empresa son las siguientes:\n{EntriesMsg}")
            
        except:
            await update.message.reply_text("⚠️ Error consultando ingresos.")
            return ConversationHandler.END
        await update.message.reply_text(f"¿Cuál actividad vas a reportar cierre?")
        return ActivityController.OBTENER_INGRESO
    
    @staticmethod
    async def ObtenerIngreso(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def safe_date(value):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except Exception:
                return "N/A"
        def safe_time(value):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime("%H:%M")
            except Exception:
                return "N/A"
        try:
            choice = int(update.message.text)
            entries = context.user_data.get("entries", [])
            if choice < 1 or choice > len(entries):
                raise ValueError
            selected_entry = entries[choice - 1]
            entry_id = selected_entry["entryid"]
            context.user_data["entry"] = selected_entry
            context.user_data["entryid"] = entry_id
            await update.message.reply_text(
                f"✅ Entrada seleccionada:\n{selected_entry['node_item']['item']['item']['name']} {selected_entry['node_item']['item']['name']}\nTécnico: {selected_entry['technician_item']['firstname']}\nFecha: {safe_date(selected_entry.get('datetime'))}\nHora: {safe_time(selected_entry.get('datetime'))}"
            )
            await update.message.reply_text("¿La hora actual es la hora de inicio de actividad?\n1. Sí\n2. No")
            return ActivityController.PREGUNTAR_FECHA_CIERRE
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.OBTENER_INGRESO

    @staticmethod
    async def PreguntarFechaCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            if choice == 1:
                now = datetime.now()
                context.user_data["datetime"] = now
                await update.message.reply_text(
                f"🕒 Hora registrada: {now.strftime('%Y:%m:%d %H:%M')}"
                )
                await update.message.reply_text("Escribe una descripción de la actividad que realizaste")
                return ActivityController.OBTENER_DESCRIPCION_CIERRE
            elif choice == 2:
                await update.message.reply_text("Digita al hora de inicio de la actividad, ten en cuenta el formato YYYY:MM:DD HH:MM, la hora es formato 24h")
                return ActivityController.OBTENER_FECHA_CIERRE
            else:
                raise ValueError
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return ActivityController.PREGUNTAR_FECHA_CIERRE    

    @staticmethod
    async def ObtenerFechaCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.strip()
        try:
            selected_datetime = datetime.strptime(text, "%Y:%m:%d %H:%M")
            context.user_data["datetime"] = selected_datetime
            await update.message.reply_text(
                f"🕒 Hora registrada: {selected_datetime.strftime('%Y:%m:%d %H:%M')}"
            )
            await update.message.reply_text("Escribe una descripción de la actividad a realizar")
            return ActivityController.OBTENER_DESCRIPCION_CIERRE
        except ValueError:
            await update.message.reply_text(
            "❌ Formato inválido.\n"
            "Por favor ingresa la fecha y hora en este formato:\n"
            "`YYYY:MM:DD HH:MM`\n"
            "Ejemplo: `2025:12:18 14:30`",
            parse_mode="Markdown"
                )
            return ActivityController.OBTENER_FECHA_CIERRE

    @staticmethod
    async def ObtenerDescripcionCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        Description = update.message.text
        await update.message.reply_text("✅ Descripción de actividad adquirida")
        context.user_data["description"] = Description
        bot_data = context.application.bot_data
        request_id = str(uuid.uuid4())
        node = context.user_data["entry"]["node_item"]
        department = context.user_data["entry"]["node_item"]["item"]["item"]
        municipality = context.user_data["entry"]["node_item"]["item"]
        sent_msg = await context.bot.send_message(
            chat_id=ActivityController.GROUP_ID,
            text=(
                "🚨 *SOLICITUD DE ALARMAS DE RECTIFICADOR CIERRE* 🚨\n\n"
                "Se requiere pantallazo del rectificador\n"
                f"\t*Departamento:* {department['name']}\n"
                f"\t*Municipio:* {municipality['name']}\n"
                f"\t*Código:* {str(node.get('code')).replace("_", r"\_")}\n"
                f"\t*Dirección de gestión:* {node['ipaddress']}\n"
                "⚠️ *RESPONDE* a este mensaje el pantallazo de las alarmas"
            ),
            parse_mode="Markdown"
        )
        bot_data["alarmas_requests"][request_id] = {
            "chatid": update.effective_chat.id,
            "msgid": sent_msg.message_id,
            "node_code": node['code'],
            "fileid": None,
            "type": "exit",
            "status": "pending",
            "caption": None,
        }
        context.user_data["alarmas_request_id"] = request_id
        await update.message.reply_text(
            "📸 Solicitud enviada al grupo con nuestros analistas de red.\n"
            "Esperando pantallazo de alarmas...",
            parse_mode='Markdown'
        )
        await update.message.reply_text("Las siguientes fotos que me envies deben tener georeferenciación junto con las estampas de tiempo y marcas de agua requeridas")
        await update.message.reply_text(f"*1.* Comparteme una foto del gabinete abierto del nodo", parse_mode='Markdown')
        return ActivityController.OBTENER_FOTO_ABI_CIERRE

    @staticmethod
    async def ObtenerFotoAbiertoCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["abierto_id"] = photo.file_id
        await update.message.reply_text(f"*2.*Comparteme una foto donde se enfoque el gabinete cerrado del nodo", parse_mode='Markdown') 
        return ActivityController.OBTENER_FOTO_CER_CIERRE
    
    @staticmethod
    async def ObtenerFotoCerradoCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["cerrado_id"] = photo.file_id
        await update.message.reply_text(f"*3.*Comparteme una foto de la panorámica del nodo", parse_mode='Markdown') 
        return ActivityController.OBTENER_FOTO_PAN_CIERRE

    @staticmethod
    async def ObtenerFotoPanoramicaCierre(update : Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        context.user_data["fotopanoramica_id"] = photo.file_id
        await update.message.reply_text(f"Por protocolo *NO debes salir del nodo* sin recibir el pantallazo de las alarmas del rectificador", parse_mode='Markdown')
        await update.message.reply_text(f"Apenas recibas el pantallazo de las alarmas, *confirma* que te haya llegado", parse_mode='Markdown')
        await update.message.reply_text(f"Puedes preguntarme si ya me enviaron la foto los analistas de operaciones de red 👍")
        return ActivityController.OBTENER_FOTO_ALARMAS_CIERRE

    @staticmethod
    async def ObtenerFotoAlarmasCierre(update: Update, context: ContextTypes.DEFAULT_TYPE):
        request_id = context.user_data.get("alarmas_request_id")
        bot_data = context.application.bot_data
        req = bot_data["alarmas_requests"].get(request_id)
        if req and req["status"] == "rejected":
            await update.message.reply_text(f"❌ cierre de actividad cancelada por Control de Operaciones.")
            return ConversationHandler.END
        if req and req["fileid"]:
            context.user_data["alarmas_photo_id"] = req["fileid"]
            # Limpieza
            bot_data["alarmas_requests"].pop(request_id, None)
            await update.message.reply_text("⌚ Procesando las fotos, por favor espera.")
            # Open
            photoid = context.user_data["abierto_id"]
            photo = await context.bot.get_file(photoid)
            photo_bytes = await photo.download_as_bytearray()
            DoorOpen_b64 = base64.b64encode(photo_bytes).decode("utf-8")
            # Alarms
            photoid = context.user_data["alarmas_photo_id"]
            photo = await context.bot.get_file(photoid)
            photo_bytes = await photo.download_as_bytearray()
            RC_b64 = base64.b64encode(photo_bytes).decode("utf-8")
            # close
            photoid = context.user_data["cerrado_id"]
            photo = await context.bot.get_file(photoid)
            photo_bytes = await photo.download_as_bytearray()
            DoorClose_b64 = base64.b64encode(photo_bytes).decode("utf-8")
            # panoramic
            photoid = context.user_data["fotopanoramica_id"]
            photo = await context.bot.get_file(photoid)
            photo_bytes = await photo.download_as_bytearray()
            Panoramic_b64 = base64.b64encode(photo_bytes).decode("utf-8")
            try:
                payload_photos={
                    "panoramic": Panoramic_b64,
                    "dooropen": DoorOpen_b64,
                    "doorclose": DoorClose_b64,
                    "rectifieralarms": RC_b64,
                }
                req_photo = PhotoService.create_photo(payload_photos)
            except:
                await update.message.reply_text(f"❌ Error almacenando las fotos.")
                return ConversationHandler.END
        
            await update.message.reply_text("✅ Fotos procesadas, enviando bitácora de cierre...")
            dt = context.user_data["datetime"]
            payload = {
                "datetime" : dt.isoformat(),
                "description": context.user_data["description"],
                "photoid": req_photo.get('photoid')
            }
            try:
                resp = ExitService.create_exit(payload)
                entryid = context.user_data["entryid"]
                exitid = resp.get("exitid")
                await update.message.reply_text(f"✅ Se creó bitácora de cierre exitosamente.")
                EntryService.update_Entry(
                    EntryID=entryid,
                    IsActive=False,
                    ExitID=exitid
                )
                await update.message.reply_text("✅ Se dio cierre a la actividad ingresada.")
            except Exception as e:
                await update.message.reply_text(f"❌ Error creando la bitácora.\n{e}")
            return ConversationHandler.END
        await update.message.reply_text("⏳ Aún no se ha recibido la foto.") 
        return ActivityController.OBTENER_FOTO_ALARMAS_CIERRE

    Exit_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("cierre", PedirIngreso)],
        states={
            OBTENER_INGRESO:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerIngreso)],
            PREGUNTAR_FECHA_CIERRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, PreguntarFechaCierre)],
            OBTENER_FECHA_CIERRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerFechaCierre)],
            OBTENER_DESCRIPCION_CIERRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDescripcionCierre)],
            OBTENER_FOTO_ABI_CIERRE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoAbiertoCierre)],
            OBTENER_FOTO_CER_CIERRE: [MessageHandler(filters.ALL & ~filters.COMMAND, ObtenerFotoCerradoCierre)],
            OBTENER_FOTO_PAN_CIERRE: [MessageHandler(filters.PHOTO & ~filters.COMMAND, ObtenerFotoPanoramicaCierre)],
            OBTENER_FOTO_ALARMAS_CIERRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerFotoAlarmasCierre)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )

    #
    # EOF
    #