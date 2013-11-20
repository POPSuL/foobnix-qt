# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix import Loadable, Savable
from foobnix.perspectives import BasePerspective


class PerspectivesController(QVBoxLayout, Loadable, Savable):

    def __init__(self):
        super(PerspectivesController, self).__init__()

        self.attachedPerspectives = []
        self.buttons = []
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonClicked.connect(self.activateHandler)

        ## build gui
        self.perspectivesContainer = QStackedLayout()
        self.buttonContainer = QHBoxLayout()
        self.addLayout(self.perspectivesContainer, 1)
        self.addLayout(self.buttonContainer)
        self.setContentsMargins(0, 0, 0, 0)

    def attachPerspective(self, perspective):
        """ PerspectiveController(BasePerspective) -> None """

        self.attachedPerspectives.append(perspective)
        name = perspective.getName()
        icon = perspective.getIcon()
        widget = perspective.getWidget()
        button = QToolButton()
        button.setText(name)
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        if icon and isinstance(icon, QIcon):
            button.setIcon(icon)
        button.setCheckable(True)
        button.setProperty("perspectiveId", len(self.attachedPerspectives) - 1)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.buttons.append(button)
        self.buttonGroup.addButton(button)
        self.buttonContainer.addWidget(button)
        self.perspectivesContainer.addWidget(widget)
        if not self.buttonGroup.checkedButton():
            button.setChecked(True)

    def activateHandler(self, button):
        for btn in self.buttons:
            if btn is not button:
                pID = btn.property("perspectiveId")
                self.attachedPerspectives[pID].deactivated.emit()
        pID = button.property("perspectiveId")
        self.perspectivesContainer.setCurrentIndex(pID)
        self.attachedPerspectives[pID].activated.emit()

    def load(self):
        for i in self.attachedPerspectives:
            if isinstance(i, Loadable):
                i.load()

    def save(self):
        for i in self.attachedPerspectives:
            if isinstance(i, Savable):
                i.save()
