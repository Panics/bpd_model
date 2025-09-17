
import numpy as np

# ------------------------------------------------------------------------------------------------------------
class ModelOutputData:
    # ------------------------------------------------------------------------------------------------------------
    _bpdMood:float
    _bpdTreatmentEffect:float

    # ------------------------------------------------------------------------------------------------------------
    @property
    def BpdMood(self):
        return self._bpdMood
    
    @BpdMood.setter
    def BpdMood(self, val):
        self._bpdMood = np.clip(val, -1, 1)

    # ------------------------------------------------------------------------------------------------------------
    @property
    def BpdTreatmentEffect(self):
        return self._bpdTreatmentEffect
    
    @BpdTreatmentEffect.setter
    def BpdTreatmentEffect(self, val):
        self._bpdTreatmentEffect = val

    # ------------------------------------------------------------------------------------------------------------
    def __init__(self, mood:float=0, treatmentEffect:float=0):
        self._bpdMood = mood
        self._bpdTreatmentEffect = treatmentEffect
        