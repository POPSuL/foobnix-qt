# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4.QtGui import *


class MidButtonCloseableTabBar(QTabBar):

    def __init__(self):
        super().__init__()

    def mouseReleaseEvent(self, ev):
        """
        @type ev: QMouseEvent
        """
        if ev.button() == QtCore.Qt.MidButton:
            self.tabCloseRequested.emit(self.tabAt(ev.pos()))
        super().mouseReleaseEvent(ev)


class TabbedContainer(QTabWidget):

    def __init__(self, parent=None):
        super(TabbedContainer, self).__init__(parent)
        self.setTabBar(MidButtonCloseableTabBar())
        self.tabBar().setExpanding(False)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.onTabCloseRequest)

    def onTabCloseRequest(self, pos):
        if self.count() > 1:
            self.removeTab(pos)


class Separator(QFrame):

    def __init__(self):
        super(Separator, self).__init__()
        self.setFrameShape(self.VLine)
        self.setFrameShadow(self.Sunken)


class InteractiveLabel(QLabel):

    clicked = QtCore.pyqtSignal(name="clicked")

    def __init__(self, *args, **kwargs):
        super(InteractiveLabel, self).__init__(*args, **kwargs)

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
            ev.accept()
        super(InteractiveLabel, self).mousePressEvent(ev)

    def enterEvent(self, ev):
        self.setProperty("hovered", "true")
        ev.accept()
        super(InteractiveLabel, self).enterEvent(ev)
        self.style().polish(self)

    def leaveEvent(self, ev):
        self.setProperty("hovered", "false")
        ev.accept()
        super(InteractiveLabel, self).enterEvent(ev)
        self.style().polish(self)

    def __str__(self):
        return str(self.text())
