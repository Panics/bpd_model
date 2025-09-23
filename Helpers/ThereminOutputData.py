

import numpy as np

# ------------------------------------------------------------------------------------------------------------
class ThereminOutputData:
    # ------------------------------------------------------------------------------------------------------------
    _frequency:float
    _volume:float

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Frequency(self):
        return self._frequency
    
    @Frequency.setter
    def Frequency(self, val):
        self._frequency = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Volume(self):
        return self._volume
    
    @Volume.setter
    def Volume(self, val):
        self._volume = val

    # ------------------------------------------------------------------------------------------------------------
    def __init__(self, frequency:float=0, volume:float=0):
        self._frequency = frequency
        self._volume = volume
        