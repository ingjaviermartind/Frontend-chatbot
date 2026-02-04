import requests
from Models.Config import Configuration

class NodeService:


    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    # API_BASE = "http://10.142.12.61:8000/api/nodes/"
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/nodes/"

    @staticmethod
    def create_node(payload : dict) -> dict:
        response = requests.post(
            NodeService.API_BASE,
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
    def update_node(NodeID : int, payload : dict) -> dict:
        response = requests.patch(
            f"{NodeService.API_BASE}{NodeID}/",
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

    @staticmethod
    def delete_node():
        pass
    
    @staticmethod
    def read_node(filters : dict = {}) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        response = requests.get(
            NodeService.API_BASE,
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