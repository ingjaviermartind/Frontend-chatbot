from abc import ABC
from ApiClient.ApiClient import ApiClient
from Models.Object import BaseObject

class BaseService(ABC):

    endpoint = ""

    def __init__(self, context):
        self.api = ApiClient(context)
    
    async def read(self, params=None):
        response = await self.api.get(self.endpoint, params=params)
        data = response.json()
        return [self._to_object(item) for item in data]

    async def create(self, Object : BaseObject):
        response = await self.api.post(self.endpoint, json=Object.to_payload())
        return self._to_object(response.json())

    #async def update(self, )

    def _to_object(self, data : dict):
        raise NotImplementedError

#
# EOF
#