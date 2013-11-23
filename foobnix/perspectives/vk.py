# -*- coding: utf-8 -*-

__author__ = 'popsul'

import logging
import threading

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.models import Media
from foobnix.perspectives import BasePerspective
from foobnix.services.vk import VKService


class VKTreeItem(QStandardItem):

    def __init__(self, title, parent=None, service=False, trackEntry=False, userEntry=False):
        super(VKTreeItem, self).__init__(title)

        self.userEntry = userEntry
        self.trackEntry = trackEntry
        self.serviceEntry = service
        self.userId = None
        self.url = None
        self.title = None
        self.artist = None
        self.duration = None

        if service:
            self.setItalic()
        if parent:
            parent.appendRow(self)

    def setItalic(self):
        font = self.font()
        font.setItalic(True)
        self.setFont(font)

    def setBold(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)

    def removeChildren(self):
        self.removeRows(0, self.rowCount())

    def toMedia(self):
        if self.serviceEntry:
            return []
        if self.trackEntry:
            media = Media(path=self.url, artist=self.artist, title=self.title)
            media.duration = self.duration
            return [media]
        if self.userEntry:
            medias = []
            for i in range(0, self.rowCount()):
                item = self.child(i)
                if item:
                    medias.extend(item.toMedia())
            return medias
        raise Exception("Illegal item type")


class VKTreeLoadingItem(VKTreeItem):

    def __init__(self):
        super(VKTreeLoadingItem, self).__init__("Loading", service=True)


class VKTreeModel(QStandardItemModel):

    def __init__(self):
        super(VKTreeModel, self).__init__(0, 1)
        self.clear()
        self.appendRow(VKTreeLoadingItem())

    def clear(self):
        super(VKTreeModel, self).clear()
        self.setHorizontalHeaderLabels(["VK Tree"])


class VKTreeWidget(QTreeView):

    itemDoubleClicked = QtCore.pyqtSignal(QtCore.QModelIndex, name="itemDoubleClicked")

    def __init__(self):
        super(VKTreeWidget, self).__init__()
        self.model = VKTreeModel()
        self.setModel(self.model)
        self.setDragEnabled(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def mouseDoubleClickEvent(self, ev):
        """
        @type ev: QMouseEvent
        """
        index = self.indexAt(ev.pos())
        self.itemDoubleClicked.emit(index)
        ev.accept()


class VKPerspective(BasePerspective):

    profilesLoaded = QtCore.pyqtSignal(list, name="profilesLoaded")

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super(VKPerspective, self).__init__()
        self.context = context
        self.widget = VKTreeWidget()
        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)
        self.service = VKService(context)
        self.service.activated.emit()
        self.loaded = False
        self.cache = []
        self.widget.expanded.connect(self.expanded)
        self.widget.itemDoubleClicked.connect(self.doubleClicked)

    def getName(self):
        return "VK"

    def getWidget(self):
        return self.widget

    def expanded(self, index):
        item = self.widget.model.itemFromIndex(index)
        if item:
            if item.userId in self.cache:
                return
            tracks = self.service.getUserTracks(item.userId)
            self.cache.append(item.userId)
            item.removeChildren()
            if tracks:
                for track in tracks:
                    row = VKTreeItem("%s - %s" % (track["artist"], track["title"]), parent=item, trackEntry=True)
                    row.url = track['url']
                    row.artist = track['artist']
                    row.title = track['title']
                    row.aid = track['id']
                    row.owner = track['owner_id']
                    row.duration = track['duration']
            else:
                row = VKTreeItem("Nothing found", parent=item, service=True)

    def doubleClicked(self, index):
        logging.debug("doubleClicked")
        self.expanded(index)
        item = self.widget.model.itemFromIndex(index)
        if item:
            medias = item.toMedia()
            if medias:
                self.context.getPlaylistManager().createPlaylist(item.text(), medias)
                self.context.getControls().play()
            else:
                logging.warning("No medias found")
        else:
            logging.warning("item doesn't exists")

    def clear(self):
        self.widget.model.clear()

    def appendProfile(self, data):
        if not data:
            return
        if isinstance(data, dict):
            data = [data]
        print(data)
        for profile in data:
            row = VKTreeItem("%s %s" % (profile["first_name"], profile["last_name"]), userEntry=True)
            row.userId = profile["id"]
            row.appendRow(VKTreeLoadingItem())
            row.setBold()
            self.widget.model.appendRow(row)

    @QtCore.pyqtSlot(list)
    def populateTree(self, data):
        print("populateTree", data)
        self.appendProfile(data)

    def loadProfiles(self):
        def task():
            profiles = []
            profile = self.service.getProfile()
            if not profile:
                return
            profiles += profile
            uids = self.service.getFriends()
            if uids:
                profiles += self.service.getProfiles(",".join(["%s" % i for i in uids]))
            #self.profilesLoaded.emit(profiles)
            self.appendProfile(profiles)

        threading.Thread(target=task).start()

    def _activated(self):
        self.service.setUp()
        print("VK perspective activated")
        if not self.loaded:
            self.clear()
            self.loadProfiles()
            self.loaded = True

    def _deactivated(self):
        print("VK perspective deactivated")
