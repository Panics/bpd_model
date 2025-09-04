from Helpers.AbstractTreatment import AbstractTreatment
from Helpers.ImuData import ImuData
import numpy as np

class BPDTreatment1(AbstractTreatment):
     _KGAMMA:float = 0.5        # IMU scaling
     _GAMMA_MAX:float = 5.0     # Bound treatment effect

     def CalculateTreatmentEffect(self, imuData:ImuData)->float :
        treatmentMapped:float = -1 + 2 * imuData.xAngle
        treatmentEffect:float = np.clip(treatmentMapped*self._KGAMMA, -self._GAMMA_MAX, self._GAMMA_MAX)
        return treatmentEffect