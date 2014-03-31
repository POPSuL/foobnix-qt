# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.gui import InteractiveLabel
from foobnix.util import lookupResource
from foobnix.perspectives import BasePerspective


class BaseInfoSection(QtCore.QObject):

    activated = QtCore.pyqtSignal(name="activated")
    deactivated = QtCore.pyqtSignal(name="deactivated")

    def __init__(self):
        super(BaseInfoSection, self).__init__()

    def getName(self):
        pass

    def getWidget(self):
        pass


class TabulatedInfoSection(BaseInfoSection):

    def __init__(self):
        super(TabulatedInfoSection, self).__init__()

        self.widget = QTreeWidget()
        header = []
        for l in self.getHeader():
            header.append(l)
        self.widget.setHeaderLabels(header)

    def getHeader(self):
        return [self.getName()]

    def getWidget(self):
        return self.widget


class SimilarArtistsSection(TabulatedInfoSection):

    def __init__(self):
        super(SimilarArtistsSection, self).__init__()

    def getName(self):
        return self.tr("Similar artists")


class SimilarTracksSection(TabulatedInfoSection):

    def __init__(self):
        super(SimilarTracksSection, self).__init__()

    def getName(self):
        return self.tr("Similar tracks")


class SimilarLabelsSection(TabulatedInfoSection):

    def __init__(self):
        super(SimilarLabelsSection, self).__init__()

    def getName(self):
        return self.tr("Similar labels")


class BestTracksSection(TabulatedInfoSection):

    def __init__(self):
        super(BestTracksSection, self).__init__()
        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)

    def getName(self):
        return self.tr("Best tracks")

    def _activated(self):
        print("Best tracks section has been activated")

    def _deactivated(self):
        print("Best tracks section has been deactivated")


class LyricsSection(BaseInfoSection):

    def __init__(self):
        super().__init__()

        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)

        self.widget = None

    def getName(self):
        return self.tr("Lyrics")

    def getWidget(self):
        if not self.widget:
            self.widget = QTextEdit()
        return self.widget

    def _activated(self):
        print("Lyrics section has been activated")

    def _deactivated(self):
        print("Lyrics section has been deactivated")


additionalStyleSheet = """
QLabel[hovered="true"] {
    text-decoration: underline;
}
QLabel[hovered="false"] {
    text-decoration: none;
}
QLabel[active="true"] {
    font-weight:bold;
    text-decoration: none;
}
"""


class InfoPerspective(BasePerspective):

    def __init__(self, context):
        """
        @type context: GUIContext
        """
        super().__init__()

        self.context = context
        self.attachedSections = []
        self.labels = []

        ## build gui
        self.widget = QWidget()
        mainVbox = QVBoxLayout()
        self.widget.setLayout(mainVbox)
        headHbox = QHBoxLayout()
        mainVbox.addLayout(headHbox)
        self.sectionLabels = QVBoxLayout()
        self.sectionsContainer = QStackedLayout()
        mainVbox.addLayout(self.sectionsContainer, 1)
        self.sectionsContainer.addWidget(QLabel())  # dummy
        self.cover = QPixmap(lookupResource("images/cover.jpg"))
        self.coverWrapper = QLabel()
        self.coverWrapper.setFixedSize(128, 128)
        self.coverWrapper.setPixmap(self.cover.scaled(128, 128, QtCore.Qt.KeepAspectRatio))
        headHbox.addWidget(self.coverWrapper)
        headHbox.addLayout(self.sectionLabels, 1)

        mainVbox.setContentsMargins(0, 0, 0, 0)

        self.activated.connect(self._activated)
        self.deactivated.connect(self._deactivated)

        defaultSections = [SimilarArtistsSection, SimilarLabelsSection,
                           SimilarTracksSection, LyricsSection, BestTracksSection]
        for section in defaultSections:
            self.attachSection(section())

    def attachSection(self, section):
        assert isinstance(section, BaseInfoSection), "Illegal section"

        self.attachedSections.append(section)
        name, widget = section.getName(), section.getWidget()
        self.sectionsContainer.addWidget(widget)
        label = InteractiveLabel(name)
        label.setStyleSheet(additionalStyleSheet)
        label.setProperty("sectionId", len(self.attachedSections))
        label.setProperty("active", "false")
        self.labels.append(label)
        self.sectionLabels.addWidget(label)

        def activated():
            self.activateSection(label)
        label.clicked.connect(activated)

    def activateSection(self, label):
        self.sectionsContainer.setCurrentIndex(0)
        for l in self.labels:
            if l is not label:
                l.setProperty("active", "false")
                sectionId = l.property("sectionId")
                self.attachedSections[sectionId - 1].deactivated.emit()
                self.repolishStyle(l)

        if label.property("active") == "true":
            label.setProperty("active", "false")
        else:
            label.setProperty("active", "true")
            sectionId = label.property("sectionId")
            self.sectionsContainer.setCurrentIndex(sectionId)
            self.attachedSections[sectionId - 1].activated.emit()
        self.repolishStyle(label)

    def repolishStyle(self, label):
        label.style().unpolish(label)
        label.style().polish(label)

    def getName(self):
        return self.tr("Info")

    def getWidget(self):
        return self.widget

    def getIcon(self):
        return QIcon.fromTheme("dialog-information")

    def _activated(self):
        print("Info perspective activated")

    def _deactivated(self):
        print("Info perspective deactivated")
