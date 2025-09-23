import sys
import pyo

from Sound import SoundProcessor
from Sound.utils import freq_to_midi_str, freq_to_midi, midi_to_freq
from Helpers import ModelOutputData
from pyo import *
from Helpers.ThereminOutputData import ThereminOutputData

class Theremin :

    # ------------------------------------------------------------------------------------------------------------
    _dsp:SoundProcessor
    _channel:int
    _minFrequency:int
    _maxFrequency:int
    _minVolume:float
    _maxVolume:float

    _sineR:Sine
    _harmonizerR:Harmonizer
    _chorusR:Chorus
    _freqShiftR:FreqShift

    _sineL:Sine
    _harmonizerL:Harmonizer
    _chorusL:Chorus
    _freqShiftL:FreqShift

    # --------------------------
    # State variables
    # --------------------------
    _thereminState:ThereminOutputData = ThereminOutputData()
    _isPlaying:bool

    # --------------------------
    # State variable Property Getters
    # --------------------------
    @property
    def ThereminState(self):
        return self._thereminState

    @property
    def IsPlaying(self):
        return self._isPlaying

    # ------------------------------------------------------------------------------------------------------------
    def Stop(self):
        self._dsp.stop(self._channelL)
        self._dsp.stop(self._channelR)
        self._isPlaying=False

    # ------------------------------------------------------------------------------------------------------------
    def Start(self):
        self._dsp.play(self._channelL, 0)
        self._dsp.play(self._channelR, 1)
        self._isPlaying=True

    # ------------------------------------------------------------------------------------------------------------
    def Update(self, modelState:ModelOutputData):
        # update volume
        self.ThereminState.Volume = float(self._minVolume + (self._maxVolume-self._minVolume)*(1-abs(modelState.BpdTreatmentEffect/2.70)))
        self._dsp.set_volume(self._channelL, self.ThereminState.Volume)
        self._dsp.set_volume(self._channelR, self.ThereminState.Volume)

        self.ThereminState.Frequency = float(self._minFrequency + (self._maxFrequency-self._minFrequency) * (modelState.BpdMood+1)/2)
        # use raw frequency or convert to midi note if needed
        frequency:float = self.ThereminState.Frequency
        if self._dsp.discrete:
            frequency = midi_to_freq(freq_to_midi(frequency))
        self._sineL.freq = frequency
        self._sineR.freq = frequency

    # ------------------------------------------------------------------------------------------------------------
    def __init__(self, wave='SineLoop', audio_output=None, audio_backend='portaudio', channels=2, min_frequency=55, max_frequency=10000, sampling_rate=44100, discrete=False, min_Volume=0.5, max_Volume=1):
        self._minFrequency = min_frequency
        self._maxFrequency = max_frequency
        self._minVolume = min_Volume
        self._maxVolume = max_Volume
        self._isPlaying = False
        self._thereminState = ThereminOutputData()
        
        self._dsp = SoundProcessor(output=audio_output, backend=audio_backend, channels=channels, sampling_rate=sampling_rate, discrete=discrete)

        self._sineL = Sine()
        self._harmonizerL = Harmonizer(self._sineL)
        self._chorusL = Chorus(self._harmonizerL)
        self._freqShiftL = FreqShift(self._chorusL)
        self._sineR = Sine()
        self._harmonizerR = Harmonizer(self._sineR)
        self._chorusR = Chorus(self._harmonizerR)
        self._freqShiftR = FreqShift(self._chorusR)

        self._channelL = self._dsp.add_track(self._freqShiftL)
        self._channelR = self._dsp.add_track(self._freqShiftR)
        self._dsp.start()
        self.Start()

        print('Audio processor started')

    # ------------------------------------------------------------------------------------------------------------
    def __del__(self):
        self._dsp.stop(self._channelL)
        self._dsp.stop(self._channelR)
        self._dsp.shutdown()
        print('Audio processor stopped')
