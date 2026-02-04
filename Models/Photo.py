import requests
import base64
from Models.Config import Configuration

class PhotoService:
            
    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/photos/"
    
    @staticmethod 
    def ImgTob64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def create_photo(payload : dict) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        url = f"{PhotoService.API_BASE}"
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
    def update_photo():
        pass

    @staticmethod
    def delete_photo():
        pass

    @staticmethod
    def read_photo():
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        params = {}
        response = requests.get(
            PhotoService.API_BASE,
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