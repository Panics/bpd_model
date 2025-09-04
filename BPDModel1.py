from Helpers.AbstractModel import AbstractModel

class BPDModel1(AbstractModel):
    # --------------------------
    # Parameters (Model 1)
    # --------------------------
    ALPHA:float = 0.1       # linear damping
    OMEGA2:float = 1.0      # restoring coefficient (ω²)
    B:float = -1.0          # nonlinear damping coeff

    # --------------------------
    # ODE step (Euler integration)
    # --------------------------
    def step(self, treatmentEffect:float, DT:float=0.04):
        curMood:float = super().ModelState.BpdMood
        curMoodVel:float = super().ModelState.BpdMoodVelocity

        dMood:float = curMoodVel
        dMoodVelocity:float = -self.ALPHA * curMoodVel - self.OMEGA2 * curMood - self.B * (curMood**2) * curMoodVel + treatmentEffect
        
        newMood:float = curMood + dMood * DT
        newMoodVelocity:float = curMoodVel + dMoodVelocity * DT

        super().ModelState.BpdMood = newMood
        super().ModelState.BpdMoodVelocity = newMoodVelocity
        super().ModelState.BpdTreatmentEffect = treatmentEffect
    
