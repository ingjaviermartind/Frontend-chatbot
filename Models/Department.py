import requests
from urllib.parse import urljoin
from Models.Config import Configuration
from Models.Object import BaseObject

class Department(BaseObject):
    def __init__(self, name : str, ID : int | None = None):
        super().__init__(ID)
        self._name = name

    @property
    def Name(self) -> str:
        return self._name
    
    def to_payload(self):
        return {
            "name": self.Name
        }

class DepartmentService:

    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/departments/"
    #API_BASE = "http://10.142.12.61:8000/api/departments/"
    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"

    @staticmethod
    def create_department():
        pass

    @staticmethod
    def update_department():
        pass

    @staticmethod
    def delete_department():
        pass
    
    @staticmethod
    def read_department(contractorid : int = None) -> dict:
        # headers = {
        #     "Authorization": f"Token {DepartmentService.API_TOKEN}",
        # }
        params = {}
        if contractorid:
            params = {"contractor": contractorid}
        response = requests.get(
            DepartmentService.API_BASE,
            # headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception("Error consultando departamentos")
        return response.json()