from abc import abstractmethod
from Helpers.ImuData import ImuData

class AbstractTreatment:
    
    @abstractmethod
    def CalculateTreatmentEffect(self, imuData:ImuData)->float :
        pass