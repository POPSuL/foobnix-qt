# -*- coding: utf-8 -*-

__author__ = 'popsul'

import logging
from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix import Loadable, Savable
from .perspectives import PerspectivesController
from .search import SearchBar
from .playback import PlaybackControls
from .playlist import PlaylistsContainer
from .preferences import PreferencesWindow
from foobnix.settingsprovider import SettingsProvider
from foobnix.util import lookupResource


class GeneralSettingsProvider(SettingsProvider):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context

    def getTab(self):
        l = QFormLayout()
        l.addRow(self.tr("Blah:"), QLineEdit())
        w = QWidget()
        w.setLayout(l)
        return w, self.tr("General")

    def save(self):
        pass


class BaseWindow(QMainWindow, Loadable, Savable):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super(BaseWindow, self).__init__()
        self.context = context
        self.guiSettings = context.getSettings("gui")

        self.setWindowTitle("Foobnix")

        ## set up icons
        paths = QIcon.themeSearchPaths()
        logging.debug("Icon theme path is %s" % lookupResource("icons"))
        QIcon.setThemeSearchPaths([lookupResource("icons")] + paths)
        QIcon.setThemeName("Humanity")

        ## menus
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.viewMenu = self.menuBar().addMenu(self.tr("&View"))
        self.playbackMenu = self.menuBar().addMenu(self.tr("&Playback"))
        self.helpMenu = self.menuBar().addMenu(self.tr("&Help"))

        ## perspectives
        self.leftHBoxWrapper = QWidget(self)

        ## searchbar + playlist contaner
        self.searchBar = SearchBar()
        self.playlistsContainer = PlaylistsContainer(self.context)
        rightHBox = QVBoxLayout()
        rightHBox.addLayout(self.searchBar)
        rightHBox.addWidget(self.playlistsContainer, 1)
        rightHBox.setContentsMargins(0, 0, 0, 0)
        rightHBoxWrapper = QWidget(self)
        rightHBoxWrapper.setLayout(rightHBox)

        ## splitter for left-right sides
        self.splitter = QSplitter(self)
        self.splitterHandler = QSplitterHandle(QtCore.Qt.Horizontal, None)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.leftHBoxWrapper)
        self.splitter.addWidget(rightHBoxWrapper)

        ## statusbar widgets
        self.titleLabel = QLabel(self.tr("Stopped"))
        self.titleLabel.setToolTip(self.tr("Currently playing"))

        self.busyLabel = QLabel()
        self.busyMovie = QMovie(lookupResource("images/spinner.gif"))
        self.busyLabel.setMovie(self.busyMovie)
        self.busyLabel.setToolTip(self.tr("Something is up"))

        self.busyMovie.start()
        self.busyIndicatorAcquiring = 0

        ## base container
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(PlaybackControls(self.context))
        self.vbox.addWidget(self.splitter, 1)

        #self.setLayout(self.vbox)
        wrapper = QWidget(self)
        wrapper.setLayout(self.vbox)
        self.setCentralWidget(wrapper)
        self.statusBar().addWidget(self.titleLabel, 2)
        self.statusBar().addWidget(self.busyLabel, 0)

        self.buildMenu()

        self.context.registerSettingProvider(GeneralSettingsProvider(self.context))

        self.preferences = PreferencesWindow(self.context, parent=self)

    def setTitleLabelText(self, text):
        self.titleLabel.setText(text)

    def showBusyIndicator(self):
        self.busyIndicatorAcquiring += 1
        self.busyLabel.setVisible(True)

    def hideBusyIndicator(self):
        self.busyIndicatorAcquiring -= 1
        if self.busyIndicatorAcquiring < 0:
            self.busyIndicatorAcquiring = 0
        if self.busyIndicatorAcquiring == 0:
            self.busyLabel.setVisible(False)

    def setPerspectiveController(self, pc):
        assert isinstance(pc, PerspectivesController), "argument 1 must be an instance of PerspectiveController"
        self.leftHBoxWrapper.setLayout(pc)

    def buildMenu(self):
        prefs = self.fileMenu.addAction(QIcon.fromTheme("preferences-desktop"), self.tr("&Preferences"))
        quit = self.fileMenu.addAction(QIcon.fromTheme("application-exit"), self.tr("&Quit"))
        prefs.triggered.connect(self.openPreferences)
        prefs.setShortcut(QKeySequence(self.tr("Ctrl+Shift+P")))
        quit.triggered.connect(QApplication.instance().quit)
        quit.setShortcut(QKeySequence(self.tr("Ctrl+Q")))

    def openPreferences(self):
        self.preferences.open()

    def load(self):
        savedSizes = self.guiSettings.value("splitter/sizes", None)
        if savedSizes:
            self.splitter.setSizes([int(k) for k in savedSizes])

        self.resize(int(self.guiSettings.value("window/width", 640)), int(self.guiSettings.value("window/height", 480)))
        if self.guiSettings.setValue("window/maximized", True):
            self.setWindowState(QtCore.Qt.WindowMaximized)
        self.playlistsContainer.load()

    def save(self):
        self.guiSettings.setValue("splitter/sizes", self.splitter.sizes())
        self.guiSettings.setValue("window/maximized", self.windowState() & QtCore.Qt.WindowMaximized)
        self.guiSettings.setValue("window/width", self.width())
        self.guiSettings.setValue("window/height", self.height())
        self.playlistsContainer.save()