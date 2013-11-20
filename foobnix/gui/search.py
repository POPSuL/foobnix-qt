# -*- coding: utf-8 -*-

__author__ = 'popsul'

from PyQt4 import QtCore
from PyQt4.QtGui import *
from foobnix.search import AbstractSearchSource

class SearchBar(QHBoxLayout):

    def __init__(self):
        super(SearchBar, self).__init__()

        ## base
        self.searchSources = []
        self.searchSourceSelector = QComboBox()
        self.searchTextBar = QLineEdit("")
        self.searchTextBar.setPlaceholderText("Enter your search query")
        self.searchButton = QPushButton("Search")

        ## build gui
        self.setSpacing(0)
        self.addWidget(self.searchSourceSelector)
        self.addWidget(self.searchTextBar, 1)
        self.addWidget(self.searchButton)

        ## example
        self.addSearchSource(AbstractSearchSource("Source1"))
        self.addSearchSource(AbstractSearchSource("Source2"))
        self.addSearchSource(AbstractSearchSource("Source3"))

    def addSearchSource(self, source):
        """ SearchBar.addSearchSource(AbstractSearchSource) -> None """
        self.searchSources.append(source)
        self.searchSourceSelector.addItem(source.title)