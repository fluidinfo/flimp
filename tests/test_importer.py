import os
import unittest
import uuid
from flimp.importer import get_argument
from fom.session import Fluid
from fom.mapping import Namespace, Object

PATH_TO_FILES = os.path.join(os.getcwd(), os.path.dirname(__file__))

class TestImporter(unittest.TestCase):

    def setUp(self):
        # sort out FluidDB
        fdb = Fluid('https://sandbox.fluidinfo.com')
        fdb.bind()
        fdb.login('test', 'test')

    def test_get_argument(self):
        # TBD
        pass
