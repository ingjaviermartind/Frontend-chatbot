from abc import ABC, abstractmethod

class Place:
    def __init__(self, name : str):
        self._name = name
    @property
    def getName(self) -> str:
        return self._name
    
class PlaceDepartment(Place):
    def __init__(self, name : str, item : dict):
        super().__init__(name)
        
class PlaceMunicipality(Place):
    def __init__(self, name : str, dane, item : dict):
        super().__init__(name)
        self._dane = dane
        self._department = PlaceDepartment(item.get('name'), item.get('item'))
    @property
    def getDane(self):
        return self._dane
    @property
    def getDepartmentName(self) -> str:
        return self._department.getName
#
# eof
#