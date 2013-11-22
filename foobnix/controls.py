__author__ = 'popsul'

import logging
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSignal
from . import Loadable, Savable


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

    stateChanged = pyqtSignal(int, object, name="stateChanged")
    volumeChaged = pyqtSignal(float, name="volumeChanged")
    repeatModeChanged = pyqtSignal(int, name="repeatModeChanged")
    shuffleModeChanged = pyqtSignal(int, name="shuffleModeChanged")
    positionChanged = pyqtSignal(int, int, name="positionChanged")
    seekableChanged = pyqtSignal(bool, name="seekableChanged")
    needNext = pyqtSignal(bool, bool, name="needNext")
    needPrev = pyqtSignal(bool, name="needRandom")

    def __init__(self, context):
        """
        @type context: CoreContext
        """
        super().__init__()
        self.context = context
        self.settings = context.getSettings("controls")
        self.engine = context.getEngine()
        self._repeatMode = self.NoRepat
        self._shuffleMode = self.ShuffleOff
        self._volume = 50.
        self._lastPlayed = None
        self.engine.positionChanged.connect(self.positionChanged.emit)
        self.engine.seekableChanged.connect(self.seekableChanged.emit)
        self.engine.finished.connect(self._finished)

    def load(self):
        self.setShuffleMode(int(self.settings.value("playback/shuffle", self.ShuffleOff)))
        self.setRepeatMode(int(self.settings.value("playback/repeat", self.NoRepat)))
        self.setVolume(float(self.settings.value("playback/volume", 50.)))

    def save(self):
        self.settings.setValue("playback/repeat", self.repeatMode())
        self.settings.setValue("playback/shuffle", self.shuffleMode())
        self.settings.setValue("playback/volume", self.volume())

    def play(self, media, force=False):
        logging.debug("play")
        logging.debug(media.path)
        self._lastPlayed = media
        self.engine.play(media, force=force)
        self.stateChanged.emit(self.StatePlay, media)

    def pause(self):
        self.engine.pause()
        self.stateChanged.emit(self.StatePause, self._lastPlayed)

    def stop(self):
        self.engine.stop()
        self.stateChanged.emit(self.StateStop, self._lastPlayed)

    def setVolume(self, val):
        assert isinstance(val, float), "val must be float"
        assert 0. <= val <= 100., "val must be greater than 0., and less than 100."
        self._volume = val
        self.engine.setVolume(self._volume)
        self.volumeChaged.emit(val)

    def volume(self):
        return self._volume

    def seek(self, newPos):
        self.engine.seek(newPos)

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

    def lastPlayed(self):
        return self._lastPlayed

    def playNext(self):
        logging.debug("playNext called")
        if self._lastPlayed and self.repeatMode() == self.RepeatOne:
            self.play(self._lastPlayed, True)
        else:
            self.needNext.emit(self.shuffleMode() == self.ShuffleOn, self.repeatMode() == self.RepeatAll)

    def playPrev(self):
        logging.debug("playPrev called")
        if self._lastPlayed and self.repeatMode() == self.RepeatOne:
            self.play(self._lastPlayed, True)
        else:
            self.needPrev.emit(self.shuffleMode() == self.ShuffleOn)

    def _finished(self):
        logging.debug("_finished signal received")
        self.playNext()