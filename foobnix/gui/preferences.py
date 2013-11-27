__author__ = 'popsul'

import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PreferencesWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Dialog)
        self.setWindowTitle(self.tr("Preferences"))
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.mainWidget = QTabWidget(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.layout.addWidget(self.mainWidget, 1)
        self.layout.addWidget(self.buttonBox, 0)

        self.buttonBox.accepted.connect(self.saveSettings)
        self.buttonBox.rejected.connect(self.close)

    def saveSettings(self):
        logging.debug("save settings")