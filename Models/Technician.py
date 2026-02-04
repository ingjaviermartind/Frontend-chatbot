from Models.Worker import Worker
import requests
from Models.Config import Configuration

class TechnicianWorker (Worker):

    def __init__(self, data : dict):
        super().__init__(data)
        self._cc = data.get("cc")
        self._cellphone = data.get("cellphone")
        self._crew = data.get('crew')
        self._crewid = data.get('crewid')


    @property
    def Role(self):
        return "Técnico"
    
    @property
    def Cedula(self):
        return self._cc
    
    @property
    def Telefono(self):
        return self._cellphone
    
    @property
    def Cuadrilla(self):
        return self._crew
    
    @property
    def TechID(self):
        return self._techid
    
    @property
    def CuadrillaID(self):
        return self._crewid
    
    

class TechnicianService:
     
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/technicians/"

    @staticmethod
    def create_technician(payload : dict):
        response = requests.post(
            f"{TechnicianService.API_BASE}create-with-user/",
            json=payload,
            timeout=10
        )
        if response.status_code != 201:
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    if "message" in error_data:
                        error_message = error_data["message"]
                    elif "non_field_errors" in error_data:
                        error_message = error_data["non_field_errors"][0]
                    else:
                        field, messages = next(iter(error_data.items()))
                        error_message = f"{field}: {messages[0]}"
                else:
                    error_message = "Error desconocido"
            except ValueError:
                error_message = "Respuesta inválida del servidor"
            raise Exception(
                f"Error {response.status_code}: {error_message}"
            )
        return response.json()

    @staticmethod
    def update_technician(TechnicianID : int ,isActive : bool = False):
        payload = {
            "isactive" : str(isActive).lower()
        }
        response = requests.patch(
            f"{TechnicianService.API_BASE}{TechnicianID}/",
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error ({response.status_code}: {response.text})")
        return response.json()

    @staticmethod
    def delete_technician():
        pass

    @staticmethod
    def read_technician(Contractor : int = None, Crew : int = None, isactive : bool = None) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        params = {}
        if Contractor is not None:
            params["contractor"] = Contractor
        if Crew is not None:
            params["crew"] = Crew
        if isactive is not None:
            params["isactive"] = str(isactive).lower()
            
        response = requests.get(
            TechnicianService.API_BASE,
            # headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error consultando nodos ({response.status_code})")
        return response.json()
#
# eof
#