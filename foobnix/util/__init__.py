# -*- coding: utf-8 -*-

__author__ = 'popsul'

import os
import sys
from foobnix.models import Media

supportedFiles = [".mp3", ".m3u", ".pls", ".wav", ".flac", ".mp4", ".aac", ".m4a", ".cue"]
supportedFilesGlob = ["*" + k for k in supportedFiles]


class Singleton(type):

    def __call__(self, *args, **kw):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args, **kw)
        return self.instance

    def __init__(self, name, bases, dict):
        super(Singleton, self).__init__(name, bases, dict)
        self.instance = None


def getFileExtension(path):
    a, b = os.path.splitext(path)
    return b


def createMediasForPaths(paths):
    if not isinstance(paths, list):
        paths = [paths]
    medias = []
    for path in paths:
        if os.path.isdir(path):
            for (d, dirs, files) in os.walk(path):
                medias.append(Media(d, isMeta=True))
                for file in sorted(files):
                    p = os.path.join(d, file)
                    ext = getFileExtension(p)
                    if ext in supportedFiles:
                        medias.append(Media(p))
        elif os.path.isfile(path):
            medias.append(Media(path))
    return medias


def lookupResource(name):
    if not name:
        return None

    paths = ["/usr/local/share/pixmaps",
             "/usr/local/share/foobnix-qt",
             "/usr/share/pixmaps",
             "/usr/share/foobnix-qt",
             "share/pixmaps",
             "share/foobnix-qt",
             "share/pixmaps",
             "./",
             name]

    if len(sys.path) > 1:
        paths.append(sys.path[0])
        paths.append(os.path.join(sys.path[0], "share/pixmaps"))
        paths.append(os.path.join(sys.path[0], "share/foobnix-qt"))

    for path in paths:
        full_path = os.path.join(path, name)
        if os.path.exists(full_path):
            return full_path

    raise FileNotFoundError("File %s doesn't exists" % name)