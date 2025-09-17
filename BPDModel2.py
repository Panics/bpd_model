from Helpers.AbstractModel import AbstractModel
import numpy as np
from math import erf   # ✅ error function
from Helpers.ModelOutputData import ModelOutputData

class BPDModel2(AbstractModel):

    # --------------------------
    # State variables
    # --------------------------
    _injectMode:str
    _g1:float
    _g2:float
    _qPmin:float
    _qPmax:float
    _lamb:float
    _dt:float
    _tmin:float
    _tmax:float
    _delay_seconds:float
    _P0:float
    _N0:float
    _delay_steps:int
    _buf_len:int
    _P_buf:np.ndarray
    _N_buf:np.ndarray
    _i:int

    # ------------------------------------------------------------------------------------------------------------
    @property
    def InjectMode(self):
        return self._injectMode
    
    @InjectMode.setter
    def InjectMode(self, val):
        self._injectMode = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def dt(self):
        return self._dt
    
    @dt.setter
    def dt(self, val):
        self._dt = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def lamb(self):
        return self._lamb
    
    @lamb.setter
    def lamb(self, val):
        self._lamb = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def g_gain(self):
        return self._g_gain
    
    @g_gain.setter
    def g_gain(self, val):
        self._g_gain = val

    # --------------------------
    # Constructor
    # --------------------------
    def __init__(self, 
                 g1=3.0, g2=3.0,
                 qPmin=10.0, qPmax=10.0,
                 qNmin=2.5, qNmax=7.0,
                 lamb=4,
                 dt=0.001,
                 tmin=1.0, tmax=5.0,
                 injectMode = 'add_to_lambda',
                 delay_seconds=0.02,
                 g_gain=0.2,
                 P0=100.0, 
                 N0=100.0,
                 initialMood:float=0.5, 
                 initialTreatmentEffect:float=0):

        super().__init__(mood=initialMood, treatmentEffect=initialTreatmentEffect)

        self._g1 = g1; 
        self._g2 = g2
        self._qPmin = qPmin; 
        self._qPmax = qPmax
        self._qNmin = qNmin; 
        self._qNmax = qNmax
        self._lamb = lamb
        self._tmin = tmin; 
        self._tmax = tmax
        self._delay_seconds = delay_seconds
        self._g_gain = g_gain
        self._dt = dt
        self.InjectMode = injectMode
        self.reset(P0, N0)

    # --------------------------
    def reset(self, P0=100.0, N0=100.0):
        self._delay_steps = max(1, int(round(self._delay_seconds / self._dt)))
        buf_len = max(8, self._delay_steps + 10)
        self._buf_len = buf_len
        self._P_buf = np.zeros(buf_len)
        self._N_buf = np.zeros(buf_len)
        self._P_buf[0] = P0
        self._N_buf[0] = N0
        self._i = 0

    # --------------------------
    def f(self, x): return erf(x - 2.0)

    # --------------------------
    def S1(self, x):
        denom = (self.f(self._g1) - self.f(0.0))
        return (self.f(self._g1 * x) - self.f(0.0)) / denom if denom != 0 else 0.0

    # --------------------------
    def S2(self, x):
        denom = (self.f(self._g2) - self.f(0.0))
        return (self.f(self._g2 * x) - self.f(0.0)) / denom if denom != 0 else 0.0

    # --------------------------
    def qP(self, eb): return self._qPmin + self.S1(eb) * (self._qPmax - self._qPmin)

    # --------------------------
    def qN(self, eb): return self._qNmin + (1.0 - self.S2(eb)) * (self._qNmax - self._qNmin)

    # --------------------------
    def tP(self, eb): return self._tmin + self.S1(eb) * (self._tmax - self._tmin)

    # --------------------------
    def tN(self, eb): return self._tmin + (1.0 - self.S2(eb)) * (self._tmax - self._tmin)

    # --------------------------
    def current_indices(self):
        cur_idx = self._i % self._buf_len
        delay_idx = (self._i - self._delay_steps) % self._buf_len
        return cur_idx, delay_idx

    # --------------------------
    def step(self, treatmentEffect:float=0.0, DT:float=0.04):

        self._dt = DT

        cur_idx, delay_idx = self.current_indices()
        P_cur = self._P_buf[cur_idx]; N_cur = self._N_buf[cur_idx]
        total = P_cur + N_cur
        EB = P_cur / total if total > 1e-9 else 0.5

        qP_val, qN_val = self.qP(EB), self.qN(EB)
        tP_val, tN_val = self.tP(EB), self.tN(EB)

        lamb_eff, g_eff = self._lamb, self._g_gain
        P_next, N_next = P_cur, N_cur  # init with current

        if self.InjectMode == 'add_to_lambda':
            lamb_eff = self._lamb + treatmentEffect
        elif self.InjectMode == 'add_to_g':
            g_eff = self._g_gain + treatmentEffect

        # base dynamics
        P_delay, N_delay = self._P_buf[delay_idx], self._N_buf[delay_idx]
        diffP, diffN = (P_cur - P_delay), (N_cur - N_delay)

        dP = -P_cur / tP_val + lamb_eff * qP_val
        dN = -N_cur / tN_val + lamb_eff * qN_val
        P_next = P_cur + self._dt * dP + g_eff * diffP
        N_next = N_cur + self._dt * dN + g_eff * diffN

        # ✅ Injection modes
        if self.InjectMode == 'add_to_P':
            P_next += treatmentEffect * 1.0
        elif self.InjectMode == 'add_to_EB':
            # push EB directly by biasing P vs N
            P_next += treatmentEffect * 10.0
            N_next -= treatmentEffect * 10.0
        elif self.InjectMode == 'tilt_to_PN':
            if treatmentEffect > 0:
                P_next += abs(treatmentEffect) * 10.0
            else:
                N_next += abs(treatmentEffect) * 10.0

        # Clamp to avoid runaway
        P_next = max(1e-6, min(P_next, 1e6))
        N_next = max(1e-6, min(N_next, 1e6))

        next_idx = (self._i + 1) % self._buf_len
        self._P_buf[next_idx] = P_next
        self._N_buf[next_idx] = N_next
        self._i += 1

        EB_next = P_next / (P_next + N_next) if (P_next + N_next) > 1e-9 else 0.5
        EB_next = min(1.0, max(0.0, EB_next))

        self.ModelState.BpdMood = EB_next
        self.ModelState.BpdTreatmentEffect = treatmentEffect

        return EB_next, P_next, N_next