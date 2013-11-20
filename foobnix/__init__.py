
__author__ = "popsul"

from PyQt4 import QtCore


class Savable():

    def save(self):
        raise NotImplementedError()


class Loadable():

    def load(self):
        raise NotImplementedError()


class Context(QtCore.QObject):
    pass