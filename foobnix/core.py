
__author__ = 'popsul'

import sys
import time
from PyQt4 import QtCore
from PyQt4.QtGui import *
from . import Loadable, Savable, Context
from .settings import SettingsContainer
from .interfaces import GUIInterface, DBusInterface
from .controls import PlaybackControl
from .engine.phonon import PhononEngine


class Core(QtCore.QObject, Loadable, Savable):

    __settings = None
    __window = None
    __perspectives = None
    __interfaces = []
    __controls = None
    __engine = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Core, cls).__new__(cls)
            cls.instance.app = QApplication(sys.argv)
            cls.instance.app.setApplicationName("foobnix-qt")
        return cls.instance

    def __init__(self):
        super().__init__()

    def initSettings(self):
        self.__settings = SettingsContainer()

    def initDataStorage(self):
        print("init data storage")
        pass

    def initEngine(self):
        self.__engine = PhononEngine(self.createContext())

    def initControls(self):
        self.__controls = PlaybackControl(self.createContext())

    def initInterfaces(self):
        self.__interfaces.append(DBusInterface(self.createContext()))
        self.__interfaces.append(GUIInterface(self.createContext()))

    def run(self):
        print("run core")
        t = time.time()
        self.app.aboutToQuit.connect(self.quit)

        self.initSettings()
        self.initDataStorage()
        self.initEngine()
        self.initControls()
        self.initInterfaces()
        self.load()
        print("App started in %.04fs" % (time.time() - t))
        sys.exit(self.app.exec_())

    def quit(self):
        self.save()
        self.__engine.quit()

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

    def createContext(self):
        return CoreContext(self)

    def getSettings(self):
        """
        @rtype SettingsContainer
        """
        return self.__settings

    def getControls(self):
        """
        @rtype PlaybackControl
        """
        return self.__controls

    def getEngine(self):
        """
        @rtype MediaEngine
        """
        return self.__engine


class CoreContext(Context):

    def __init__(self, instance):
        """
        @type instance Core
        """
        super().__init__()
        self.__instance = instance

    def getControls(self):
        """
        @return foobnix.controls.PlaybackControl
        """
        return self.__instance.getControls()

    def getSettings(self, container):
        """
        @type container: str
        @rtype foobnix.settings.SettingsContainer
        """
        return self.__instance.getSettings().getContainer(container)

    def getEngine(self):
        """
        @rtype MediaEngine
        """
        return self.__instance.getEngine()