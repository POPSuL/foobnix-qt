# -*- coding: utf-8 -*-

__author__ = 'popsul'

import os
import json

from PyQt4 import QtCore
from PyQt4.QtCore import QUrl, pyqtSlot
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from html.parser import HTMLParser
from foobnix.services import BaseService

scope = ["audio", "friends", "wall"]
appId = "2234333"
authUrl = "http://oauth.vk.com/oauth/authorize?" + \
          "redirect_uri=http://oauth.vk.com/blank.html&response_type=token&" + \
          "client_id=%s&scope=%s&layout=popup&display=page" % (appId, ",".join(scope))


class PersistentCookieJar(QNetworkCookieJar):

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.load()

    def load(self):
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        if not os.path.exists(self.path):
            return
        with open(self.path) as f:
            cookies = []
            for l in f.readlines():
                cookies += QNetworkCookie.parseCookies(l)
            self.setAllCookies(cookies)

    def save(self):
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            for cookie in self.allCookies():
                f.write(cookie.toRawForm().data().decode('utf-8'))
                f.write("\n")


class VKAuthDialog(QDialog):

    def __init__(self, parent=None):
        super(VKAuthDialog, self).__init__(parent)

        self.eventLoop = QtCore.QEventLoop()

        ## build gui
        self.setWindowTitle("VK Auth")
        self.webView = QWebView()
        storage = os.path.join(os.path.expanduser("~"), ".config", "foobnix-qt", "vk.cookie")
        self.cookieJar = PersistentCookieJar(storage)
        self.webView.page().networkAccessManager().setCookieJar(self.cookieJar)
        self.setFixedSize(610, 318)
        #self.webView.page().setViewportSize(QtCore.QSize(640, 480))
        #self.webView.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.webView, 1)
        self.setLayout(layout)

        ##
        self.webView.load(QUrl(authUrl))
        self.webView.urlChanged.connect(self.urlChanged)
        self.webView.loadFinished.connect(self.loadFinished)
        self.oauthData = None

    @staticmethod
    def getToken():
        dialog = VKAuthDialog(QApplication.activeWindow())
        dialog.eventLoop.exec(QtCore.QEventLoop.AllEvents)
        if dialog.oauthData:
            return dialog.oauthData
        result = dialog.exec_()
        if result:
            return dialog.oauthData
        return None

    @pyqtSlot()
    def loadFinished(self):
        pass

    @pyqtSlot(QUrl)
    def urlChanged(self, url):
        self.cookieJar.save()
        if url.path() == "/blank.html":
            def split_key_value(kv_pair):
                kv = kv_pair.split("=")
                if len(kv) == 2:
                    return kv[0], kv[1]  # ["key", "val"], e.g. key=val
                else:
                    return kv[0], None  # ["key"], e.g. key= or key
            self.oauthData = dict(split_key_value(kv_pair) for kv_pair in str(url.fragment()).split("&"))
            self.done(1)
        self.eventLoop.exit()


class VKService(BaseService):

    def __init__(self):
        super(VKService, self).__init__()
        self.connected = False
        self.authData = None
        self.nmanager = QNetworkAccessManager()

    def setUp(self):
        self.getUserToken()     # fake connecting

    def isConnected(self):
        return self.connected

    def getUserToken(self, makeNewToken=False):
        if self.authData and "access_token" in self.authData and not makeNewToken:
            self.connected = True
            return self.authData["access_token"]
        self.authData = VKAuthDialog.getToken()
        print("auth data", self.authData)
        if self.authData and "access_token" in self.authData:
            self.connected = True
            return self.authData["access_token"]
        self.connected = False
        return None

    def apiRequest(self, method, data):
        if not self.isConnected():
            return None
        url = "https://api.vk.com/method/%(METHOD_NAME)s?%(PARAMETERS)s&access_token=%(ACCESS_TOKEN)s" % {
            'METHOD_NAME': method,
            'PARAMETERS': data,
            'ACCESS_TOKEN': self.getUserToken()}
        print("api url %s" % url)
        url = QUrl(url)
        loop = QtCore.QEventLoop()
        request = QNetworkRequest(url)
        reply = self.nmanager.get(request)
        reply.finished.connect(loop.exit)
        loop.exec_()
        if reply.error() == QNetworkReply.NoError:
            answer = reply.readAll().data().decode('utf-8')
            data = self.jsonToDict(answer)
            if "error" in data:
                print("error found")
            else:
                return data["response"]

        return None

    def jsonToDict(self, j):
        return json.loads(j)

    def getProfile(self, userId=None):
        if not self.isConnected():
            return None
        if not userId:
            userId = self.authData["user_id"]
        return self.apiRequest("getProfiles", "uid=" + str(userId))

    def getProfiles(self, uids):
        if not self.isConnected():
            return None
        return self.apiRequest("getProfiles", "uids=" + str(uids))

    def getFriends(self, userId=None):
        if not self.isConnected():
            return None
        if not userId:
            userId = self.authData["user_id"]
        return self.apiRequest("friends.get", "uid=" + str(userId))

    def getUserTracks(self, userId=None):
        if not self.isConnected():
            return None
        if not userId:
            userId = self.authData["user_id"]
        return self.apiRequest("audio.get", "uid=" + str(userId))
