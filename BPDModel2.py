from Helpers.AbstractModel import AbstractModel
import numpy as np
import os
from math import erf   # ✅ error function
from BPDModel2Configuration import BPDModel2Configuration

class BPDModel2(AbstractModel):

    # --------------------------
    # State variables
    # --------------------------
    _currentConfiguration:BPDModel2Configuration
    _P0:float
    _N0:float
    _buf_len:int
    _P_buf:np.ndarray
    _N_buf:np.ndarray
    _i:int

    # ------------------------------------------------------------------------------------------------------------
    @property
    def CurrentConfiguration(self):
        return self._currentConfiguration
    
    @CurrentConfiguration.setter
    def CurrentConfiguration(self, val):
        self._currentConfiguration = val

    # --------------------------
    # Constructor
    # --------------------------
    def __init__(self, 
                 g1:float=3.0, 
                 g2:float=3.0,
                 qPmin:float=10.0, 
                 qPmax:float=10.0,
                 qNmin:float=2.5, 
                 qNmax:float=7.0,
                 lamb:float=4,
                 dt:float=0.001,
                 tmin:float=1.0, 
                 tmax:float=5.0,
                 injectMode:str = 'tilt_to_PN',
                 delay_seconds:float=0.02,
                 g_gain:float=0.2,
                 P0:float=100.0, 
                 N0:float=100.0,
                 initialMood:float=0.5, 
                 initialTreatmentEffect:float=0):

        super().__init__(mood=initialMood, treatmentEffect=initialTreatmentEffect)

        self._currentConfiguration = BPDModel2Configuration(
                 g1 = g1,
                 g2 = g2,
                 qPmin = qPmin,
                 qPmax = qPmax,
                 qNmin = qNmin,
                 qNmax = qNmax,
                 lamb = lamb,
                 dt = dt,
                 tmin = tmin,
                 tmax = tmax,
                 injectMode = injectMode,
                 delay_seconds = delay_seconds,
                 g_gain = g_gain
        )

        self.reset(P0, N0)

    # --------------------------
    def reset(self, P0=100.0, N0=100.0):
        buf_len = max(8, self.CurrentConfiguration.Delay_Steps + 10)
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
        denom = (self.f(self.CurrentConfiguration.G1) - self.f(0.0))
        return (self.f(self.CurrentConfiguration.G1 * x) - self.f(0.0)) / denom if denom != 0 else 0.0

    # --------------------------
    def S2(self, x):
        denom = (self.f(self.CurrentConfiguration.G2) - self.f(0.0))
        return (self.f(self.CurrentConfiguration.G2 * x) - self.f(0.0)) / denom if denom != 0 else 0.0

    # --------------------------
    def qP(self, eb): return self.CurrentConfiguration.QPMin + self.S1(eb) * (self.CurrentConfiguration.QPMax - self.CurrentConfiguration.QPMin)

    # --------------------------
    def qN(self, eb): return self.CurrentConfiguration.QNMin + (1.0 - self.S2(eb)) * (self.CurrentConfiguration.QNMax - self.CurrentConfiguration.QNMin)

    # --------------------------
    def tP(self, eb): return self.CurrentConfiguration.TMin + self.S1(eb) * (self.CurrentConfiguration.TMax - self.CurrentConfiguration.TMin)

    # --------------------------
    def tN(self, eb): return self.CurrentConfiguration.TMin + (1.0 - self.S2(eb)) * (self.CurrentConfiguration.TMax - self.CurrentConfiguration.TMin)

    # --------------------------
    def current_indices(self):
        cur_idx = self._i % self._buf_len
        delay_idx = (self._i - self.CurrentConfiguration.Delay_Steps) % self._buf_len
        return cur_idx, delay_idx

    # --------------------------
    def step(self, treatmentEffect:float=0.0, DT:float=0.04):

        # self.CurrentConfiguration.Dt = DT

        cur_idx, delay_idx = self.current_indices()
        P_cur = self._P_buf[cur_idx]; N_cur = self._N_buf[cur_idx]
        total = P_cur + N_cur
        EB = P_cur / total if total > 1e-9 else 0.5

        qP_val, qN_val = self.qP(EB), self.qN(EB)
        tP_val, tN_val = self.tP(EB), self.tN(EB)

        lamb_eff, g_eff = self.CurrentConfiguration.Lamb, self.CurrentConfiguration.Gain
        P_next, N_next = P_cur, N_cur  # init with current

        if self.CurrentConfiguration.InjectMode == 'add_to_lambda':
            lamb_eff = self.CurrentConfiguration.Lamb + treatmentEffect
        elif self.CurrentConfiguration.InjectMode == 'add_to_g':
            g_eff = self.CurrentConfiguration.Gain + treatmentEffect

        # base dynamics
        P_delay, N_delay = self._P_buf[delay_idx], self._N_buf[delay_idx]
        diffP, diffN = (P_cur - P_delay), (N_cur - N_delay)

        dP = -P_cur / tP_val + lamb_eff * qP_val
        dN = -N_cur / tN_val + lamb_eff * qN_val
        P_next = P_cur + self.CurrentConfiguration.Dt * dP + g_eff * diffP
        N_next = N_cur + self.CurrentConfiguration.Dt * dN + g_eff * diffN

        # ✅ Injection modes
        if self.CurrentConfiguration.InjectMode == 'add_to_P':
            P_next += treatmentEffect * 1.0
        elif self.CurrentConfiguration.InjectMode == 'add_to_EB':
            # push EB directly by biasing P vs N
            P_next += treatmentEffect * 10.0
            N_next -= treatmentEffect * 10.0
        elif self.CurrentConfiguration.InjectMode == 'tilt_to_PN':
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

        self.ModelState.BpdMood = 2 * (EB_next - 0.5)
        self.ModelState.BpdTreatmentEffect = treatmentEffect

        return EB_next, P_next, N_next
    
    # ------------------------------------------------------------------------------------------------------------
    def on_key(self, event):
        printMsg:bool = False

        if event.key == 'l': 
            self.CurrentConfiguration.Lamb = max(0.0, self.lamb - 0.05)
            printMsg = True
        elif event.key == 'L': 
            self.CurrentConfiguration.Lamb += 0.05
            printMsg = True
        elif event.key == 'g': 
            self.CurrentConfiguration.Gain = max(0.0, self.g_gain - 0.005)
            printMsg = True
        elif event.key == 'G': 
            self.CurrentConfiguration.Gain += 0.005
            printMsg = True
        elif event.key == 't': 
            self.CurrentConfiguration.Dt = max(0.0005, self.dt - 0.0005)
            self.reset()
            printMsg = True
        elif event.key == 'T': 
            self.CurrentConfiguration.Dt += 0.0005
            self.reset()
            printMsg = True
        elif event.key == 'm':
            modes = ['add_to_lambda', 'add_to_g', 'add_to_P', 'add_to_EB', 'tilt_to_PN']
            self.CurrentConfiguration.InjectMode = modes[(modes.index(self.CurrentConfiguration.InjectMode) + 1) % len(modes)]
            printMsg = True
        elif event.key == 'r': 
            self.reset()
            printMsg = True

        if printMsg:
            print(f"λ={self.CurrentConfiguration.Lamb:.2f}, g={self.CurrentConfiguration.Gain:.2f}, dt={self.CurrentConfiguration.Dt:.4f}, mode={self.CurrentConfiguration.InjectMode}")

    # ------------------------------------------------------------------------------------------------------------
    def print_key_info(self):
        print(f'{os.path.basename(__file__)}: l/L  = reduce or increase lambda by 0.05')      
        print(f'{os.path.basename(__file__)}: g/G  = reduce or increase gain by 0.0005')      
        print(f'{os.path.basename(__file__)}: t/T  = reduce or increase dT by 0.0005')      
        print(f'{os.path.basename(__file__)}: m  = cycle through inject modes (add_to_lambda, add_to_g, add_to_P, add_to_EB, tilt_to_PN)')
        print(f'{os.path.basename(__file__)}: r  = reset')      
      
