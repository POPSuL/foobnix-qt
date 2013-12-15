__author__ = 'popsul'

import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PreferencesWindow(QDialog):

    def __init__(self, context, parent=None):
        """
        @type context: GUIContext
        @type parent: QWidget
        """
        super().__init__(parent, Qt.Dialog)
        self.context = context
        self.setWindowTitle(self.tr("Preferences"))
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setMinimumHeight(480)
        self.setMinimumWidth(640)

        self.mainWidget = QTabWidget(self)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Save)
        self.layout.addWidget(self.mainWidget, 1)
        self.layout.addWidget(self.buttonBox, 0)

        self.buttonBox.accepted.connect(self.saveSettings)
        self.buttonBox.rejected.connect(self.close)
        self.providers = None

    def saveSettings(self):
        logging.debug("save settings")
        if self.providers:
            for provider in self.providers:
                provider.save()
        self.close()

    def open(self):
        self.mainWidget.clear()
        super().open()

        self.providers = self.context.getSettingProviders()
        for provider in self.providers:
            tab = provider.getTab()
            assert isinstance(tab, tuple), "tab must be tuple"
            assert len(tab) == 2, "invalid tab tuple"
            self.mainWidget.addTab(tab[0], tab[1])