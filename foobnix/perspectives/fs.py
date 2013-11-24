# -*- coding: utf-8 -*-

__author__ = 'popsul'

import os
from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix import Savable, Loadable
from foobnix.gui import TabbedContainer
from foobnix.util import createMediasForPaths
from foobnix.perspectives import BasePerspective


supportedFiles = ["*.mp3", "*.m3u", "*.pls", "*.wav", "*.flac", "*.mp4", "*.aac", "*.m4a", "*.cue"]


class FSTreeView(QTreeView):

    itemDoubleClicked = QtCore.pyqtSignal(str, name="itemDoubleClicked")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeModel = QFileSystemModel()
        self.setModel(self.treeModel)

    def mouseDoubleClickEvent(self, ev):
        """
        @type ev: QMouseEvent
        """
        index = self.indexAt(ev.pos())
        self.itemDoubleClicked.emit(self.treeModel.filePath(index))
        ev.accept()


class FSTabPage(QWidget):
    tabRenameRequested = QtCore.pyqtSignal(str, name="tabRenameRequested")

    def __init__(self, context, path=None):
        """
        @type context: GUIContext
        @type path: str
        """
        super().__init__()

        self.context = context
        self.rootPath = None

        ## build gui
        self.layout = QStackedLayout()
        self.tree = FSTreeView()
        self.treeModel = self.tree.treeModel
        self.tree.setModel(self.treeModel)
        # hide additional columns
        [self.tree.hideColumn(i) for i in range(1, self.treeModel.columnCount())]
        self.button = QPushButton("Select directory")
        hbox = QHBoxLayout()
        hbox.addWidget(self.button)
        wrapper = QWidget()
        wrapper.setLayout(hbox)
        self.layout.addWidget(wrapper)
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)

        ## set up
        self.treeModel.setNameFilters(supportedFiles)
        self.treeModel.setNameFilterDisables(False)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(False)
        self.button.clicked.connect(self.selectPath)
        if path:
            self.setRootPath(path)
            self.layout.setCurrentIndex(1)
        else:
            self.layout.setCurrentIndex(0)

        self.tree.itemDoubleClicked.connect(self.playPath)

    def playPath(self, path):
        if os.path.isdir(path):
            title = os.path.basename(path)
        else:
            title = os.path.basename(os.path.dirname(path))

        medias = createMediasForPaths([path])
        playlist = self.context.getPlaylistManager().createPlaylist(title, medias)
        playlist.playFirst()

    def selectPath(self):
        path = QFileDialog.getExistingDirectory(self, "Select a directory")
        if path:
            self.setRootPath(path)

    def setRootPath(self, path):
        self.rootPath = path
        index = self.treeModel.setRootPath(self.rootPath)
        self.tree.setRootIndex(index)
        self.layout.setCurrentIndex(1)
        self.tabRenameRequested.emit(QtCore.QDir(path).dirName())

    def rootPath(self):
        return self.rootPath


class FSTabbedWidget(TabbedContainer):
    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.setTabPosition(QTabWidget.West)

        self.menu = QMenu()
        self.addTabAction = QAction("Add empty tab", self)
        self.menu.addAction(self.addTabAction)
        self.selectOtherDirAction = QAction("Select another dir", self)
        self.menu.addAction(self.selectOtherDirAction)
        self.addTabAction.triggered.connect(lambda *a: self.addTab())
        self.selectOtherDirAction.triggered.connect(lambda *a: self.currentWidget().selectPath())

    def addTab(self, label="Empty", path=None):
        page = FSTabPage(self.context, path)

        def renameTabPage(name):
            index = self.indexOf(page)
            if index is not None:
                self.setTabText(index, name)

        page.tabRenameRequested.connect(renameTabPage)
        return super().addTab(page, label)

    def contextMenuEvent(self, ev):
        self.menu.popup(ev.globalPos())
        ev.accept()


class FSPerspective(BasePerspective, Savable, Loadable):
    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.settings = context.getSettings("fsperspective")
        self.widget = FSTabbedWidget(context)
        self.widget.addTab()

        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)

    def getName(self):
        return "FS"

    def getIcon(self):
        return QIcon.fromTheme("drive-harddisk")

    def getWidget(self):
        return self.widget

    def _activated(self):
        print("FS perspective activated")

    def _deactivated(self):
        print("FS perspective deactivated")

    def load(self):
        self.widget.clear()
        tabs = self.settings.value("perspective/tabs")
        if tabs:
            for tab in tabs:
                self.widget.addTab(label=tab["title"], path=tab["path"])
            self.widget.setCurrentIndex(int(self.settings.value("perspective/selected", 0)))
        else:
            self.widget.addTab()

    def save(self):
        tabs = []
        for i in range(0, self.widget.count()):
            title = self.widget.tabText(i)
            path = self.widget.widget(i).rootPath
            tabs.append({
                "title": title,
                "path": path
            })
        self.settings.setValue("perspective/tabs", tabs)
        self.settings.setValue("perspective/selected", self.widget.currentIndex())
