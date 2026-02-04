import requests
import base64
from Models.Config import Configuration

class ExitService:
            
    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/exits/"
    
    @staticmethod 
    def ImgTob64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def create_exit(payload : dict) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        url = f"{ExitService.API_BASE}"
        response = requests.post(
            url,
            # headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code != 201:
            raise Exception(f"Error creando la bitácora ({response.status_code})")
        return response.json()

    @staticmethod
    def update_entry():
        pass

    @staticmethod
    def delete_entry():
        pass

    @staticmethod
    def read_entry():
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        params = {}
        response = requests.get(
            ExitService.API_BASE,
            # headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error consultando cierres ({response.status_code})")
        return response.json()
#
# EOF
#  