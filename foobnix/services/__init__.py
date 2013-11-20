# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore


class BaseService(QtCore.QObject):

    activated = QtCore.pyqtSignal(name="activated")
