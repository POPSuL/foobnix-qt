__author__ = 'popsul'

import time
import logging
from hashlib import md5
from concurrent.futures import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from . import BaseService
from foobnix.settingsprovider import SettingsProvider
from foobnix.thirdparty import pylast

API_KEY = "5249a9b0abb2209ecbfb31b3cec3b9ba"
SECRET_KEY = "fe8beba163b08899da75ea46affe1904"

SETTINGS = "lastfm"


class LastFMSettingsProvider(SettingsProvider):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()
        self.context = context

        self.loginEdit = None
        self.passwordEdit = None
        self.networkSwitcher = None

    def getTab(self):
        l = QFormLayout()
        w = QWidget()
        s = self.context.getSettings(SETTINGS)
        l.setLabelAlignment(Qt.AlignRight)
        l.setFormAlignment(Qt.AlignLeft)
        self.loginEdit = QLineEdit(str(s.value("auth/login", "")))
        self.passwordEdit = QLineEdit(str(s.value("auth/password", "")))
        self.passwordEdit.setEchoMode(QLineEdit.Password)
        self.networkSwitcher = QCheckBox()
        if s.value("network/selected", "lastfm") == "librefm":
            self.networkSwitcher.setCheckState(Qt.Checked)
        l.addRow(self.tr("Login:"), self.loginEdit)
        l.addRow(self.tr("Password:"), self.passwordEdit)
        l.addRow(self.tr("Use Libre.FM instead of Last.FM:"), self.networkSwitcher)
        w.setLayout(l)
        return w, self.tr("Last.FM")

    def save(self):
        s = self.context.getSettings(SETTINGS)
        s.setValue("auth/login", self.loginEdit.text())
        if str(s.value("auth/password", "")) != self.passwordEdit.text():
            s.setValue("auth/password", md5(self.passwordEdit.text().encode("utf-8")).hexdigest())
        if self.networkSwitcher.checkState() == Qt.Checked:
            s.setValue("network/selected", "librefm")
        else:
            s.setValue("network/selected", "lastfm")


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

        self.login = self.settings.value("auth/login", "")
        self.password = self.settings.value("auth/password", "")

        self.context.registerSettingProvider(LastFMSettingsProvider(self.context))

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
                    self.network = pylast.LibreFMNetwork(username=self.login, password_hash=self.password,
                                                         api_key=API_KEY, api_secret=SECRET_KEY)
                else:
                    self.network = pylast.LastFMNetwork(username=self.login, password_hash=self.password,
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