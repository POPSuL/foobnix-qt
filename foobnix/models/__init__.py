__author__ = 'popsul'

import os
from hashlib import md5
from PyQt4 import QtCore
from PyQt4 import QtGui


class Media():

    def __init__(self, path=None, artist=None, title=None, parent=None, isMeta=False):
        self.path = path
        self.temporary = not path
        if path:
            self.id = md5(self.path.encode("utf-8")).hexdigest()
        else:
            self.id = None
        self.parent = parent
        self.number = None
        if title:
            self.title = title
        elif os.path.basename(path):
            self.title = os.path.basename(path)
        else:
            self.title = QtCore.QObject().tr("Unknown title")
        self.artist = artist or QtCore.QObject().tr("Unknown artist")
        self.year = None
        self.album = None
        self.duration = None
        self.isRemote = True if path and path.startswith("http://") else False
        self.isMeta = isMeta

    def __eq__(self, other):
        return isinstance(other, Media) and other.id == self.id

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self):
        return "%s - %s" % (self.artist, self.title)


class MediaItem(list):

    def __init__(self, media):
        super().__init__()

        self.media = media

        self.append(QtGui.QStandardItem(QtGui.QIcon(), ""))
        if media.isMeta:
            self.append(QtGui.QStandardItem(""))
            item = QtGui.QStandardItem(1, 3)
            item.setText(self.media.title)
            defFont = item.font()
            defFont.setBold(True)
            item.setFont(defFont)
            item.setColumnCount(3)
            self.append(item)
        else:
            self.append(QtGui.QStandardItem(self.media.number))
            self.append(QtGui.QStandardItem(self.media.artist))
            self.append(QtGui.QStandardItem(self.media.title))
            self.append(QtGui.QStandardItem(self.media.album))
            self.append(QtGui.QStandardItem(self.media.year))
            self.append(QtGui.QStandardItem(str(self.media.duration)))
        for item in self:
            item.setDropEnabled(False)
        self[0].media = self.media


class StandartPlaylistModel(QtGui.QStandardItemModel):

    def __init__(self, *args):
        super().__init__(0, 7)
        self.setHeaderData(0, QtCore.Qt.Horizontal, self.tr("*"))
        self.setHeaderData(1, QtCore.Qt.Horizontal, self.tr("#"))
        self.setHeaderData(2, QtCore.Qt.Horizontal, self.tr("Artist"))
        self.setHeaderData(3, QtCore.Qt.Horizontal, self.tr("Title"))
        self.setHeaderData(4, QtCore.Qt.Horizontal, self.tr("Album"))
        self.setHeaderData(5, QtCore.Qt.Horizontal, self.tr("Year"))
        self.setHeaderData(6, QtCore.Qt.Horizontal, self.tr("Duration"))
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

    def flags(self, index):
        """
        @type index: QModelIndex
        """

        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        #return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled


class PlaylistModel(QtCore.QAbstractItemModel):
    def __init__(self, media=[], parent=None):
        super().__init__(parent)
        self.media = media
        self.root = QtCore.QModelIndex()

    def index(self, row, col, parent):
        if self.hasIndex(row, col, parent):
            return self.createIndex(row, col, 0)
        else:
            return self.root

    def hasChildren(self, parent=None, *args, **kwargs):
        return False if parent.isValid() else True

    def parent(self, index=None):
        return QtCore.QModelIndex()

    def rowCount(self, *args, **kwargs):
        return len(self.media)

    def columnCount(self, *args, **kwargs):
        return 6

    def data(self, index, role=None):
        """
        @type index: QModelIndex
        """
        if not index.isValid():
            return None
        if index.row() > len(self.media):
            return None
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 5:
                return 5
            return "Data for %dx%d — %d" % (index.row(), index.column(), self.media[index.row()][index.column()])
        else:
            return None

    def headerData(self, section, orientation, role=None):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return "Column %d" % section

    def sort(self, column, order=None):
        self.media = sorted(self.media, key=lambda i: i[column],
                            reverse=True if order == QtCore.Qt.DescendingOrder else False)
        self.reset()

    def supportedDragActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction | QtCore.Qt.TargetMoveAction

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction | QtCore.Qt.TargetMoveAction

    def mimeTypes(self):
        return ["application/x-vnd-media-id"]

    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        mimedata.setData('application/x-vnd-media-id', 'mimeData')
        return mimedata

    def flags(self, index):
        """
        @type index: QModelIndex
        """

        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        print(index.parent().isValid())
        if index == self.root:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled

    def beginMoveRows(self, index, first, last, targetIndex, targetChild):
        print("beginMoveRows", index, first, last, targetIndex, targetChild)
        return True