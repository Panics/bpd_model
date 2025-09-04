
import numpy as np

# ------------------------------------------------------------------------------------------------------------
class ModelOutputData:
    # ------------------------------------------------------------------------------------------------------------
    _bpdMood:float
    _bpdMoodVelocity:float
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
    def BpdMoodVelocity(self):
        return self._bpdMoodVelocity
    
    @BpdMoodVelocity.setter
    def BpdMoodVelocity(self, val):
        self._bpdMoodVelocity = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def BpdTreatmentEffect(self):
        return self._bpdTreatmentEffect
    
    @BpdTreatmentEffect.setter
    def BpdTreatmentEffect(self, val):
        self._bpdTreatmentEffect = val

    # ------------------------------------------------------------------------------------------------------------
    def __init__(self, mood:float=0, moodVelocity:float=0, treatmentEffect:float=0):
        self._bpdMood = mood
        self._bpdMoodVelocity = moodVelocity
        self._bpdTreatmentEffect = treatmentEffect
        