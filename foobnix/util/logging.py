__author__ = 'popsul'

import logging
from logging import INFO, WARNING, ERROR, CRITICAL, DEBUG


def setup(level, filename=None):
    if not level:
        level = ERROR

    logging.getLogger("foobnix-qt")
    logging.basicConfig(
        level=level,
        format="[%(levelname)-8s] [%(asctime)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%H:%M:%S",
        filename=filename,
        filemode="w"
    )


def printPlatformInfo():
    import platform
    logging.debug('*************** PLATFORM INFORMATION ************************')

    logging.debug('==Interpreter==')
    logging.debug('Version      :' + platform.python_version())
    logging.debug('Version tuple:' + str(platform.python_version_tuple()))
    logging.debug('Compiler     :' + platform.python_compiler())
    logging.debug('Build        :' + str(platform.python_build()))

    logging.debug('==Platform==')
    logging.debug('Normal   :' + platform.platform())
    logging.debug('Aliased  :' + platform.platform(aliased=True))
    logging.debug('Terse    :' + platform.platform(terse=True))

    logging.debug('==Operating System and Hardware Info==')
    logging.debug('uname    :' + str(platform.uname()))
    logging.debug('system   :' + platform.system())
    logging.debug('node     :' + platform.node())
    logging.debug('release  :' + platform.release())
    logging.debug('version  :' + platform.version())
    logging.debug('machine  :' + platform.machine())
    logging.debug('processor:' + platform.processor())

    logging.debug('==Executable Architecture==')
    logging.debug('interpreter:' + str(platform.architecture()))
    logging.debug('/bin/ls    :' + str(platform.architecture('/bin/ls')))
    logging.debug('*******************************************************')
