import requests
from Models.Config import Configuration

class CrewService():
    
    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/crews/"

    @staticmethod
    def create_crew(ContractorID : int, name : str):
        payload = {
            "name": name.strip(),
            "isactive": True,
            "contractorid": ContractorID
        }
        response = requests.post(
            CrewService.API_BASE,
            # headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 201:
            return response.json()

        if response.status_code == 400:
            error = response.json()
            raise Exception(error.get("name", ["Error creando cuadrilla"])[0])

    @staticmethod
    def update_crew(CrewID : int, isActive : bool = False):
        payload = {
            "isactive" : isActive
        }
        response = requests.patch(
            f"{CrewService.API_BASE}{CrewID}/",
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error ({response.status_code})")
        return response.json()

    @staticmethod
    def delete_crew():
        pass

    @staticmethod
    def read_crew(Contractor : int = None, isactive : bool = None) -> dict:
        # headers = {
        #     "Authorization": f"Token {NodeService.API_TOKEN}",
        # }
        params = {}
        if Contractor is not None:
            params["contractor"] = Contractor
        if isactive is not None:
            params["isactive"] = str(isactive).lower()
        response = requests.get(
            CrewService.API_BASE,
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