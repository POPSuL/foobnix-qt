__author__ = 'popsul'

import os
import logging
from PyQt4 import QtCore
from PyQt4.QtGui import *
from . import BasePerspective
from foobnix import Loadable, Savable
from foobnix.util import lookupResource
from foobnix.models import Media


class RadioItem(QStandardItem):

    def __init__(self, title, url=None, isMeta=False, parent=None):
        super().__init__(title)
        self.isMeta = isMeta
        self.url = url
        if self.isMeta:
            self.setBold()
        if parent:
            parent.appendRow(self)

    def setBold(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)

    def toMedia(self):
        if self.isMeta:
            medias = [Media(path=None, title=self.text(), isMeta=True)]
            for i in range(0, self.rowCount()):
                item = self.child(i)
                if item:
                    medias.extend(item.toMedia())
            return medias
        else:
            return [Media(path=self.url, title=self.text())]


class RadioTreeModel(QStandardItemModel):

    def __init__(self):
        super().__init__(0, 1)
        self.setHorizontalHeaderLabels([self.tr("Radio list")])


class RadioTreeWidget(QTreeView):

    itemDoubleClicked = QtCore.pyqtSignal(RadioItem, name="itemDoubleClicked")

    def __init__(self):
        super().__init__()
        self.model = RadioTreeModel()
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


class RadioTabbedContainer(QTabWidget):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.setTabPosition(QTabWidget.West)
        self.stockRadios = RadioTreeWidget()
        self.myRadios = RadioTreeWidget()
        self.addTab(self.stockRadios, self.tr("Stock radios"))
        self.addTab(self.myRadios, self.tr("My radios"))

    def getMyRadios(self):
        """
        @rtype RadioTreeWidget
        """
        return self.myRadios

    def getStockRadios(self):
        """
        @rtype RadioTreeWidget
        """
        return self.stockRadios


class RadioPerspective(BasePerspective, Loadable, Savable):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self.settings = context.getSettings("radioperspective")
        self.widget = RadioTabbedContainer(context)
        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)
        self.widget.getMyRadios().itemDoubleClicked.connect(self.doubleClicked)
        self.widget.getStockRadios().itemDoubleClicked.connect(self.doubleClicked)

    def getName(self):
        return "Radio"

    def getIcon(self):
        return QIcon.fromTheme("network-transmit-receive")

    def getWidget(self):
        return self.widget

    def doubleClicked(self, item):
        """
        @type item: RadioItem
        """
        logging.debug("-> doubleClicked handler")
        if item:
            medias = item.toMedia()
            if medias:
                self.context.getPlaylistManager().createPlaylist(item.text(), medias)
                self.context.getControls().stop()
                self.context.getControls().play()
            else:
                logging.info("medias doen't exists")

    def _activated(self):
        logging.debug("Radio perspective activated")

    def _deactivated(self):
        logging.debug("Radio perspective deactivated")

    def _addFpl(self, path):
        if not os.path.exists(path):
            return
        target = self.widget.getStockRadios().model
        basename = os.path.basename(path)[:-4]
        top = RadioItem(basename, isMeta=True)
        target.appendRow(top)
        with open(path, encoding="utf-8") as f:
            for line in f.readlines():
                chunks = [k.strip() for k in line.split("=", 1)]
                if len(chunks) == 2:
                    RadioItem(chunks[0], chunks[1], parent=top)

    def load(self):
        self.widget.setCurrentIndex(int(self.settings.value("perspective/tab", 0)))
        path = lookupResource("radio")
        if path and os.path.isdir(path):
            for (d, dirs, files) in os.walk(path):
                for f in files:
                    self._addFpl(os.path.join(d, f))

    def save(self):
        self.settings.setValue("perspective/tab", self.widget.currentIndex())