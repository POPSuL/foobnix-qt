# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.gui import Separator
from foobnix.controls import PlaybackControl


class VolumeController(QSlider):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__(QtCore.Qt.Horizontal)
        self.context = context
        self.controls = context.getControls()

        self.setMinimumWidth(130)
        self.setRange(0, 100)
        self.setValue(self.controls.volume())
        self.controls.volumeChaged.connect(self.setValue)
        self.valueChanged.connect(lambda x: self.controls.setVolume(float(x)))

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.setValue(self.minimum() + ((self.maximum() - self.minimum()) * ev.x()) / (self.width() - 8))
            ev.accept()
        super(QSlider, self).mousePressEvent(ev)


class SeekableProgressbar(QProgressBar):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.controls = context.getControls()
        self.controls.positionChanged.connect(self.onPositionChanged)

        self.setTextVisible(True)
        self.valueChanged.connect(self._valueChanged)
        self.controls.seekableChanged.connect(self.seekableChanged)

        self.isSeekable = True

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.isSeekable:
            self.setValue(self.minimum() + ((self.maximum() - self.minimum()) * ev.x()) / (self.width() - 8))
            self.controls.seek(self.value())
            ev.accept()
        super(QProgressBar, self).mousePressEvent(ev)

    def onPositionChanged(self, current, total):
        self.setMaximum(total)
        self.setValue(current)

    def _valueChanged(self, newValue):
        nv = newValue / 1000
        minutes = nv / 60
        seconds = nv % 60
        self.setFormat("%02d:%02d" % (minutes or 0, seconds or 0))

    def seekableChanged(self, seekable):
        self.isSeekable = seekable
        self.onPositionChanged(1, 1)


class PlaybackControls(QHBoxLayout):

    #__metaclass__ = Singleton

    def __init__(self, context, parent=None):
        """
        @type context: GUIContext
        """
        super().__init__(parent)
        self.context = context
        self.controls = context.getControls()

        ## buttons
        self.stopButton = QPushButton(QIcon.fromTheme("media-playback-stop"), "")
        self.playButton = QPushButton(QIcon.fromTheme("media-playback-start"), "")
        self.pauseButton = QPushButton(QIcon.fromTheme("media-playback-pause"), "")
        self.prevButton = QPushButton(QIcon.fromTheme("media-seek-backward"), "")
        self.nextButton = QPushButton(QIcon.fromTheme("media-seek-forward"), "")
        self.queueModeButton = QPushButton(QIcon.fromTheme("media-playlist-shuffle"), "")
        self.repeatModeButton = QPushButton(QIcon.fromTheme("media-playlist-repeat"), "")
        buttonsWrapper = QHBoxLayout()
        buttonsWrapper.setSpacing(3)
        buttonsWrapper.setContentsMargins(0, 0, 0, 0)

        ## volume controller
        self.volumeSeeker = VolumeController(self.context)

        ## progress seekbar
        self.seekBar = SeekableProgressbar(self.context)
        self.seekBar.setMinimum(0)
        self.seekBar.setMaximum(100)
        self.seekBar.setValue(50)

        buttonsWrapper.addWidget(self.stopButton)
        buttonsWrapper.addWidget(self.playButton)
        buttonsWrapper.addWidget(self.pauseButton)
        buttonsWrapper.addWidget(self.prevButton)
        buttonsWrapper.addWidget(self.nextButton)
        buttonsWrapper.addWidget(Separator())
        buttonsWrapper.addWidget(self.queueModeButton)
        buttonsWrapper.addWidget(self.repeatModeButton)
        self.addLayout(buttonsWrapper)
        self.addWidget(Separator())
        self.addWidget(self.volumeSeeker)
        self.addWidget(Separator())
        self.addWidget(self.seekBar, 1)

        self.playButton.clicked.connect(lambda *x: self.controls.play(None))
        self.pauseButton.clicked.connect(self.controls.pause)
        self.stopButton.clicked.connect(self.controls.stop)

        self.queueModeButton.setCheckable(True)
        self.queueModeButton.setChecked(self.controls.shuffleMode() == PlaybackControl.ShuffleOn)
        self.queueModeButton.toggled.connect(self.queueToggled)
        self.controls.shuffleModeChanged.connect(self.queueModeChanged)

        self.repeatModeButton.setCheckable(True)
        self.repeatModeButton.setChecked(self.controls.repeatMode() == PlaybackControl.RepeatAll)
        self.repeatModeButton.toggled.connect(self.repeatToggled)
        self.controls.repeatModeChanged.connect(self.repeatModeChanged)

    def queueToggled(self, pressed):
        if pressed:
            self.controls.setShuffleMode(PlaybackControl.ShuffleOn)
        else:
            self.controls.setShuffleMode(PlaybackControl.ShuffleOff)

    def queueModeChanged(self, mode):
        if mode == PlaybackControl.ShuffleOn:
            self.queueModeButton.setChecked(True)
        else:
            self.queueModeButton.setChecked(False)

    def repeatToggled(self, pressed):
        if pressed:
            self.controls.setRepeatMode(PlaybackControl.RepeatAll)
        else:
            self.controls.setRepeatMode(PlaybackControl.NoRepat)

    def repeatModeChanged(self, mode):
        self.repeatModeButton.setChecked(mode == PlaybackControl.RepeatAll)