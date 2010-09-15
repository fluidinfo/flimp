import unittest
import uuid

from fom.session import Fluid
from fom.mapping import Namespace
from flimp.utils import make_namespace, make_tag, make_namespace_path

class TestUtils(unittest.TestCase):

    def setUp(self):
        # sort out FluidDB
        fdb = Fluid('https://sandbox.fluidinfo.com')
        fdb.bind()
        fdb.login('test', 'test')

    def test_make_namespace(self):
        # create a new namespace
        path = "test/%s" % str(uuid.uuid4())
        result = make_namespace(path, 'flimp-test', 'For the purposes of'
                                ' testing flimp')
        self.assertEqual(path, result.path)
        # try to create an existing namespace (just return the existing one)
        result = make_namespace(path, 'flimp-test', 'For the purposes of'
                                ' testing flimp')
        self.assertEqual(path, result.path)
        result.delete()

    def test_make_tag(self):
        # create a new tag
        parent_ns = Namespace('test')
        tag_name = str(uuid.uuid4())
        expected_path = 'test/%s' % tag_name
        result = make_tag(parent_ns, tag_name, 'flimp-test', 'For the'
                          ' purposes of testing flimp')
        self.assertEqual(expected_path, result.path)
        # try to create an existing tag (just return the existing one)
        result = make_tag(parent_ns, tag_name, 'flimp-test', 'For the'
                          ' purposes of testing flimp')
        self.assertEqual(expected_path, result.path)
        result.delete()

    def test_make_namespace_path(self):
        # create a new namespace path (returning the leaf namespace)
        unique_ns = str(uuid.uuid4())
        path = "test/%s/foo" % unique_ns
        result = make_namespace_path(path, 'flimp-test', 'For the purposes of'
                                ' testing flimp')
        self.assertEqual(path, result.path)
        # try to create an existing namespace path (just return the leaf)
        result = make_namespace(path, 'flimp-test', 'For the purposes of'
                                ' testing flimp')
        self.assertEqual(path, result.path)
        # be a good citizen an tidy up the mess
        result.delete()
        ns = Namespace("test/%s" % unique_ns)
        ns.delete()
