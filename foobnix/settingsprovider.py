__author__ = 'popsul'

from PyQt4.QtCore import *


class SettingsProvider(QObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getTab(self):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()