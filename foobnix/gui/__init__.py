# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4.QtGui import *


class TabbedContainer(QTabWidget):

    def __init__(self):
        super(TabbedContainer, self).__init__()
        self.setTabsClosable(True)
        self.tabBar().setExpanding(False)
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
