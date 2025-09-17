import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt

from Helpers.ModelOutputData import ModelOutputData

# ------------------------------------------------------------------------------------------------------------
     
class ModelPlot:
    # --------------------------
    # Model State History
    # --------------------------
    _moodHistory:NDArray[np.float64] = []
    _treatmentHistory:NDArray[np.float64] = []

    # --------------------------
    # Figure Tracking
    # --------------------------
    _fig:plt.Figure
    _ax1:plt.Axes
    _line1:plt.Line2D
    _line2:plt.Line2D
    _line3:plt.Line2D

    # --------------------------
    # State variable Property Getters
    # --------------------------
    @property
    def Fig(self):
        return self._fig

    # --------------------------
    # Plot``
    # --------------------------
    def UpdatePlot(self, modelOutputData:ModelOutputData):
        self._moodHistory.append(modelOutputData.BpdMood)
        self._treatmentHistory.append(modelOutputData.BpdTreatmentEffect)
        
        if len(self._moodHistory)>500:
            self._moodHistory.pop(0)
            self._treatmentHistory.pop(0)

        self._ax1.clear()
        self._ax1.set_ylim(-5, 5)
        self._ax1.set_ylabel("Mood & Treatment")
        
        self._ax1.plot(list(range(len(self._moodHistory))), self._moodHistory, label="Mood")
        self._ax1.plot(list(range(len(self._treatmentHistory))), self._treatmentHistory, label="Treatment Effect")

        self._ax1.legend()

        plt.pause(0.1)
    
    # --------------------------
    # Plotting setup
    # --------------------------
    def __init__(self):
        plt.ion()

        self._fig, self._ax1 = plt.subplots()

        self._line1, = self._ax1.plot([], [], label="Mood")
        self._line3, = self._ax1.plot([], [], label="Treatment Effect")
        self._ax1.set_ylim(-5, 5)
        self._ax1.set_ylabel("Mood & Treatment")
        self._ax1.legend()

