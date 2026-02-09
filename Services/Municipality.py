from Models.Department import Department
from Models.Municipality import Municipality
from Services.BaseService import BaseService

class MunicipalityService(BaseService):

    def __init__(self, context):
        super().__init__(context)
        self.endpoint = "/municipalities/"
    
    async def read(self, department : Department | None = None) -> list[Municipality]:
        params = {}
        if Municipality:
            params["department"] = department.ID
        return await super().read(params)

    async def create(self, municipality : Municipality):
        return await super().create(municipality)

    async def update(self, municipality : Municipality):
        return await super().update(municipality)

    def _to_object(self, data : dict) -> Municipality:
        DeptDict = data.get('item')
        return Municipality(
            dept=Department(DeptDict.get('name'),DeptDict.get('departmentid')),
            ID=data.get('municipalityid'),
            name=data.get('name'),
            dane=data.get('dane')
        )

#
# EOF
#