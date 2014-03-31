# -*- coding: utf-8 -*-

import logging
import platform
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
        self.controls.volumeChaged.connect(lambda x: self.setToolTip("%d%%" % x))
        self.valueChanged.connect(lambda x: self.controls.setVolume(float(x)))

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.setValue(self.minimum() + ((self.maximum() - self.minimum()) * ev.x()) / (self.width() - 8))
            ev.accept()
        super().mousePressEvent(ev)


class SeekableProgressbar(QProgressBar):

    style = """QProgressBar::chunk {
     background-color: #3add36;
     width: 1px;
    }
     QProgressBar {
         border: 2px solid grey;
         border-radius: 0px;
         text-align: center;
    }"""

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
        if platform.system() == "Windows":
            self.setStyleSheet(self.style)

        self.isSeekable = True

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and self.isSeekable:
            self.setValue(self.minimum() + ((self.maximum() - self.minimum()) * ev.x()) / (self.width() - 8))
            self.controls.seek(self.value())
            ev.accept()
        super().mousePressEvent(ev)

    def onPositionChanged(self, current, total, force=False):
        if self.isSeekable or force:
            self.setMaximum(total)
            self.setValue(current)
        else:
            self._valueChanged(current)

    def _valueChanged(self, newValue):
        nv = newValue / 1000
        minutes = nv / 60
        seconds = nv % 60
        self.setFormat("%02d:%02d" % (minutes or 0, seconds or 0))

    def seekableChanged(self, seekable):
        logging.debug("Seekable changed. seekable?: %s" % str(seekable))
        self.isSeekable = seekable
        self.onPositionChanged(1, 1, True)


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
        self.stopButton.setToolTip(self.tr("Stop"))
        self.stopButton.setShortcut(QKeySequence(self.tr("S")))
        self.playButton = QPushButton(QIcon.fromTheme("media-playback-start"), "")
        self.playButton.setToolTip(self.tr("Play/Resume"))
        self.playButton.setShortcut(QKeySequence(self.tr("P")))
        self.pauseButton = QPushButton(QIcon.fromTheme("media-playback-pause"), "")
        self.pauseButton.setToolTip(self.tr("Pause"))
        self.prevButton = QPushButton(QIcon.fromTheme("media-seek-backward"), "")
        self.prevButton.setToolTip(self.tr("Previous track"))
        self.prevButton.setShortcut(QKeySequence(self.tr("B")))
        self.nextButton = QPushButton(QIcon.fromTheme("media-seek-forward"), "")
        self.nextButton.setToolTip(self.tr("Next track"))
        self.nextButton.setShortcut(QKeySequence(self.tr("N")))
        self.queueModeButton = QPushButton(QIcon.fromTheme("media-playlist-shuffle"), "")
        self.queueModeButton.setToolTip(self.tr("Shuffle mode"))
        self.queueModeButton.setShortcut(QKeySequence(self.tr("Q")))
        self.repeatModeButton = QPushButton(QIcon.fromTheme("media-playlist-repeat"), "")
        self.repeatModeButton.setToolTip(self.tr("Repeat mode"))
        self.repeatModeButton.setShortcut(QKeySequence(self.tr("R")))
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
        self.prevButton.clicked.connect(lambda *x: self.controls.playPrev())
        self.nextButton.clicked.connect(lambda *x: self.controls.playNext())

        self.queueModeButton.setCheckable(True)
        self.queueModeButton.setChecked(self.controls.shuffleMode() == PlaybackControl.ShuffleOn)
        self.queueModeButton.toggled.connect(self.queueToggled)
        self.controls.shuffleModeChanged.connect(self.queueModeChanged)

        self.repeatModeButton.setCheckable(True)
        self.repeatModeButton.setChecked(self.controls.repeatMode() == PlaybackControl.RepeatAll)
        self.repeatModeButton.toggled.connect(self.repeatToggled)
        self.controls.repeatModeChanged.connect(self.repeatModeChanged)

        self.controls.titleChanged.connect(lambda x: self.context.setStatusText(x))

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