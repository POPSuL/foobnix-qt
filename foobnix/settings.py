
__author__ = 'popsul'

import os
from PyQt4 import QtCore
from . import Savable, Loadable

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "foobnix-qt")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "foobnix-qt")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


class Settings(QtCore.QSettings, Savable, Loadable):

    valueChanged = QtCore.pyqtSignal(str, object, object, name="valueChanged")

    def __init__(self, name, *__args):
        super().__init__(os.path.join(CONFIG_DIR, name), self.IniFormat)
        self.sync()

    def setValue(self, p_str, p_object):
        oldValue = self.value(p_str)
        super().setValue(p_str, p_object)
        self.valueChanged.emit(p_str, oldValue, p_object)

    def load(self):
        self.sync()

    def save(self):
        self.sync()


class SettingsContainer(QtCore.QObject, Loadable, Savable):

    __containers = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SettingsContainer, cls).__new__(cls)
        return cls.instance

    def getContainer(self, name):
        assert type(name) == str, "Name of container must be str"
        if name not in self.__containers:
            self.__containers[name] = Settings(name)
        return self.__containers[name]

    def load(self):
        for k in self.__containers:
            self.__containers[k].load()

    def save(self):
        for k in self.__containers:
            self.__containers[k].save()