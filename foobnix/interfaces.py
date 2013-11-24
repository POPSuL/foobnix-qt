__author__ = 'popsul'

from PyQt4 import QtCore
from . import Loadable, Savable, Context
from .gui.base_window import BaseWindow
from .gui.perspectives import PerspectivesController
from .perspectives.fs import FSPerspective
from .perspectives.info import InfoPerspective
from .perspectives.vk import VKPerspective
from .perspectives.radio import RadioPerspective


class Interface(QtCore.QObject, Loadable, Savable):
    pass


class GUIInterface(Interface):

    def __init__(self, context):
        """
        @type context foobnix.core.CoreContext
        """
        super().__init__()
        self.context = context

        self.window = BaseWindow(self.createContext())

        self.perspectives = PerspectivesController(self.createContext())
        self.perspectives.attachPerspective(FSPerspective(self.createContext()))
        self.perspectives.attachPerspective(VKPerspective(self.createContext()))
        self.perspectives.attachPerspective(RadioPerspective(self.createContext()))
        self.perspectives.attachPerspective(InfoPerspective(self.createContext()))
        self.window.setPerspectiveController(self.perspectives)

    def load(self):
        self.perspectives.load()
        self.window.load()
        self.window.show()

    def save(self):
        self.window.save()
        self.perspectives.save()

    def createContext(self):
        """
        @rtype GUIContext
        """
        return GUIContext(self)

    def getContext(self):
        """
        @rtype CoreContext
        """
        return self.context


class GUIContext(Context):

    def __init__(self, interface):
        """
        @type interface: GUIInterface
        """
        super().__init__()
        self.__interface = interface
        self.__coreContext = interface.getContext()

    def getBaseWindow(self):
        """
        @rtype PyQt4.QtGui.QMainWindow
        """
        return self.__interface.window

    def showBusyIndicator(self):
        self.getBaseWindow().showBusyIndicator()

    def hideBusyIndicator(self):
        self.getBaseWindow().hideBusyIndicator()

    def setStatusText(self, text):
        self.getBaseWindow().setTitleLabelText(text)

    def getSettings(self, container):
        """
        @type container: str
        @rtype Settings
        """
        return self.__coreContext.getSettings(container)

    def getControls(self):
        """
        @rtype PlaybackControl
        """
        return self.__coreContext.getControls()

    def getPlaylistManager(self):
        """
        @rtype PlaylistContainer
        """
        return self.__interface.window.playlistsContainer

    def getEngine(self):
        """
        @rtype MediaEngine
        """
        return self.__coreContext.getEngine()


class DBusInterface(Interface):

    def __init__(self, context):
        """
        @type context: foobnix.core.CoreContext
        """
        super().__init__()

    def load(self):
        pass

    def save(self):
        pass