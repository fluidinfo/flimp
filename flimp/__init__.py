# -*- coding: utf-8 -*-
import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("flimp").addHandler(h)

VERSION = "0.1.0"
