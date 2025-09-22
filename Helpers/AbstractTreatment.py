from abc import abstractmethod
from Helpers.ImuData import ImuData

class AbstractTreatment:
   # ------------------------------------------------------------------------------------------------------------
   _treatment_scale:float = 0.01

   # ------------------------------------------------------------------------------------------------------------
   @property
   def TreatmentScale(self):
      return self._treatment_scale
    
   @TreatmentScale.setter
   def TreatmentScale(self, val):
      self._treatment_scale = val

   # ------------------------------------------------------------------------------------------------------------
   # Constructor
   def __init__(self, TreatmentScale:float=0.01):
      self._treatment_scale = TreatmentScale

   # ------------------------------------------------------------------------------------------------------------
   # Abstract method to calculate treatment effect based on IMU state data
   @abstractmethod
   def CalculateTreatmentEffect(self, imuData:ImuData)->float :
      pass

   # ------------------------------------------------------------------------------------------------------------
   # Method to handle keypress
   def on_key(self, event):
      pass
