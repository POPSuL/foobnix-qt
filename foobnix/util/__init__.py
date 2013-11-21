# -*- coding: utf-8 -*-

__author__ = 'popsul'

import os
from pprint import PrettyPrinter as pp
from foobnix.models import Media


class Singleton(type):

    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance

    def __init__(self, name, bases, dict):
        super(Singleton, self).__init__(name, bases, dict)
        self.instance = None


def createMediasForPaths(paths):
    if not isinstance(paths, list):
        paths = [paths]
    medias = []
    for path in paths:
        for (d, dirs, files) in os.walk(path):
            medias.append(Media(d, isMeta=True))
            for file in files:
                medias.append(Media(os.path.join(d, file)))
    pp(indent=4).pprint(medias)
    return medias
