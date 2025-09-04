class ImuData:
    # ------------------------------------------------------------------------------------------------------------
    _xAngle:float = 0
    _yAngle:float = 0
    _zAngle:float = 0
    
    # ------------------------------------------------------------------------------------------------------------
    _xGyro:float = 0
    _yGyro:float = 0
    _zGyro:float = 0
    
    # ------------------------------------------------------------------------------------------------------------
    _xAccel:float = 0
    _yAccel:float = 0
    _zAccel:float = 0
    
    # ------------------------------------------------------------------------------------------------------------
    _xAccelAngle:float = 0
    _yAccelAngle:float = 0
    _zAccelAngle:float = 0
    
    # ------------------------------------------------------------------------------------------------------------
    _temp:float = 0

    # ------------------------------------------------------------------------------------------------------------
    @property
    def xAngle(self):
        return self._xAngle
    
    @xAngle.setter
    def xAngle(self, val):
        self._xAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def yAngle(self):
        return self._yAngle
    
    @yAngle.setter
    def yAngle(self, val):
        self._yAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def zAngle(self):
        return self._zAngle
    
    @zAngle.setter
    def zAngle(self, val):
        self._zAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def xGyro(self):
        return self._xGyro
    
    @xGyro.setter
    def xGyro(self, val):
        self._xGyro = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def yGyro(self):
        return self._yGyro
    
    @yGyro.setter
    def yGyro(self, val):
        self._yGyro = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def zGyro(self):
        return self._zGyro
    
    @zGyro.setter
    def zGyro(self, val):
        self._zGyro = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def xAccel(self):
        return self._xAccel
    
    @xAccel.setter
    def xAccel(self, val):
        self._xAccel = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def yAccel(self):
        return self._yAccel
    
    @yAccel.setter
    def yAccel(self, val):
        self._yAccel = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def zAccel(self):
        return self._zAccel
    
    @zAccel.setter
    def zAccel(self, val):
        self._zAccel = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def xAccelAngle(self):
        return self._xAccelAngle
    
    @xAccelAngle.setter
    def xAccelAngle(self, val):
        self._xAccelAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def yAccelAngle(self):
        return self._yAccelAngle
    
    @yAccelAngle.setter
    def yAccelAngle(self, val):
        self._yAccelAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def zAccelAngle(self):
        return self._zAccelAngle
    
    @zAccelAngle.setter
    def zAccelAngle(self, val):
        self._zAccelAngle = val

    # ------------------------------------------------------------------------------------------------------------
    @property
    def temp(self):
        return self._temp
    
    @temp.setter
    def temp(self, val):
        self._temp = val


