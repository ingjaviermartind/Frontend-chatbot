import requests
from Models.Config import Configuration

class MunicipalityService:

    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/municipalities/"
    # API_TOKEN = "83bbc88691202926bb2a6c8d71f9aa63075c9ef1"
    # API_BASE = "http://10.142.12.61:8000/api/municipalities/"
    @staticmethod
    def create_municipality(Name : str, Dane : int, DeptID : int):
        payload = {
            "name": Name,
            "dane": Dane,
            "departmentid": DeptID
        }
        response = requests.post(
            MunicipalityService.API_BASE,
            # headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 201:
            return response.json()

        if response.status_code == 400:
            error = response.json()
            raise Exception(error.get("name", ["Error creando municipio"])[0])

    @staticmethod
    def update_municipality(Name : str = None, Dane : int = None, MunID : int = None):
        payload = {}
        if Name is not None:
            payload["name"] = Name
        if Dane is not None: 
            payload["dane"] = Dane
        response = requests.patch(
            f"{MunicipalityService.API_BASE}{MunID}/",
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error ({response.status_code})")
        return response.json()

    @staticmethod
    def delete_municipality():
        pass
    
    @staticmethod
    def read_municipality(deptid : int = None) -> dict:
        # headers = {
        #     "Authorization": f"Token {MunicipalityService.API_TOKEN}",
        # }
        params = {}
        if deptid:
            params = {"department": deptid}
        response = requests.get(
            MunicipalityService.API_BASE,
            #headers=headers,
            params=params,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception("Error consultando municipios")
        return response.json()
    #
    # EOF
    #