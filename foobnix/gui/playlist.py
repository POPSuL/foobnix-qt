# -*- coding: utf-8 -*-

__author__ = 'popsul'

import random
from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.gui import TabbedContainer


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


class Playlist(QTreeWidget):

    def __init__(self):
        super(Playlist, self).__init__()
        header = []
        columns = ["#", "Artist", "Title", "Album", "Year", "Rating"]
        [header.append(k) for k in columns]
        self.setHeaderLabels(header)
        self.setColumnCount(len(columns))
        self.setSortingEnabled(True)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setItemDelegateForColumn(5, RatingDelegate())

        for i in range(0, 1000):
            self.addItem(DummyPlaylistItem())

    def addItem(self, item):
        self.addTopLevelItem(item)

    def dropEvent(self, ev):
        print("dropEvent", ev)
        assert isinstance(ev, QDropEvent)
        super(Playlist, self).dropEvent(ev)

    def dragEnterEvent(self, ev):
        print("dragEnterEvent", ev)
        assert isinstance(ev, QDragEnterEvent)
        ev.acceptProposedAction()
        ev.accept()

    def dragMoveEvent(self, ev):
        assert isinstance(ev, QDragMoveEvent)
        ev.acceptProposedAction()
        ev.accept()


class PlaylistsContainer(TabbedContainer):

    def __init__(self):
        super(PlaylistsContainer, self).__init__()
        self.addTab(self.createNewPlaylist(), "Tab")

    def createNewPlaylist(self):
        return Playlist()