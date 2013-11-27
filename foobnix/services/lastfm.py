__author__ = 'popsul'

import time
import logging
from concurrent.futures import *
from PyQt4.QtCore import *
from . import BaseService
from foobnix.models import Media
from foobnix.thirdparty import pylast

API_KEY = "5249a9b0abb2209ecbfb31b3cec3b9ba"
SECRET_KEY = "fe8beba163b08899da75ea46affe1904"

LOGIN = "popsul"
HASH = ""


class LastFMService(BaseService):

    activationFailed = pyqtSignal(name="activationFailed")

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context
        self._isActive = False
        self._worker = ThreadPoolExecutor(max_workers=1)
        self.network = None
        self.lastError = None
        self.useLibrefm = False

        self.settings = context.getSettings("lastfm")
        if self.settings.value("network/selected", "lastfm") == "librefm":
            self.useLibrefm = True

    @pyqtSlot()
    def activate(self):
        logging.debug("service activated")
        self._activate()

    def _activate(self):
        if self.isActive():
            return

        def connect():
            time.sleep(1)
            try:
                if self.useLibrefm:
                    self.network = pylast.LibreFMNetwork(username=LOGIN, password_hash=HASH,
                                                         api_key=API_KEY, api_secret=SECRET_KEY)
                else:
                    self.network = pylast.LastFMNetwork(username=LOGIN, password_hash=HASH,
                                                        api_key=API_KEY, api_secret=SECRET_KEY)
                return True
            except Exception as e:
                self.lastError = str(e)
                return False

        def connected(f):
            self.context.hideBusyIndicator()
            if not f.result():
                self.activationFailed.emit()
            else:
                self._isActive = True
                self.activated.emit()
        future = self._worker.submit(connect)
        future.add_done_callback(connected)
        self.context.showBusyIndicator()

    @pyqtSlot()
    def deactivate(self):
        logging.debug("service deactivated")
        self.network = None
        self.lastError = None
        self.deactivated.emit()

    def getLastError(self):
        return self.lastError

    def isActive(self):
        return self._isActive

    def submitToWorker(self, f):
        self.context.showBusyIndicator()
        f = self._worker.submit(f)
        f.add_done_callback(lambda *x: self.context.hideBusyIndicator())
        return f

    def getRecommendations(self):
        logging.debug("getTopArtists")
        try:
            user = self.network.get_authenticated_user()
            artists = user.get_recommended_artists()
            logging.debug("Artists getted")
            return artists if artists else []
        except Exception as e:
            logging.error("LFM error: %s" % str(e))
        return []

    def getTopArtists(self):
        logging.debug("getTopArtists")
        try:
            user = self.network.get_authenticated_user()
            artists = user.get_top_artists()
            logging.debug("Artists getted")
            if artists:
                out = []
                for artist, w in artists:
                    out.append(artist)
                return out
        except Exception as e:
            logging.error("LFM error: %s" % str(e))
        return []

    def getTopTracks(self):
        logging.debug("getTopTracks")
        try:
            user = self.network.get_authenticated_user()
            tracks = user.get_top_tracks()
            logging.debug("Tracks getted")
            if tracks:
                out = []
                for track, w in tracks:
                    out.append(track)
                return out
        except Exception as e:
            logging.error("LFM error: %s" % str(e))
        return []

    def getLoved(self):
        logging.debug("getLoved")
        try:
            user = self.network.get_authenticated_user()
            tracks = user.get_loved_tracks()
            logging.debug("Tracks getted")
            if tracks:
                out = []
                for track, d, s in tracks:
                    out.append(track)
                return out
        except Exception as e:
            logging.error("LFM error: %s" % str(e))
        return []

    def getRecent(self):
        logging.debug("getRecent")
        try:
            user = self.network.get_authenticated_user()
            tracks = user.get_recent_tracks()
            logging.debug("Tracks getted")
            if tracks:
                out = []
                for track, d, t in tracks:
                    out.append(track)
                return out
        except Exception as e:
            logging.error("LFM error: %s" % str(e))
        return []