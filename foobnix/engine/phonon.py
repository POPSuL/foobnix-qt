__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.phonon import Phonon
from . import MediaEngine


class PhononEngine(MediaEngine):

    def __init__(self, context):
        """
        @type context: CoreContext
        """
        super().__init__(context)

        self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
        self.mediaObject = Phonon.MediaObject(self)
        self.metaInformationResolver = Phonon.MediaObject(self)

        self.mediaObject.setTickInterval(500)
        self.mediaObject.tick.connect(self._tick)
        self.mediaObject.stateChanged.connect(self._stateChanged)
        self.metaInformationResolver.stateChanged.connect(self._metaStateChanged)
        self.mediaObject.currentSourceChanged.connect(self._currentSourceChanged)
        self.mediaObject.aboutToFinish.connect(self._aboutToFinish)
        Phonon.createPath(self.mediaObject, self.audioOutput)

        self.prevMedia = None

    def _tick(self, t):
        self.timeChanged.emit(t, self.mediaObject.totalTime())

    def _stateChanged(self, newState, oldState):
        print("_stateChanged", newState, oldState)
        if newState == Phonon.StoppedState:
            self.stateChanged.emit(self.StoppedState)
        elif newState == Phonon.PausedState:
            self.stateChanged.emit(self.PausedState)
        elif newState == Phonon.PlayingState:
            self.stateChanged.emit(self.PlayingState)
        elif newState == Phonon.BufferingState:
            self.stateChanged.emit(self.BufferingState)
        elif newState == Phonon.ErrorState:
            self.stateChanged.emit(self.ErrorState)

    def _metaStateChanged(self, newState, oldState):
        print("_metaStateChanged", newState, oldState)

    def _currentSourceChanged(self, source):
        print("_currentSourceChanged", source)

    def _aboutToFinish(self):
        print("_aboutToFinish")

    def play(self, media=None, force=False):
        """
        @type media: Media
        """
        if self.isPaused():
            self.mediaObject.play()
        elif force or (self.isPlaying() and media != self.prevMedia) or (self.isStopped() and media):
            source = Phonon.MediaSource(media.path)
            self.stop()
            self.mediaObject.setQueue([])
            self.mediaObject.setCurrentSource(source)
            self.mediaObject.play()
            self.prevMedia = media

    def pause(self):
        self.mediaObject.pause()

    def stop(self):
        self.mediaObject.stop()
        self.mediaObject.clearQueue()

    def isPlaying(self):
        return self.mediaObject.state() == Phonon.PlayingState

    def isPaused(self):
        return self.mediaObject.state() == Phonon.PausedState

    def isStopped(self):
        return self.mediaObject.state() == Phonon.StoppedState

    def setVolume(self, val):
        self.audioOutput.setVolume(val / 100.)

    def seek(self, newPos):
        if self.isSeekable():
            self.mediaObject.seek(newPos)

    def isSeekable(self):
        return self.mediaObject.isSeekable()

    def quit(self):
        self.stop()
        del self.mediaObject
        del self.audioOutput
