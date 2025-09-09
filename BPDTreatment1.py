from Helpers.AbstractTreatment import AbstractTreatment
from Helpers.ImuData import ImuData
import numpy as np

class BPDTreatment1(AbstractTreatment):
     _KGAMMA:float = 0.015        # IMU scaling
     _GAMMA_MAX:float = 5.0     # Bound treatment effect

     def CalculateTreatmentEffect(self, imuData:ImuData)->float :
        treatmentEffect:float = np.clip(imuData.xAngle*self._KGAMMA, -self._GAMMA_MAX, self._GAMMA_MAX)
        return treatmentEffect