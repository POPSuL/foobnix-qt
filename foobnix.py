#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'popsul'

import sys
import argparse
from foobnix.core import Core
from foobnix.util import logging


def parseArgs():
    parser = argparse.ArgumentParser(prog="foobnix.py")
    parser.add_argument("--debug", help="Turn on debug mode", dest="debug", action="store_true")
    parser.add_argument("--log", help="Path to log", type=str, default="-")
    return parser.parse_args()

if __name__ == "__main__":
    args = parseArgs()
    if args.debug:
        if args.log != "-":
            logging.setup(logging.DEBUG, args.log)
        else:
            logging.setup(logging.DEBUG)
        logging.printPlatformInfo()
    else:
        logging.setup(logging.WARNING)
    Core().run()