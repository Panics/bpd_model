from pyo import *


def list_output_devices():
    pa_list_devices()


class Track:
    def __init__(self, audio):
        self.audio = audio
        self.playing = False

    def play(self, channel:int):
        self.audio.out(channel)
        self.playing = True

    def stop(self):
        self.audio.stop()
        self.playing = False

    def set_volume(self, volume):
        self.audio.setMul(volume)

    def set_frequency(self, frequency):
        self.audio.setFreq(frequency)


class SoundProcessor:
    def __init__(self, sampling_rate=44100, backend='portaudio', output=None, channels=2, discrete=False):
        self.backend = backend
        self.discrete = discrete
        self.sampling_rate = sampling_rate
        self.server = Server(audio=self.backend, sr=sampling_rate, jackname='pyo', winhost='directsound', nchnls=channels)
        self.server.boot()
        self.audio_output = output or pa_get_default_output()
        self.server.setOutputDevice(self.audio_output)
        self.tracks = []

    def start(self):
        self.server.start()

    def shutdown(self):
        self.stop()
        self.server.stop()
        self.server.shutdown()

    def add_track(self, audio):
        self.tracks.append(Track(audio))
        return len(self.tracks) - 1

    def remove_track(self, i):
        assert 0 <= i < len(self.tracks)
        return self.tracks.pop(i)

    def play(self, track:int, channel:int):
        assert 0 <= track < len(self.tracks)
        self.tracks[track].play(channel)

    def stop(self, i=None):
        if i is not None:
            assert 0 <= i < len(self.tracks)
            self.tracks[i].stop()
        else:
            for track in self.tracks:
                track.stop()

    def is_playing(self, i):
        assert 0 <= i < len(self.tracks)
        return self.tracks[i].playing

    def set_volume(self, i, volume):
        assert 0 <= i < len(self.tracks)
        self.tracks[i].set_volume(volume)

    def set_frequency(self, i, frequency):
        assert 0 <= i < len(self.tracks)
        self.tracks[i].set_frequency(frequency)

