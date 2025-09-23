from abc import abstractmethod
from Helpers.ModelOutputData import ModelOutputData

class AbstractModel:
    # --------------------------
    # State variables
    # --------------------------
    _modelState:ModelOutputData

    # --------------------------
    # State variable Property Getters
    # --------------------------
    @property
    def ModelState(self):
        return self._modelState
    
    # --------------------------
    # Abstract method to update the model state
    # --------------------------
    @abstractmethod
    def step(self, treatmentEffect:float, DT:float=0.04):
        pass

    # --------------------------
    # Method to handle key press
    # --------------------------
    def on_key(self, event:str):
        pass

    def print_key_info(self):
        pass

    # --------------------------
    # Constructor
    # --------------------------
    def __init__ (self, mood:float=0, treatmentEffect:float=0):
        self._modelState = ModelOutputData(mood, treatmentEffect)