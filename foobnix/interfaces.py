__author__ = 'popsul'

from PyQt4 import QtCore
from . import Loadable, Savable
from .gui.base_window import BaseWindow
from .gui.perspectives import PerspectivesController
from .perspectives.fs import FSPerspective
from .perspectives.info import InfoPerspective
from .perspectives.vk import VKPerspective


class Interface(QtCore.QObject, Loadable, Savable):
    pass


class GUIInterface(Interface):

    def __init__(self):
        super().__init__()
        self.window = BaseWindow()
        self.perspectives = PerspectivesController()
        self.perspectives.attachPerspective(FSPerspective())
        self.perspectives.attachPerspective(VKPerspective())
        self.perspectives.attachPerspective(InfoPerspective())
        self.window.setPerspectiveController(self.perspectives)

    def load(self):
        self.perspectives.load()
        self.window.load()
        self.window.show()

    def save(self):
        self.window.save()
        self.perspectives.save()


class DBusInterface(Interface):

    def __init__(self):
        super().__init__()

    def load(self):
        pass

    def save(self):
        pass