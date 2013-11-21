# -*- coding: utf-8 -*-

__author__ = 'popsul'

import glob
import random
from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.gui import TabbedContainer
from foobnix.models import PlaylistModel, StandartPlaylistModel, Media, MediaItem


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


class DummyPlaylistItem(PlaylistItem):

    count = 0

    def __init__(self):
        super(DummyPlaylistItem, self).__init__()
        count = self.getCount()
        self.setText(0, str(count))
        for i in range(1, 5):
            self.setText(i, "Dummy %d" % count)
        self.setData(5, 0, random.randint(0, 10))

    @staticmethod
    def getCount():
        DummyPlaylistItem.count += 1
        return DummyPlaylistItem.count


class Playlist(QTreeView):

    def __init__(self, context, media=None):
        """
        @type context: GUIContext
        """
        super().__init__()
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

        if media:
            self.addMedias(media)

        self.doubleClicked.connect(self.dbclicked)
        #self.setItemDelegateForColumn(5, RatingDelegate())
        #for i in range(0, 1000):
        #    self.addItem(DummyPlaylistItem())

    def addMedia(self, media):
        assert isinstance(media, Media), "unrecognized media type"
        self.model.appendRow(MediaItem(media))

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
        cell = self.model.item(index.row())
        self.context.getControls().play(cell.media)

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
        self.context.getControls().play(item.media, True)
        self.setPlayIcon(item.media)

    def setPlayIcon(self, media):
        assert isinstance(media, Media)
        setted = False
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            if not setted and item and item == media:
                item.setIcon(QIcon.fromTheme("go-next"))
                setted = True
            else:
                item.setIcon(QIcon())

    def playFirst(self):
        for i in range(0, self.model.rowCount()):
            item = self.model.item(i)
            media = item.media
            if media.isMeta:
                continue
            self.playAt(i)
            return


class PlaylistsContainer(TabbedContainer):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.createPlaylist()

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