from abc import ABC, abstractmethod

class Worker:
    def __init__(self, data : dict):
        self._firstname = data.get("firstname")
        self._lastname = data.get("lastname")
        self._contractor = data.get("contractor")
        self._id = data.get("id")
        self._contractorid = data.get("contractorid")
    @property
    def Fullname(self) -> str:
        return f"{self._firstname} {self._lastname}"
    @property
    def Firstname(self) -> str:
        if not self._firstname:
            return ""
        name : str = self._firstname
        return name.split()[0]
    @property
    def First_LastName(self) -> str:
        if not self._lastname:
            return ""
        lastname : str = self._lastname
        return lastname.split()[0]
    @property
    def Contractor(self) -> str:
        return self._contractor
    @property
    def ContractorID(self) -> int:
        return self._contractorid
    @property
    def getID(self) -> int:
        return self._id

    @property
    @abstractmethod 
    def Role(self) -> str:
        pass


