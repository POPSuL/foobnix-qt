__author__ = 'popsul'

import logging
from .readers import getParserForMedia
from foobnix.models import Media

playlistTypes = ["pls", "m3u", "fpl"]


def isPlaylist(media):
    """
    @type media: Media
    """
    return media and media.path and media.path[-3:] in playlistTypes


def expandPlaylist(media):
    if not isPlaylist(media):
        logging.debug("is not playlist")
        return [media]
    parser = getParserForMedia(media)
    medias = []
    if parser:
        data = parser.read()
        if data:
            for item in data:
                medias.append(Media(path=item["path"], title=item["title"]))
            return medias
    else:
        logging.debug("parser doesn't exists")
    return [media]
