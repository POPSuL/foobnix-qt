
__author__ = 'popsul'

import os
import sys
import time
from PyQt4 import QtCore
from PyQt4.QtGui import *
from . import Loadable, Savable
from .settings import SettingsContainer
from .interfaces import GUIInterface, DBusInterface
from .controls import PlaybackControl


class Core(QtCore.QObject, Loadable, Savable):

    __settings = None
    __window = None
    __perspectives = None
    __interfaces = []
    __controls = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Core, cls).__new__(cls)
            cls.instance.app = QApplication(sys.argv)
        return cls.instance

    def __init__(self):
        super().__init__()

    def initSettings(self):
        self.__settings = SettingsContainer()

    def initDataStorage(self):
        print("init data storage")
        pass

    def initControls(self):
        self.__controls = PlaybackControl()

    def initInterfaces(self):
        self.__interfaces.append(DBusInterface())
        self.__interfaces.append(GUIInterface())

    def run(self):
        print("run core")
        t = time.time()
        self.app.aboutToQuit.connect(self.save)

        self.initSettings()
        self.initDataStorage()
        self.initControls()
        self.initInterfaces()
        self.load()
        print("App started in %.04fs" % (time.time() - t))
        sys.exit(self.app.exec_())

    def save(self):
        self.__controls.save()
        for interface in self.__interfaces:
            interface.save()
        self.__settings.save()

    def load(self):
        self.__settings.load()
        for interface in self.__interfaces:
            interface.load()
        self.__controls.load()

    def getSettings(self):
        return self.__settings

    def getControls(self):
        return self.__controls
