# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix import Loadable, Savable
from foobnix.gui.perspectives import PerspectivesController
from foobnix.gui.search import SearchBar
from foobnix.gui.playback import PlaybackControls
from foobnix.gui.playlist import PlaylistsContainer


class BaseWindow(QMainWindow, Loadable, Savable):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super(BaseWindow, self).__init__()
        self.context = context
        self.guiSettings = context.getSettings("gui")

        self.setWindowTitle("Foobnix")

        ## menus
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        self.playbackMenu = self.menuBar().addMenu(self.tr("&Playback"))
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))

        ## perspectives
        self.leftHBoxWrapper = QWidget()

        ## searchbar + playlist contaner
        self.searchBar = SearchBar()
        self.playlistsContainer = PlaylistsContainer(self.context)
        rightHBox = QVBoxLayout()
        rightHBox.addLayout(self.searchBar)
        rightHBox.addWidget(self.playlistsContainer, 1)
        rightHBox.setContentsMargins(0, 0, 0, 0)
        rightHBoxWrapper = QWidget()
        rightHBoxWrapper.setLayout(rightHBox)

        ## splitter for left-right sides
        self.splitter = QSplitter()
        self.splitterHandler = QSplitterHandle(QtCore.Qt.Horizontal, None)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.leftHBoxWrapper)
        self.splitter.addWidget(rightHBoxWrapper)

        self.splitter.splitterMoved.connect(self.splitterMovedHandler)

        ## base container
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(PlaybackControls(self.context))
        self.vbox.addWidget(self.splitter, 1)

        #self.setLayout(self.vbox)
        wrapper = QWidget()
        wrapper.setLayout(self.vbox)
        self.setCentralWidget(wrapper)
        self.buildMenu()

    def splitterMovedHandler(self, *args):
        pass
        #self.guiSettings.setValue("splitter/sizes", self.splitter.sizes())

    def setPerspectiveController(self, pc):
        assert isinstance(pc, PerspectivesController), "argument 1 must be an instance of PerspectiveController"
        self.leftHBoxWrapper.setLayout(pc)

    def buildMenu(self):
        prefs = self.fileMenu.addAction(QIcon.fromTheme("preferences-desktop"), self.tr("&Preferences"))
        quit = self.fileMenu.addAction(QIcon.fromTheme("application-exit"), self.tr("&Quit"))
        prefs.triggered.connect(self.openPreferences)
        quit.triggered.connect(QApplication.instance().quit)

    def openPreferences(self):
        pass

    def load(self):
        savedSizes = self.guiSettings.value("splitter/sizes", None)
        if savedSizes:
            self.splitter.setSizes([int(k) for k in savedSizes])

        self.resize(int(self.guiSettings.value("window/width", 640)), int(self.guiSettings.value("window/height", 480)))
        if self.guiSettings.setValue("window/maximized", True):
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def save(self):
        self.guiSettings.setValue("splitter/sizes", self.splitter.sizes())
        self.guiSettings.setValue("window/maximized", self.windowState() & QtCore.Qt.WindowMaximized)
        self.guiSettings.setValue("window/width", self.width())
        self.guiSettings.setValue("window/height", self.height())