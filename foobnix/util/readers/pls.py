__author__ = 'popsul'

import os
from PyQt4.QtCore import QUrl, QEventLoop
from PyQt4.QtNetwork import *


class PLSReader(object):

    def __init__(self, path):
        self.data = []
        if os.path.exists(path):
            with open(path) as f:
                self.data = f.readlines()
        elif path.startswith("http"):
            url = QUrl(path)
            loop = QEventLoop()
            manager = QNetworkAccessManager()
            request = QNetworkRequest(url)
            reply = manager.get(request)
            reply.finished.connect(loop.exit)
            loop.exec_()
            if reply.error() == QNetworkReply.NoError:
                self.data = reply.readAll().data().decode('utf-8').split("\n")

    def read(self):
        lines = [l.split("=", 1) for l in self.data if not l.strip().startswith("[")]
        playlist = {}
        out = []
        for l in lines:
            playlist[l[0].strip()] = l[1].strip()
        for i in range(1, int(playlist["NumberOfEntries"])+1):
            si = str(i)
            if "File" + si in playlist:
                out.append({
                    "path": playlist["File" + si],
                    "title": playlist["Title" + si] if "Title" + si in playlist else playlist["File" + si]
                })
        return out
