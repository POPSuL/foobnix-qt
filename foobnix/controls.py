__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal
from . import Loadable, Savable
from .util import Singleton
from .settings import SettingsContainer


class Control(QtCore.QObject, Loadable, Savable):

    def __init__(self):
        super().__init__()


class PlaybackControl(Control):

    NoRepat = 0
    RepeatOne = 1
    RepeatAll = 2

    ShuffleOff = 0
    ShuffleOn = 1

    StateStop = 0
    StatePause = 1
    StatePlay = 2

    _repeatMode = NoRepat
    _shuffleMode = ShuffleOff
    _volume = 50.
    settings = SettingsContainer().getContainer("controls")

    stateChanged = pyqtSignal(int, name="stateChanged")
    volumeChaged = pyqtSignal(float, name="volumeChanged")
    repeatModeChanged = pyqtSignal(int, name="repeatModeChanged")
    shuffleModeChanged = pyqtSignal(int, name="shuffleModeChanged")

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PlaybackControl, cls).__new__(cls)
        return cls.instance

    def load(self):
        self.setShuffleMode(int(self.settings.value("playback/shuffle", self.ShuffleOff)))
        self.setRepeatMode(int(self.settings.value("playback/repeat", self.NoRepat)))
        self.setVolume(float(self.settings.value("playback/volume", 50.)))

    def save(self):
        self.settings.setValue("playback/repeat", self.repeatMode())
        self.settings.setValue("playback/shuffle", self.shuffleMode())
        self.settings.setValue("playback/volume", self.volume())

    def play(self, mediaId):
        self.stateChanged.emit(self.StatePlay)

    def pause(self):
        self.stateChanged.emit(self.StatePause)

    def stop(self):
        self.stateChanged.emit(self.StateStop)

    def setVolume(self, val):
        assert isinstance(val, float), "val must be float"
        assert 0. <= val <= 100., "val must be greater than 0., and less than 100."
        self._volume = val
        self.volumeChaged.emit(val)

    def volume(self):
        return self._volume

    def setRepeatMode(self, mode):
        assert isinstance(mode, int), "mode must be int"
        self._repeatMode = mode
        self.repeatModeChanged.emit(mode)

    def repeatMode(self):
        return self._repeatMode

    def setShuffleMode(self, mode):
        assert isinstance(mode, int), "mode must be int"
        self._shuffleMode = mode
        self.shuffleModeChanged.emit(mode)

    def shuffleMode(self):
        return self._shuffleMode