from abc import abstractmethod
from Helpers.ModelOutputData import ModelOutputData

class AbstractModel:
    # --------------------------
    # State variables
    # --------------------------
    _modelState:ModelOutputData = ModelOutputData()

    # --------------------------
    # State variable Property Getters
    # --------------------------
    @property
    def ModelState(self):
        return self._modelState
    
    @abstractmethod
    def step(self, treatmentEffect:float, DT:float=0.04):
        pass