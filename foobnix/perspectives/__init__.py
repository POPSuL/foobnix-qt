# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4.QtCore import QObject, pyqtSignal


class BasePerspective(QObject):

    deactivated = pyqtSignal(name="deactivated")

    activated = pyqtSignal(name="activated")

    def __init__(self, context=None):
        super().__init__()

    def getName(self):
        pass

    def getIcon(self):
        pass

    def getWidget(self):
        pass