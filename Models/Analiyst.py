from Models.Worker import Worker
import requests
from Models.Config import Configuration

class AnalystWorker (Worker):

    def __init__(self, data : dict):
        super().__init__(data)

    @property    
    def Role(self):
        return "Analista"
    
class AnalystService ():
    
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/analysts/"

    @staticmethod
    def create_analyst(payload : dict):
        response = requests.post(
            f"{AnalystService.API_BASE}create-with-user/",
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
    def read_analyst(filters : dict):
        response = requests.get(
            AnalystService.API_BASE,
            # headers=headers,
            params=filters,
            timeout=10
        )
        if response.status_code != 200:
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
    def update_analyst(AnalystID : int, payload : dict):
        response = requests.patch(
            f"{AnalystService.API_BASE}{AnalystID}/",
            # headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
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


#
# EOF
#