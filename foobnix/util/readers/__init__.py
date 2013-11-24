__author__ = 'popsul'

from .pls import PLSReader


def getParserForMedia(media):
    """
    @type media: Media
    """
    ext = media.path[-3:]
    if ext == "pls":
        return PLSReader(media.path)
    return None