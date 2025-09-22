from Helpers.AbstractTreatment import AbstractTreatment
from Helpers.ImuData import ImuData

class BPDTreatment1(AbstractTreatment):
   # ------------------------------------------------------------------------------------------------------------
   _x_angle_ratio:float = 0.5             # IMU scaling
   _x_angle_velocity_ratio:float = 0.0    # IMU scaling
 
   # ------------------------------------------------------------------------------------------------------------
   @property
   def XAngleRatio(self):
      return self._x_angle_ratio
    
   @XAngleRatio.setter
   def XAngleRatio(self, val):
      self._x_angle_ratio = val

   # ------------------------------------------------------------------------------------------------------------
   @property
   def XAngleVelocityRatio(self):
      return self._x_angle_velocity_ratio
    
   @XAngleVelocityRatio.setter
   def XAngleVelocityRatio(self, val):
      self._x_angle_velocity_ratio = val

   # ------------------------------------------------------------------------------------------------------------
   def __init__(self, XAngleRatio:float = 0.5, XAngleVelocityRatio:float=0, TreatmentScale:float=0.01):
      super().__init__(TreatmentScale=TreatmentScale)
      self._x_angle_ratio = XAngleRatio
      self._x_angle_velocity_ratio = XAngleVelocityRatio

   # ------------------------------------------------------------------------------------------------------------
   def CalculateTreatmentEffect(self, imuData:ImuData)->float :
      treatmentEffect:float = self.TreatmentScale * (imuData.xAngle*self._x_angle_ratio + imuData.xAccelAngle*self._x_angle_velocity_ratio)
      return treatmentEffect
   
   # ------------------------------------------------------------------------------------------------------------
   def on_key(self, event):
      
      if event.key == 'k': self.TreatmentScale = max(0.0, self.TreatmentScale - 0.0005)
      elif event.key == 'K': self.TreatmentScale += 0.0005

      print(f"treatment scale={self.TreatmentScale}")
