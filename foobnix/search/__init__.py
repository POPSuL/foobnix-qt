# -*- coding: utf-8 -*-

__author__ = 'popsul'


class AbstractSearchSource():

    def __init__(self, title):
        self.title = title

    def onSearch(self, searchString):
        print("onSearch", self, searchString)
