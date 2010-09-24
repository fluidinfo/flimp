# -*- coding: utf-8 -*-
import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("flimp").addHandler(h)

VERSION = "0.6.1"

NAMESPACE_DESC = "%s namespace derived from %s.\n\n%s"
TAG_DESC = "%s tag derived from %s.\n\n%s"
