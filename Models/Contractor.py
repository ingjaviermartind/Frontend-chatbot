from abc import ABC, abstractmethod
import requests
from Models.Config import Configuration
from Models.Object import BaseObject

class Contractor(BaseObject):
    def __init__(self, name : str, ID : int):
        super().__init__(ID)
        self._name = name

    @property
    def Name(self) -> str:
        return self._name
    
class ContractorService:

    API_BASE = f"http://{Configuration.getServer()}:{Configuration.getPort()}/api/contractors/"

    @staticmethod
    def create_contractor(Name : str, isAactive : bool = True):
        payload = {
            "name": Name,
            "isactive": isAactive
        }
        response = requests.post(
            ContractorService.API_BASE,
            # headers=headers,
            json=payload,
            timeout=10
        )
        if response.status_code == 201:
            return response.json()

        if response.status_code == 400:
            error = response.json()
            raise Exception(error.get("name", ["Error creando contratista"])[0])

    @staticmethod
    def update_contractor(ContractorID : int = None, isActive : bool = False):
        payload = {
            "isactive": isActive
        }
        response = requests.patch(
            f"{ContractorService.API_BASE}{ContractorID}/",
            json=payload,
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Error ({response.status_code})")
        return response.json()

    @staticmethod
    def delete_contractor():
        pass
    
    @staticmethod
    def read_contractor(isActive : bool = None) -> dict:
        # headers = {
        #     "Authorization": f"Token {MunicipalityService.API_TOKEN}",
        # }
        params = {}
        if isActive is not None:
            params = {"isactive": isActive}
        response = requests.get(
            ContractorService.API_BASE,
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