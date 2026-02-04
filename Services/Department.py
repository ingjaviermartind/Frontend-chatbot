from Models.Department import Department
from Models.Contractor import Contractor
from Services.BaseService import BaseService

class DepartmentService(BaseService):

    def __init__(self, context):
        super().__init__(context)
        self.endpoint = "/departments/"
    
    async def read(self, contractor : Contractor | None = None) -> list[Department]:
        params = {}
        if contractor:
            params["contractor"] = contractor.ID
        return await super().read(params)

    async def create(self, dept : Department):
        return await super().create(dept)

    def _to_object(self, data : dict) -> Department:
        return Department(
            ID=data.get('departmentid'),
            name=data.get('name')
        )

#
# EOF
#