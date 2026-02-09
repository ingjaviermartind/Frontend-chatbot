import requests
from ApiClient.Config import Configuration
from Models.Contractor import Contractor
from Services.BaseService import BaseService
    
class ContractorService(BaseService):

    def __init__(self, context):
        super().__init__(context)

    
    #
    # EOF
    #