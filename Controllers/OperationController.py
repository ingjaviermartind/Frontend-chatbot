from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters

from Controllers.AuthController import AuthController

from Models.Department import DepartmentService
from Models.Municipality import MunicipalityService
from Models.Node import NodeService
from Models.Contractor import ContractorService
from Models.Analiyst import AnalystService

class OperationController:
    # -- Municipality -- #
    CM_OBT_DEPT, CM_OBT_NOMBRE, CM_OBT_DANE = range(3)
    LM_OBT_DEPT = range(1)
    EM_OBT_DEPT, EM_OBT_MUN, EM_PRE_NOMBRE, EM_OBT_NOMBRE, EM_PRE_DANE, EM_OBT_DANE = range(6)
    # -- Contractor -- #
    CC_OBT_NOMBRE, CC_PRE_ACTIVAR = range(2)
    BC_OBT_CONTRATISTA = range(1)
    # -- Analyst -- #
    CA_OBT_CONTRATISTA, CA_OBT_NOMBRE, CA_OBT_APELLIDO = range(3)
    LA_OBT_CONTRATISTA = range(1)
    BA_OBT_CONTRATISTA, BA_OBT_ANALISTA = range(2)
    # -- Node -- #
    CN_OBT_DEPT, CN_OBT_MUN, CN_OBT_COD, CN_OBT_DIR, CN_PRE_IPV4, CN_OBT_IPV4 = range(6)
    LN_OBT_DEPT, LN_OBT_MUN = range(2)
    BN_OBT_DEPT, BN_OBT_MUN, BN_OBT_NODO = range(3)
    @staticmethod
    async def CancelConversation(update : Update, context : ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⭕ operación cancelada")
        return ConversationHandler.END
    #
    # Conversación para listar municipios por departamento
    #
    @staticmethod
    async def PreguntarDepartamentoLM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento vas a consultar los municipios?")
        return OperationController.LM_OBT_DEPT
    
    @staticmethod
    async def ObtenerDepartamentoLM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
        try:
            municipalities = MunicipalityService.read_municipality(selected_department.get('departmentid'))
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {selected_department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
        finally:
            return ConversationHandler.END
    
    read_municipality_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("listar_municipios", PreguntarDepartamentoLM)],
        states={
            LM_OBT_DEPT:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoLM)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para crear Municipios
    #
    @staticmethod
    async def PreguntarDepartamentoCM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento está el municipio que vas a crear?")
        return OperationController.CM_OBT_DEPT

    @staticmethod
    async def ObtenerDepartamentoCM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            context.user_data["department"] = selected_department
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
        await update.message.reply_text("¿cuál es el nombre del municipio?")
        return OperationController.CM_OBT_NOMBRE

    @staticmethod
    async def ObtenerNombreCM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        new_name = update.message.text
        department = context.user_data.get("department")
        try:
            municipalities = MunicipalityService.read_municipality(department.get('departmentid'))
            existing_names = {
                municipality["name"].strip().lower()
                for municipality in municipalities
                if "name" in municipality
            }
            if new_name.strip().lower() in existing_names:
                await update.message.reply_text("❌ Ya existe un municipio con ese nombre")
                return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        context.user_data["name"] = new_name
        await update.message.reply_text("✅ Nombre de municipio valido")
        await update.message.reply_text("¿Cuál es el código dane del municipio?")
        return OperationController.CM_OBT_DANE

    @staticmethod
    async def ObtenerDaneCM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def normalize_num(num: str) -> str:
            num_clean = (
                num.replace(".", "")
                .replace(",", "")
                .replace(" ", "")
                .strip()
            )
            if not num_clean.isdigit():
                raise ValueError("El número telefónico debe contener solo números")
            return num_clean
        department = context.user_data.get("department")
        dane = update.message.text
        try:
            clean_dane = normalize_num(dane)
            await update.message.reply_text(f"✅ código dane adquirido")
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {e}.\nPor favor escribe el *código dane* sin espacios."
            )
            return OperationController.CM_OBT_DANE
        department = context.user_data.get("department") 
        try:
            MunicipalityService.create_municipality(
                DeptID=department.get("departmentid"),
                Dane=clean_dane,
                Name=context.user_data["name"]
            )
            await update.message.reply_text("✅ Municipio creado exitosamente")
            municipalities = MunicipalityService.read_municipality(department.get('departmentid'))
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")
        finally:
            return ConversationHandler.END

    create_municipality_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_municipio", PreguntarDepartamentoCM)],
        states={
            CM_OBT_DEPT:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoCM)],
            CM_OBT_NOMBRE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCM)],
            CM_OBT_DANE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDaneCM)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para editar municipios
    #
    @staticmethod
    async def PreguntarDepartamentoEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento está el municipio que vas a editar?")
        return OperationController.EM_OBT_DEPT

    @staticmethod
    async def ObtenerDepartamentoEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            context.user_data["department"] = selected_department
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
        try:
            municipalities = MunicipalityService.read_municipality(selected_department.get('departmentid'))
            context.user_data["municipalities"] = municipalities
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {selected_department.get('name')} son:\n{municipalityMsg}")
            await update.message.reply_text("¿cuál es el municipio que vas a editar?")
            return OperationController.EM_OBT_MUN
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        
    @staticmethod
    async def ObtenerMunicipioEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            municipalities = context.user_data.get("municipalities", [])
            if choice < 1 or choice > len(municipalities):
                raise ValueError
            selected_municipality = municipalities[choice - 1]
            context.user_data["municipality"] = selected_municipality
            await update.message.reply_text(
                f"✅ Municipio seleccionado: {selected_municipality['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.EM_OBT_MUN
        
        await update.message.reply_text("¿Vas a editar el nombre del municipio?\n1. Sí\n2. No")
        return OperationController.EM_PRE_NOMBRE

    @staticmethod
    async def PreguntarNombreEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            if choice == 1:
                await update.message.reply_text("Escribe el nuevo nombre del municipio")
                return OperationController.EM_OBT_NOMBRE
            elif choice == 2:
                await update.message.reply_text("¿Vas a editar el dane del municipio?\n1. Sí\n2. No")
                context.user_data["name"] = None
                return OperationController.EM_PRE_DANE
            else:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Selección inválida. Por favor ingresa un número de la lista.")
            return OperationController.EM_PRE_DANE

    @staticmethod 
    async def ObtenerNombreEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        new_name = update.message.text
        department = context.user_data.get("department")
        try:
            municipalities = MunicipalityService.read_municipality(department.get('departmentid'))
            existing_names = {
                municipality["name"].strip().lower()
                for municipality in municipalities
                if "name" in municipality
            }
            if new_name.strip().lower() in existing_names:
                await update.message.reply_text("❌ Ya existe un municipio con ese nombre")
                return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        context.user_data["name"] = new_name
        await update.message.reply_text("✅ Nombre de municipio valido")
        await update.message.reply_text("¿Vas a editar el dane del municipio?\n1. Sí\n2. No")
        return OperationController.EM_PRE_DANE

    @staticmethod
    async def PreguntarDaneEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            if choice == 1:
                await update.message.reply_text("Escribe el nuevo dane del municipio")
                return OperationController.EM_OBT_DANE
            elif choice == 2:
                if context.user_data.get("name") is None:
                    await update.message.reply_text("✅ No se editó el municipio")
                    return ConversationHandler.END
            else:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Selección inválida. Por favor ingresa un número de la lista.")
            return OperationController.EM_PRE_DANE
        municipality = context.user_data.get("municipality")
        department = context.user_data.get("department")
        try:
            MunicipalityService.update_municipality(
                Name=context.user_data["name"],
                MunID=municipality.get("municipalityid")
            )
            await update.message.reply_text("✅ Municipio editado exitosamente")
            municipalities = MunicipalityService.read_municipality(department.get('departmentid'))
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")
        return ConversationHandler.END

    @staticmethod
    async def ObtenerDaneEM(update : Update, context : ContextTypes.DEFAULT_TYPE):
        def normalize_num(num: str) -> str:
            num_clean = (
                num.replace(".", "")
                .replace(",", "")
                .replace(" ", "")
                .strip()
            )
            if not num_clean.isdigit():
                raise ValueError("El número telefónico debe contener solo números")
            return num_clean
        municipality = context.user_data.get("municipality")
        department = context.user_data.get("department")
        dane = update.message.text
        try:
            clean_dane = normalize_num(dane)
            await update.message.reply_text(f"✅ código dane adquirido")
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {e}.\nPor favor escribe el *código dane* sin espacios."
            )
            return OperationController.CM_OBT_DANE
        try:
            MunicipalityService.update_municipality(
                Name=context.user_data["name"],
                Dane=clean_dane,
                MunID=municipality.get("municipalityid")
            )
            await update.message.reply_text("✅ Municipio editado exitosamente")
            municipalities = MunicipalityService.read_municipality(department.get('departmentid'))
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error: {e}")
        finally:
            return ConversationHandler.END

    update_municipality_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("editar_municipio", PreguntarDepartamentoEM)],
        states={
            EM_OBT_DEPT:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoEM)],
            EM_OBT_MUN:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerMunicipioEM)],
            EM_PRE_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, PreguntarNombreEM)],
            EM_OBT_NOMBRE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreEM)],
            EM_PRE_DANE:[MessageHandler(filters.TEXT & ~filters.COMMAND, PreguntarDaneEM)],
            EM_OBT_DANE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDaneEM)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para crear contratistas
    #
    @staticmethod
    async def PreguntarNombreCC(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        await update.message.reply_text("¿cuál es el nombre de la empresa contratista?")
        return OperationController.CC_OBT_NOMBRE
    
    @staticmethod
    async def ObtenerNombreCC(update : Update, context : ContextTypes.DEFAULT_TYPE):
        new_name = update.message.text
        try:
            contractors = ContractorService.read_contractor(True)
            existing_names = {
                contractor["name"].strip().lower()
                for contractor in contractors
                if "name" in contractor
            }
            if new_name.strip().lower() in existing_names:
                await update.message.reply_text("❌ Ya existe un contratista con ese nombre")
                return ConversationHandler.END
                await update.message.reply_text("¿Vas a editar el dane del municipio?\n1. Sí\n2. No")
                return OperationController.CC_PRE_ACTIVAR
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
        try:
            ContractorService.create_contractor(new_name)
            await update.message.reply_text("✅ Contratista creado exitosamente")
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
    
    create_contractor_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_contratista", PreguntarNombreCC)],
        states={
            CC_OBT_NOMBRE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCC)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para borrar contratistas
    #
    @staticmethod
    async def PreguntarNombreBC(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
            await update.message.reply_text(f"¿cuál de los contratistas quieres eliminar?")
            return OperationController.BC_OBT_CONTRATISTA
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
    
    @staticmethod
    async def ObtenerNombreBC(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            contractors = context.user_data.get("contractors", [])
            if choice < 2 or choice > len(contractors):
                raise ValueError
            selected_contractor = contractors[choice - 1]
            contractorid = selected_contractor["contractorid"]
            await update.message.reply_text(
                f"Contratista seleccionado: {selected_contractor['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.BC_OBT_CONTRATISTA
        try:
            ContractorService.update_contractor(contractorid)
            await update.message.reply_text("✅ Contratista borrado exitosamente")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error borrando contratista. {e}")
            return ConversationHandler.END
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
        finally:
            return ConversationHandler.END

    delete_contractor_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_contratista", PreguntarNombreBC)],
        states={
            BC_OBT_CONTRATISTA:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreBC)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Listar contratistas
    #
    @staticmethod
    async def ListarContratistas(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
        finally:
            return 
    #
    # Activar Contratistas
    #
    activate_contractor_conversation_handler = ConversationHandler(
        entry_points=[],
        states={
            
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para listar analistas
    #
    @staticmethod
    async def PreguntarContratistaLA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
            await update.message.reply_text(f"¿De cuál contratista vas visualizar los analistas?")
            return OperationController.LA_OBT_CONTRATISTA
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
        
    
    @staticmethod
    async def ObtenerContratistaLA(update : Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            contractors = context.user_data.get("contractors", [])
            if choice < 1 or choice > len(contractors):
                raise ValueError
            selected_contractor = contractors[choice - 1]
            await update.message.reply_text(
                f"Contratista seleccionado: {selected_contractor['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CA_OBT_CONTRATISTA
        filters = {
            "isactive": True,
            "contractor": selected_contractor.get("contractorid")
        }
        try:
            Analysts = AnalystService.read_analyst(filters)
            AnalystsMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}" for i, b in enumerate(Analysts, start=1)])
            if not AnalystsMsg:
                await update.message.reply_text("No hay analistas registrados/activos")
                return ConversationHandler.END
            await update.message.reply_text(f"Los analistas de la empresa {selected_contractor.get('name')} son:\n{AnalystsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando analistas. {e}")
        finally:
            return ConversationHandler.END


    read_analyst_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("listar_analistas", PreguntarContratistaLA)],
        states={
            LA_OBT_CONTRATISTA:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerContratistaLA)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para crear Analistas
    #
    @staticmethod
    async def PreguntarContratistaCA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
        await update.message.reply_text(f"¿A cuál contratista va a pertenecer el analista?")
        return OperationController.CA_OBT_CONTRATISTA
    
    @staticmethod
    async def ObtenerContratistaCA(update : Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            contractors = context.user_data.get("contractors", [])
            if choice < 1 or choice > len(contractors):
                raise ValueError
            selected_contractor = contractors[choice - 1]
            context.user_data["contractorid"] = selected_contractor.get("contractorid")
            await update.message.reply_text(
                f"Contratista seleccionado: {selected_contractor['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CA_OBT_CONTRATISTA
        await update.message.reply_text(
            text="A continuación, te pediré la información del analista\nEscribe el *nombre* (posterior me darás su apellido)",
            parse_mode="Markdown"
        )
        return OperationController.CA_OBT_NOMBRE

    @staticmethod
    async def ObtenerNombreCA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        firstname = update.message.text
        context.user_data["firstname"] = firstname
        await update.message.reply_text(f"✅ Nombre adquirido: {firstname}")
        await update.message.reply_text(
            text="Escribe el *apellido*",
            parse_mode="Markdown"
        )
        return OperationController.CA_OBT_APELLIDO
    
    @staticmethod
    async def ObtenerApellidoCA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        lastname = update.message.text
        context.user_data["lastname"] = lastname
        await update.message.reply_text(f"✅ Apellido adquirido: {lastname}")
        payload = {
            "lastname": lastname,
            "firstname": context.user_data["firstname"],
            "contractorid": context.user_data["contractorid"]
        }
        try:
            req = AnalystService.create_analyst(payload)
            analyst = req.get("analyst")
            await update.message.reply_text(f"Nombre: {analyst.get("firstname")} {analyst.get("lastname")}\nUsuario: {analyst.get("username")}\nContraseña: {analyst.get("password")}")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}.")
        finally:
            return ConversationHandler.END

    create_analyst_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_analista", PreguntarContratistaCA)],
        states={
            CA_OBT_CONTRATISTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerContratistaCA)],
            CA_OBT_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNombreCA)],
            CA_OBT_APELLIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerApellidoCA)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para borrar Analistas
    #
    @staticmethod
    async def PreguntarContratistaBA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END  
        try:
            contractors = ContractorService.read_contractor(True)
            contractorsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(contractors, start=1)])
            await update.message.reply_text(f"Los contratistas a disposición son:\n{contractorsMsg}")
            context.user_data['contractors'] = contractors
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando contratistas. {e}")
            return ConversationHandler.END
        await update.message.reply_text(f"¿A cuál contratista pertenece el analista?")
        return OperationController.BA_OBT_CONTRATISTA
    
    @staticmethod
    async def ObtenerContratistaBA(update : Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            contractors = context.user_data.get("contractors", [])
            if choice < 1 or choice > len(contractors):
                raise ValueError
            selected_contractor = contractors[choice - 1]
            context.user_data["contractor"] = selected_contractor
            await update.message.reply_text(
                f"Contratista seleccionado: {selected_contractor['name']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CA_OBT_CONTRATISTA
        filters = {
            "isactive": True,
            "contractor": selected_contractor.get("contractorid")
        }
        try:
            Analysts = AnalystService.read_analyst(filters)
            context.user_data["analysts"] = Analysts
            AnalystsMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}" for i, b in enumerate(Analysts, start=1)])
            if not AnalystsMsg:
                await update.message.reply_text("No hay analistas registrados/activos")
                return ConversationHandler.END
            await update.message.reply_text(f"Los analistas de la empresa {selected_contractor.get('name')} son:\n{AnalystsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando analistas. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿Cuál analista vas a borrar?")
        return OperationController.BA_OBT_ANALISTA

    @staticmethod
    async def ObtenerAnalistaBA(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            analysts = context.user_data.get("analysts", [])
            if choice < 1 or choice > len(analysts):
                raise ValueError
            selected_analyst = analysts[choice - 1]
            await update.message.reply_text(
                f"Contratista seleccionado: {selected_analyst['firstname']} {selected_analyst['lastname']}"
            )
        except:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.BA_OBT_CONTRATISTA
        contractor = context.user_data["contractor"]
        payload = {
            "isactive":False 
        }
        try:
            AnalystService.update_analyst(selected_analyst.get("id"), payload)
            await update.message.reply_text("✅ Analista borrado exitosamente")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error borrando analista. {e}")
            return ConversationHandler.END
        filters = {
            "isactive": True,
            "contractor": context.user_data["contractor"].get("contractorid")
        }
        try:
            Analysts = AnalystService.read_analyst(filters)
            AnalystsMsg = "\n".join([f"{i}. {b['firstname']} {b['lastname']}" for i, b in enumerate(Analysts, start=1)])
            if not AnalystsMsg:
                await update.message.reply_text("No hay analistas registrados/activos")
                return ConversationHandler.END
            await update.message.reply_text(f"Los analistas de la empresa {contractor.get('name')} son:\n{AnalystsMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando analistas. {e}")
        finally:
            return ConversationHandler.END

    delete_analyst_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_analista",PreguntarContratistaBA)],
        states={
            BA_OBT_CONTRATISTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerContratistaBA)],
            BA_OBT_ANALISTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerAnalistaBA)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para crear nodos
    #
    @staticmethod
    async def PreguntarDepartamentoCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] != "admin":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento está ubicado el nodo?")
        return OperationController.CN_OBT_DEPT
    
    @staticmethod
    async def ObtenerDepartamentoCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CN_OBT_DEPT
        try:
            municipalities = MunicipalityService.read_municipality(selected_department.get('departmentid'))
            context.user_data["municipalities"] = municipalities
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {selected_department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál municipio se ubica el nodo?")
        return OperationController.CN_OBT_MUN
    
    @staticmethod
    async def ObtenerMunicipioCN(update: Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            municipalities = context.user_data.get("municipalities", [])
            if choice < 1 or choice > len(municipalities):
                raise ValueError
            selected_municipality = municipalities[choice - 1]
            context.user_data["municipality"] = selected_municipality
            await update.message.reply_text(
                f"✅ Municipio seleccionado: {selected_municipality['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CN_OBT_MUN
        await update.message.reply_text("Digita el código de ingeniería del nodo")
        return OperationController.CN_OBT_COD
    
    @staticmethod
    async def ObtenerCodigoCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        code = update.message.text
        if len(code) != 5:
            await update.message.reply_text("❌ Código no válido, debe contar con 5 dígitos")
            return OperationController.CN_OBT_COD
        context.user_data["code"] = code
        await update.message.reply_text(f"✅ código adquirido: {code}")
        await update.message.reply_text(
            text="Escribe la dirección del nodo (ubicación física)",
            parse_mode="Markdown"
        )
        return OperationController.CN_OBT_DIR
    
    @staticmethod
    async def ObtenerDireccionFisicaCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        direction = update.message.text
        context.user_data["direction"] = direction
        await update.message.reply_text(f"✅ dirección adquirida: {direction}")
        await update.message.reply_text(
            text="¿El nodo cuenta con rectificador?\n1. Sí\n2. No",
            parse_mode="Markdown"
        )
        return OperationController.CN_PRE_IPV4
    
    @staticmethod
    async def PreguntarDireccionGestionCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            if choice == 1:
                await update.message.reply_text("Escribe la dirección de gestión del rectificador")
                context.user_data["hasrectifier"] = True
                return OperationController.CN_OBT_IPV4
            elif choice == 2:
                if context.user_data.get("name") is None:
                    payload = {
                        "hasrectifier": False,
                        "ipaddress": "NO APLICA",
                        "code": context.user_data.get("code"),
                        "isactive": True,
                        "municipalityid": context.user_data["municipality"].get("municipalityid"),
                        "description": context.user_data.get("direction")
                    }
                    try:
                        NodeService.create_node(payload)
                        await update.message.reply_text("✅ Nodo creado exitosamente")
                    except Exception as e:
                        await update.message.reply_text(f"❌ {e}.")
                    payload = {
                        "municipality": context.user_data["municipality"].get("municipalityid"),
                        "isactive": True
                    }
                    try:
                        nodes = NodeService.read_node(payload)
                        nodesMsg = "\n".join([f"{i}. {b['code']} dirección de gestión: {b['ipaddress']}" for i, b in enumerate(nodes, start=1)])
                        await update.message.reply_text(f"Los nodos del municipio {context.user_data["municipality"].get("name")} son:\n{nodesMsg}")
                    except Exception as e:
                        await update.message.reply_text(f"❌ {e}.")
                    finally:
                        return ConversationHandler.END
            else:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Selección inválida. Por favor ingresa un número de la lista.")
            return ConversationHandler.END
        
    @staticmethod
    async def ObtenerDireccionGestionCN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        ipaddress = update.message.text
        await update.message.reply_text(f"✅ dirección de gestión adquirida: {ipaddress}")
        payload = {
            "hasrectifier": True,
            "ipaddress": ipaddress,
            "code": context.user_data.get("code"),
            "isactive": True,
            "municipalityid": context.user_data["municipality"].get("municipalityid"),
            "description": context.user_data.get("direction")
        }
        try:
            NodeService.create_node(payload)
            await update.message.reply_text("✅ Nodo creado exitosamente")
            payload = {
                "municipality": context.user_data["municipality"].get("municipalityid")
            }
            nodes = NodeService.read_node(payload)
            nodesMsg = "\n".join([f"{i}. {b['code']} dirección de gestión: {b['ipaddress']}" for i, b in enumerate(nodes, start=1)])
            await update.message.reply_text(f"Los nodos del municipio {context.user_data["municipality"].get("name")} son:\n{nodesMsg}")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}.")
        finally:
            return ConversationHandler.END
    
    create_node_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("crear_nodo",PreguntarDepartamentoCN)],
        states={
            CN_OBT_DEPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoCN)],
            CN_OBT_MUN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerMunicipioCN)],
            CN_OBT_COD : [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerCodigoCN)],
            CN_OBT_DIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDireccionFisicaCN)],
            CN_PRE_IPV4: [MessageHandler(filters.TEXT & ~filters.COMMAND, PreguntarDireccionGestionCN)],
            CN_OBT_IPV4: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDireccionGestionCN)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para listar nodos
    #
    @staticmethod
    async def PreguntarDepartamentoLN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento vas a consultar los nodos?")
        return OperationController.CN_OBT_DEPT
    
    @staticmethod
    async def ObtenerDepartamentoLN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CN_OBT_DEPT
        try:
            municipalities = MunicipalityService.read_municipality(selected_department.get('departmentid'))
            context.user_data["municipalities"] = municipalities
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {selected_department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál municipio vas a consultar los nodos?")
        return OperationController.CN_OBT_MUN
    
    @staticmethod
    async def ObtenerMunicipioLN(update: Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            municipalities = context.user_data.get("municipalities", [])
            if choice < 1 or choice > len(municipalities):
                raise ValueError
            selected_municipality = municipalities[choice - 1]
            await update.message.reply_text(
                f"✅ Municipio seleccionado: {selected_municipality['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.CN_OBT_MUN
        payload = {
            "municipality": selected_municipality.get("municipalityid"),
            "isactive": True
        }
        try:
            nodes = NodeService.read_node(payload)
            nodesMsg = "\n".join([f"{i}. {b['code']} dirección de gestión: {b['ipaddress']}" for i, b in enumerate(nodes, start=1)])
            if not nodesMsg:
                nodesMsg = "No hay nodos en este municipio"
            await update.message.reply_text(f"Los nodos del municipio {selected_municipality.get("name")} son:\n{nodesMsg}")
        except Exception as e:
            await update.message.reply_text(f"❌ {e}.")
        finally:
            return ConversationHandler.END
    
    read_node_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("listar_nodos",PreguntarDepartamentoLN)],
        states={
            LN_OBT_DEPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoLN)],
            LN_OBT_MUN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerMunicipioLN)],
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
    #
    # Conversación para borrar nodos
    #
    @staticmethod
    async def PreguntarDepartamentoBN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        if not AuthController.IsAuthenticated(context):
            await update.message.reply_text("⚠️ Autenticate primero.")
            return ConversationHandler.END     
        if context.user_data["permission"] == "user":
            await update.message.reply_text("⚠️ No tienes permiso de usar esta función.")
            return ConversationHandler.END
        try:
            departments = DepartmentService.read_department()
            DepartmentsMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(departments, start=1)])
            await update.message.reply_text(f"Los departamentos disponibles son:\n{DepartmentsMsg}")
            context.user_data["departments"] = departments
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando departamentos. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál departamento está el nodo que vas a borrar?")
        return OperationController.BN_OBT_DEPT
    
    @staticmethod
    async def ObtenerDepartamentoBN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            departments = context.user_data.get("departments", [])
            if choice < 1 or choice > len(departments):
                raise ValueError
            selected_department = departments[choice - 1]
            await update.message.reply_text(
                f"✅ Departamento seleccionado: {selected_department['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.BN_OB
        try:
            municipalities = MunicipalityService.read_municipality(selected_department.get('departmentid'))
            context.user_data["municipalities"] = municipalities
            municipalityMsg = "\n".join([f"{i}. {b['name']}" for i, b in enumerate(municipalities, start=1)])
            await update.message.reply_text(f"Los municipios del departamento {selected_department.get('name')} son:\n{municipalityMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando municipios. {e}")
            return ConversationHandler.END
        await update.message.reply_text("¿En cuál municipio está el nodo que vas a borrar?")
        return OperationController.BN_OBT_MUN
    
    @staticmethod
    async def ObtenerMunicipioBN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            municipalities = context.user_data.get("municipalities", [])
            if choice < 1 or choice > len(municipalities):
                raise ValueError
            selected_municipality = municipalities[choice - 1]
            context.user_data["municipality"] = selected_municipality
            await update.message.reply_text(
                f"✅ Municipio seleccionado: {selected_municipality['name']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.BN_OBT_MUN
        filters = {
            "isactive": True,
            "municipality": selected_municipality.get("municipalityid")
        }
        try:
            nodes = NodeService.read_node(filters)
            context.user_data["nodes"] = nodes
            NodesMsg = "\n".join([f"{i}. {b['code']}" for i, b in enumerate(nodes, start=1)])
            await update.message.reply_text(f"Los nodos del municipio {selected_municipality.get('name')} son:\n{NodesMsg}")
            await update.message.reply_text("¿cuál nodo vas a borrar?")
            return OperationController.BN_OBT_NODO
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando nodos. {e}")
            return ConversationHandler.END
         
    @staticmethod
    async def ObtenerNodoBN(update : Update, context : ContextTypes.DEFAULT_TYPE):
        try:
            choice = int(update.message.text)
            nodes = context.user_data.get("nodes", [])
            if choice < 1 or choice > len(nodes):
                raise ValueError
            selected_node = nodes[choice - 1]
            await update.message.reply_text(
                f"✅ Nodo seleccionado: {selected_node['code']}"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Selección inválida. Por favor ingresa un número de la lista."
            )
            return OperationController.BN_OBT_NODO
        payload = {
            "isactive":False
        }
        try:
            req = NodeService.update_node(selected_node.get("nodeid"), payload)
            await update.message.reply_text("✅ Nodo borrado exitosamente")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error borrando nodo. {e}")
        filters = {
            "isactive": True,
            "municipality": context.user_data["municipality"].get("municipalityid")
        }
        try:
            nodes = NodeService.read_node(filters)
            context.user_data["nodes"] = nodes
            NodesMsg = "\n".join([f"{i}. {b['code']}" for i, b in enumerate(nodes, start=1)])
            if not NodesMsg:
                NodesMsg = "No hay nodos en este municipio"
            await update.message.reply_text(f"Los nodos del municipio {context.user_data["municipality"].get("name")} son:\n{NodesMsg}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error consultando nodos. {e}")
        finally:
            return ConversationHandler.END
        
    delete_node_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_nodo", PreguntarDepartamentoBN)],
        states = {
            BN_OBT_DEPT:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerDepartamentoBN)],
            BN_OBT_MUN:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerMunicipioBN)],
            BN_OBT_NODO:[MessageHandler(filters.TEXT & ~filters.COMMAND, ObtenerNodoBN)]
        },
        fallbacks=[CommandHandler("cancel", CancelConversation)]
    )
#
# EOF
#