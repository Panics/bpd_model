
class BPDModel2Configuration:

    # --------------------------
    # State variables
    # --------------------------
    _injectMode:str
    _g1:float
    _g2:float
    _qPmin:float
    _qPmax:float
    _qNmin:float
    _qNmax:float
    _lamb:float
    _dt:float
    _tmin:float
    _tmax:float
    _delay_seconds:float
    _g_gain:float

    # ------------------------------------------------------------------------------------------------------------
    @property
    def InjectMode(self):
        return self._injectMode
    
    @InjectMode.setter
    def InjectMode(self, val):
        self._injectMode = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def G1(self):
        return self._g1
    
    @G1.setter
    def G1(self, val):
        self._g1 = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def G2(self):
        return self._g2
    
    @G2.setter
    def G2(self, val):
        self._g2 = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def QPMin(self):
        return self._qPmin
    
    @QPMin.setter
    def QPMin(self, val):
        self._qPmin = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def QPMax(self):
        return self._qPmax
    
    @QPMin.setter
    def QPMax(self, val):
        self._qPmax = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def QNMin(self):
        return self._qNmin
    
    @QNMin.setter
    def QNMin(self, val):
        self._qNmin = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def QNMax(self):
        return self._qNmax
    
    @QNMin.setter
    def QNMax(self, val):
        self._qNmax = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Lamb(self):
        return self._lamb
    
    @Lamb.setter
    def Lamb(self, val):
        self._lamb = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Dt(self):
        return self._dt
    
    @Dt.setter
    def Dt(self, val):
        self._dt = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def TMin(self):
        return self._tmin
    
    @TMin.setter
    def TMin(self, val):
        self._tmin = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def TMax(self):
        return self._tmax
    
    @TMax.setter
    def TMax(self, val):
        self._tmax = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Delay_Seconds(self):
        return self._delay_seconds
    
    @Delay_Seconds.setter
    def Delay_Seconds(self, val):
        self._delay_seconds = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def Gain(self):
        return self._g_gain
    
    @Gain.setter
    def Gain(self, val):
        self._g_gain = val

    # --------------------------
    @property
    def Delay_Steps(self):
        return max(1, int(round(self.Delay_Seconds / self.Dt)))

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
                 g_gain:float=0.2):

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
        self._injectMode = injectMode

