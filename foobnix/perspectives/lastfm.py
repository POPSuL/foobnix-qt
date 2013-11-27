__author__ = 'popsul'

import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from . import BasePerspective
from foobnix import Loadable, Savable
from foobnix.services.lastfm import LastFMService
from foobnix.thirdparty import pylast


class LastFMTreeItem(QStandardItem):

    def __init__(self, title, url=None, isMeta=False, addDummy=False, parent=None):
        super().__init__(title)
        self.isMeta = isMeta
        self.url = url
        self.method = None
        if self.isMeta:
            self.setBold()
        if parent:
            parent.appendRow(self)

        if addDummy:
            d = LastFMTreeItem(QObject().tr("Loading..."), parent=self)
            d.setItalic()

    def setBold(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)

    def setItalic(self):
        font = self.font()
        font.setItalic(True)
        self.setFont(font)

    @staticmethod
    def fromMedia(media):
        return LastFMTreeItem(str(media), url=media.path)

    @staticmethod
    def fromTrack(track):
        assert isinstance(track, pylast.Track), "illegal track type"
        return LastFMTreeItem("%s - %s" % (track.artist.name, track.title))

    @staticmethod
    def fromArtist(artist):
        assert isinstance(artist, pylast.Artist)
        return LastFMTreeItem(artist.name)

    def removeChildren(self):
        self.removeRows(0, self.rowCount())


class LastFMTreeModel(QStandardItemModel):

    def __init__(self):
        super().__init__()


class LastFMTree(QTreeView):

    itemDoubleClicked = pyqtSignal(LastFMTreeItem, name="itemDoubleClicked")

    def __init__(self):
        super().__init__()
        self.model = LastFMTreeModel()
        self.setModel(self.model)
        self.setDragEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def mouseDoubleClickEvent(self, ev):
        """
        @type ev: QMouseEvent
        """
        index = self.indexAt(ev.pos())
        item = self.model.itemFromIndex(index)
        if item:
            logging.debug("mouseDoubleClickEvent")
            self.itemDoubleClicked.emit(item)
            ev.accept()


class LastFMPerspective(BasePerspective, Loadable, Savable):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.service = LastFMService(self.context)
        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)

        self.layoutWrapper = QWidget()
        self.widget = QStackedLayout()
        self.loadingWidget = self._createLoadingWidget()
        self.errorWidget = self._createErrorWidget()
        self.baseWidget = self._createBaseWidget()
        self.widget.addWidget(self.loadingWidget)
        self.widget.addWidget(self.errorWidget)
        self.widget.addWidget(self.baseWidget)
        self.widget.setCurrentIndex(0)
        self.layoutWrapper.setLayout(self.widget)

        self.service.activationFailed.connect(self._activationFailed)
        self.service.activated.connect(self._serviceActivated)

        self.baseWidget.expanded.connect(self.expanded)

        self.__cache = []

    def getIcon(self):
        return QIcon.fromTheme("network-wired")

    def getName(self):
        if not self.service.useLibrefm:
            return self.tr("Last.FM")
        else:
            return self.tr("Libre.FM")

    def getWidget(self):
        return self.layoutWrapper

    def _createLoadingWidget(self):
        w = QLabel(self.tr("This perspective will be loaded in some time"))
        w.setAlignment(Qt.AlignCenter)
        return w

    def _createErrorWidget(self):
        w = QLabel(self.tr("<b>Oups...</b>"))
        w.setAlignment(Qt.AlignCenter)
        return w

    def _createBaseWidget(self):
        w = LastFMTree()
        recommendations = LastFMTreeItem(self.tr("My recommendations"), isMeta=True, addDummy=True)
        topArtists = LastFMTreeItem(self.tr("My top artists"), isMeta=True, addDummy=True)
        topTracks = LastFMTreeItem(self.tr("My top tracks"), isMeta=True, addDummy=True)
        lovedTracks = LastFMTreeItem(self.tr("My loved"), isMeta=True, addDummy=True)
        recentTracks = LastFMTreeItem(self.tr("My recent"), isMeta=True, addDummy=True)
        recommendations.method = self.service.getRecommendations
        topArtists.method = self.service.getTopArtists
        topTracks.method = self.service.getTopTracks
        lovedTracks.method = self.service.getLoved
        recentTracks.method = self.service.getRecent
        w.model.appendRow(recommendations)
        w.model.appendRow(topArtists)
        w.model.appendRow(topTracks)
        w.model.appendRow(lovedTracks)
        w.model.appendRow(recentTracks)
        return w

    def _activationFailed(self):
        baseMessage = self.tr("<b>Oups.. Something wrong</b><br /> %s")
        errMessage = baseMessage % self.service.getLastError()
        self.errorWidget.setText(errMessage)
        logging.warning("Lastfm service actiovation failed")
        self.widget.setCurrentIndex(1)

    def _serviceActivated(self):
        logging.debug("Lastfm service activated")
        if self.service.useLibrefm:
            self.baseWidget.model.setHorizontalHeaderLabels([self.tr("Libre.FM")])
        else:
            self.baseWidget.model.setHorizontalHeaderLabels([self.tr("Last.FM")])
        self.widget.setCurrentIndex(2)

    def expanded(self, index):
        """
        @type index: QModelIndex
        """

        item = self.baseWidget.model.itemFromIndex(index)
        if item and item.method:
            if item.text() in self.__cache:
                return
            self.__cache.append(item.text())

            def populate(f):
                medias = f.result()
                assert isinstance(medias, list), "undefined result"
                item.removeChildren()
                if medias:
                    for media in medias:
                        if isinstance(media, pylast.Track):
                            mediaItem = LastFMTreeItem.fromTrack(media)
                        elif isinstance(media, pylast.Artist):
                            mediaItem = LastFMTreeItem.fromArtist(media)
                        else:
                            mediaItem = LastFMTreeItem.fromMedia(media)
                        item.appendRow(mediaItem)
                else:
                    LastFMTreeItem(self.tr("Nothing found"), parent=item).setItalic()
                    try:
                        del self.__cache[self.__cache.index(item.text())]
                    except ValueError as e:
                        pass

            future = self.service.submitToWorker(item.method)
            future.add_done_callback(populate)

    def _activated(self):
        pass

    def _deactivated(self):
        pass

    def load(self):
        self.service.activate()

    def save(self):
        self.service.deactivate()
