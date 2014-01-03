# -*- coding: utf-8 -*-

__author__ = 'popsul'

import os
import pickle
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix import Loadable, Savable
from foobnix.gui import TabbedContainer, MidButtonCloseableTabBar
from foobnix.util.playlist import expandPlaylist, isPlaylist
from foobnix.util.tags import fillTags
from foobnix.models import StandartPlaylistModel, Media, MediaItem
from foobnix.settings import CACHE_DIR


class RatingDelegate(QItemDelegate):

    def __init__(self):
        super().__init__()
        self.pixmaps = []
        for i in range(0, 11):
            self.pixmaps.append(QImage("./share/foobnix/rating-%d.png" % i))
        self.overrideRating = None

    def paint(self, painter, options, index):
        if self.overrideRating:
            rating = self.overrideRating
        else:
            rating = index.data(0)

        if rating < 0:
            rating = 0
        elif rating > 10:
            rating = 10

        pixmap = self.pixmaps[rating]
        painter.drawImage(options.rect.x(), options.rect.y(), pixmap)

    def sizeHint(self, QStyleOptionViewItem, QModelIndex):
        return QtCore.QSize(94, 17)

    def editorEvent(self, event, QAbstractItemModel, QStyleOptionViewItem, QModelIndex):
        if event.type() == QtCore.QEvent.HoverMove:
            seg = int(event.pos().x() / 94 / 10)
            if seg < 0:
                seg = 0
            elif seg > 10:
                seg = 10
            self.overrideRating = seg
        elif event.type() == QtCore.QEvent.HoverLeave:
            self.overrideRating = None


class PlaylistItem(QTreeWidgetItem):

    def __init__(self):
        super(PlaylistItem, self).__init__(None)


class Playlist(QTreeView):

    itemAdded = QtCore.pyqtSignal(MediaItem, name="itemAdded")

    def __init__(self, context, media=None):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.updateWorker = ThreadPoolExecutor(max_workers=1)
        self.context = context
        self.model = StandartPlaylistModel()
        self.setModel(self.model)
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setIndentation(0)
        self.setColumnWidth(0, 32)
        self.setColumnWidth(1, 32)
        self.setColumnWidth(5, 50)
        self.header().setResizeMode(0, QHeaderView.Fixed)
        self.header().setResizeMode(1, QHeaderView.Fixed)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.model.modelReset.connect(self.modelReset)
        self.itemAdded.connect(self._itemAddedSlot)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        if media:
            for (i, m) in enumerate(media):
                if not m.isMeta and isPlaylist(m):
                    media[i].isMeta = True
                    media[i+1:i+1] = expandPlaylist(m)
                    break
                if not m.isMeta and m.path:
                    break
            self.addMedias(media)

        self.doubleClicked.connect(self.dbclicked)

    def modelReset(self):
        print("Model reseted")

    def openContextMenu(self, point):
        """
        @type point: QPoint
        """
        selection = self.selectionModel().selectedRows()
        menu = QMenu()
        menu.addAction(QIcon.fromTheme("edit-delete"), self.tr("Delete"),
                       self.deleteSelected, QKeySequence(QtCore.Qt.Key_Delete))
        menu.exec(self.mapToGlobal(point))

    def deleteSelected(self):
        while 1:
            selection = self.selectionModel().selectedIndexes()
            if selection:
                for index in selection:
                    self.model.takeRow(index.row())
                    break
            else:
                break

    def addMedia(self, media):
        assert isinstance(media, Media), "unrecognized media type"
        item = MediaItem(media)
        self.model.appendRow(item)
        self.itemAdded.emit(item)

    def addMedias(self, medias):
        assert isinstance(medias, list), "medias must be a list"
        for m in medias:
            self.addMedia(m)

    def dbclicked(self, index):
        """
        @type index: QModelIndex
        """
        if not index.isValid():
            return
        self.playAt(index.row())

    def addItem(self, item):
        self.addTopLevelItem(item)

    def dragMoveEvent(self, ev):
        assert isinstance(ev, QDragMoveEvent)
        super().dragMoveEvent(ev)
        ev.accept()

    def playAt(self, row):
        item = self.model.item(row)
        assert isinstance(item, QStandardItem), "unrecognized item type"
        assert isinstance(item.media, Media), "unrecognized media"
        if item.media.isMeta:
            return False
        self.context.getControls().play(item.media, True)

    def setPlayIcon(self, media):
        assert isinstance(media, Media)
        logging.debug("setPlayIcon(%s)" % media.path)
        setted = False
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            if not setted and item and item.media == media:
                item.setIcon(QIcon.fromTheme("go-next"))
                setted = True
            else:
                item.setIcon(QIcon())

    def getPrevious(self, shuffle=False):
        logging.debug("getPrevious called")
        if self.model.rowCount() == 0:
            logging.debug("model is empty")
            return None
        startFrom = self.getRowWithPlayIcon() - 1
        if startFrom < 0:
            startFrom = self.model.rowCount() - 1
        logging.debug("starts from %d" % startFrom)
        iteration = 0
        while 1:
            if iteration > 1:
                return None
            for i in range(startFrom, -1, -1):
                logging.debug("check %d" % i)
                item = self.model.item(i)
                if item and not item.media.isMeta:
                    return item.media

            if startFrom != self.model.rowCount() - 1:
                startFrom = self.model.rowCount() - 1
                iteration += 1
            else:
                return None

    def getNext(self, shuffle=False, repeatAll=False):
        logging.debug("getNext called")
        if self.model.rowCount() == 0:
            return None
        startFrom = self.getRowWithPlayIcon() + 1
        if startFrom >= self.model.rowCount():
            startFrom = 0
        iteration = 0
        while 1:
            if iteration > 1:
                return None
            for i in range(startFrom, self.model.rowCount()):
                item = self.model.item(i)
                if item and not item.media.isMeta:
                    return item.media

            if repeatAll and startFrom != 0:
                startFrom = 0
                iteration += 1
            else:
                return None

    def getCurrent(self):
        row = self.getRowWithPlayIcon()
        if row != -1:
            item = self.model.item(row)
            if item and not item.media.isMeta:
                return item.media
        rows = self.selectionModel().selectedRows()
        for row in rows:
            item = self.model.item(row.row())
            if item and not item.media.isMeta:
                return item.media
        return self.getFirst()

    def getRowWithPlayIcon(self):
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            if item and not item.icon().isNull():
                return i
        return -1

    def getFirst(self):
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            if item and not item.media.isMeta:
                return item.media

    def playFirst(self):
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            media = item.media
            if media.isMeta:
                continue
            self.playAt(i)
            return

    def _itemAddedSlot(self, item):
        if item.media.isMeta or not isPlaylist(item.media):
            return

        print("is playlist!")

        def do_update(f):
            print("future done")
            index = self.model.indexFromItem(item[0])
            if not index.isValid():
                return
            expanded = f.result()
            if expanded:
                i = index.row()
                taked = self.model.takeRow(i)[0]
                taked.media.isMeta = True
                self.model.insertRow(i, MediaItem(taked.media))
                for (idx, media) in enumerate(expanded):
                    self.model.insertRow(i + idx + 1, MediaItem(media))
        future = self.updateWorker.submit(expandPlaylist, item.media)
        future.add_done_callback(do_update)
        print("submitted")

    def _doUpdateMedia(self, media):
        def updated(f):
            pass
        future = self.updateWorker.submit(fillTags, media)
        future.add_done_callback(updated)

    def getAllMedias(self):
        return [self.model.item(k).media for k in range(0, self.model.rowCount())]


class PlaylistTabBar(MidButtonCloseableTabBar):

    newPlaylistRequest = QtCore.pyqtSignal(name="newPlaylistRequest")

    def __init__(self):
        super().__init__()
        self.lastSelectedTab = -1
        self.menu = QMenu(self)
        self.newAction = QAction(self.tr("New playlist"), self)
        self.closeAction = QAction(self.tr("Close tab"), self)
        self.closeToLeft = QAction(self.tr("Close to left"), self)
        self.closeToRight = QAction(self.tr("Close to right"), self)
        self.renameTab = QAction(self.tr("Rename tab"), self)
        self.menu.addActions([self.newAction, self.closeAction, self.closeToLeft, self.closeToRight, self.renameTab])
        self.newAction.triggered.connect(self.newPlaylistHandler)
        self.closeAction.triggered.connect(self.closeTabHandler)
        self.closeToLeft.triggered.connect(self.closeToLeftHandler)
        self.closeToRight.triggered.connect(self.closeToRightHandler)

    def contextMenuEvent(self, ev):
        self.renameTab.setEnabled(False)
        self.closeAction.setEnabled(False)
        self.closeToLeft.setEnabled(False)
        self.closeToRight.setEnabled(False)
        self.lastSelectedTab = tab = self.tabAt(ev.pos())
        logging.debug("Selected Tab: %d" % tab)
        logging.debug("Total tabs: %d" % self.count())
        if tab >= 0:
            self.renameTab.setEnabled(True)
            self.closeAction.setEnabled(True)
            if tab > 0:
                self.closeToLeft.setEnabled(True)
            if tab < self.count() - 1:
                self.closeToRight.setEnabled(True)
        self.menu.popup(ev.globalPos())
        ev.accept()

    def newPlaylistHandler(self):
        self.newPlaylistRequest.emit()

    def closeTabHandler(self):
        if self.lastSelectedTab != -1:
            self.tabCloseRequested.emit(self.lastSelectedTab)

    def closeToLeftHandler(self):
        if self.lastSelectedTab != -1:
            for x in range(self.lastSelectedTab - 1, -1, -1):
                self.tabCloseRequested.emit(x)

    def closeToRightHandler(self):
        logging.debug("closeToRightHandler %d:%d" % (self.lastSelectedTab, self.count()))
        if self.lastSelectedTab != -1:
            for x in range(self.count() - 1, self.lastSelectedTab, -1):
                self.tabCloseRequested.emit(x)


class PlaylistsContainer(TabbedContainer, Savable, Loadable):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.setTabBar(PlaylistTabBar())
        self.tabBar().setExpanding(False)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.controls = self.context.getControls()
        self.controls.needNext.connect(self.playNext)
        self.controls.needPrev.connect(self.playPrev)
        self.controls.needCurrent.connect(self.playCurrent)
        self.controls.stateChanged.connect(self.stateChanged)
        self.tabBar().newPlaylistRequest.connect(lambda: self.createPlaylist())

    def load(self):
        try:
            if not os.path.exists(os.path.join(CACHE_DIR, "playlists")):
                self.createPlaylist()
                return
            with open(os.path.join(CACHE_DIR, "playlists"), "rb") as f:
                pickled = f.read()
                playlists = pickle.loads(pickled)
                if not isinstance(playlists, list):
                    raise Exception("Illegal data type")
                playlists.reverse()
                for p in playlists:
                    logging.debug("restoring %s with %d medias" % (p["title"], len(p["medias"])))
                    self.createPlaylist(p["title"], p["medias"])
        except:
            self.createPlaylist()

    def save(self):
        playlists = []
        for i in range(0, self.count()):
            title = self.tabText(i)
            widget = self.widget(i)
            p = {
                "title": title,
                "medias": widget.getAllMedias()
            }
            playlists.append(p)
            logging.debug("storing %s with %d medias" % (p["title"], len(p["medias"])))
        with open(os.path.join(CACHE_DIR, "playlists"), "wb") as f:
            pickle.dump(playlists, f, 3)

    def __createPlaylist(self, media):
        return Playlist(self.context, media=media)

    def getCurrent(self):
        w = self.currentWidget()
        assert isinstance(w, Playlist), "unrecognized widget type"
        return w

    def createPlaylist(self, title=None, media=None):
        if not title:
            title = self.tr("Playlist")
        if not media:
            media = []

        playlist = self.__createPlaylist(media)
        index = self.insertTab(0, playlist, title)
        self.setCurrentIndex(index)
        return playlist

    def playNext(self, shuffle, repeatAll):
        current = self.getCurrent()
        assert isinstance(current, Playlist), "playlist not provided"
        media = current.getNext(shuffle, repeatAll)
        if media:
            self.controls.play(media)

    def playPrev(self, shuffle):
        current = self.getCurrent()
        assert isinstance(current, Playlist), "playlist not provided"
        media = current.getPrevious(shuffle)
        if media:
            self.controls.play(media)

    def playCurrent(self):
        current = self.getCurrent()
        assert isinstance(current, Playlist), "playlist not provided"
        media = current.getCurrent()
        if media:
            self.controls.play(media)

    def stateChanged(self, state, media):
        logging.debug("state changed: %s" % state)
        if media and state == self.controls.StatePlay:
            current = self.getCurrent()
            if current:
                current.setPlayIcon(media)