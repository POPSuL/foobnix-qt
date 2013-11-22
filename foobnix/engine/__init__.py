__author__ = 'popsul'

from PyQt4 import QtCore


class MediaEngine(QtCore.QObject):

    StoppedState = 0
    PlayingState = 1
    PausedState = 2
    BufferingState = 3
    ErrorState = 4

    stateChanged = QtCore.pyqtSignal(int, name="stateChanged")
    positionChanged = QtCore.pyqtSignal(int, int, name="timeChanged")
    seekableChanged = QtCore.pyqtSignal(bool, name="seekableChanged")
    finished = QtCore.pyqtSignal(name="finished")

    def __init__(self, context):
        """
        @type context: CoreContext
        """
        super().__init__()
        self.context = context

    def getContext(self):
        """
        @rtype CoreContext
        """
        return self.context

    def play(self, media=None, force=False):
        """
        @type media: MediaItem
        @type force: bool
        """
        raise NotImplementedError()

    def pause(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def isPlaying(self):
        raise NotImplementedError()

    def isPaused(self):
        raise NotImplementedError()

    def isStopped(self):
        raise NotImplementedError()

    def setVolume(self, val):
        raise NotImplementedError()

    def seek(self, newPos):
        raise NotImplementedError()

    def isSeekable(self):
        raise NotImplementedError()

    def quit(self):
        pass
