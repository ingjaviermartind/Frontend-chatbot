import requests
import base64
from Models.Config import Configuration

class EntryService:
            
    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/entries/"
    
    @staticmethod 
    def ImgTob64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @staticmethod
    def create_Entry(payload : dict) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        url = f"{EntryService.API_BASE}"
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
    def update_Entry(EntryID : int, IsActive : bool = None, ExitID : int = None):
        if IsActive is not None and ExitID is not None:
            payload = {
                "isactive": str(IsActive).lower(),
                "exitid": ExitID,
            }
            response = requests.patch(
                f"{EntryService.API_BASE}{EntryID}/",
                json=payload,
                timeout=10
            )
            if response.status_code != 200:
                raise Exception(f"Error editando ingreso ({response.status_code})")
            return response.json()

    @staticmethod
    def delete_Entry():
        pass

    @staticmethod
    def read_Entry(IsActive : bool = None, Municipality : int = None, Department : int = None, Contractor : int = None, date = None):
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        params = {}
        if IsActive is not None:
            params["isactive"] = str(IsActive).lower()
        if Municipality is not None:
            params["municipality"] = Municipality
        if Department is not None:
            params["department"] = Department
        if Contractor is not None:
            params["contractor"] = Contractor
        if date is not None:
            params["date"] = date
        response = requests.get(
            EntryService.API_BASE,
            # headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error consultando ingresos ({response.status_code})")
        return response.json()
#
# EOF
#  