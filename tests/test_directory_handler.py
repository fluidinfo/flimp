import os
import unittest
import uuid
from flimp.directory_handler import (get_preview, get_object, make_namespace,
    push_to_fluiddb)
from fom.session import Fluid
from fom.mapping import Namespace, Tag, Object
from fom.errors import Fluid404Error

PATH_TO_LOCAL_DIRECTORY = os.path.join(os.getcwd(), os.path.dirname(__file__))
PATH_TO_TEST_DIRECTORY = os.path.join(PATH_TO_LOCAL_DIRECTORY, 'test')

class TestDirectoryHandler(unittest.TestCase):

    def setUp(self):
        # sort out FluidDB
        fdb = Fluid('https://sandbox.fluidinfo.com')
        fdb.bind()
        fdb.login('test', 'test')

    def test_get_preview(self):
        result = get_preview(PATH_TO_TEST_DIRECTORY, 'test',
                             'test/this/is/a/test')
        expected = [
            'test/this/is/a/test/bar/bar_child.txt CONTENT-TYPE: text/plain',
            'test/this/is/a/test/foo/foo_child.txt CONTENT-TYPE: text/plain',
            'test/this/is/a/test/readme.txt CONTENT-TYPE: text/plain',
        ]
        self.assertEqual(len(expected), len(result))
        for item in expected:
            self.assertTrue(item in result)

    def test_get_object(self):
        obj1 = get_object(about="foo")
        self.assertTrue(obj1.uid)
        self.assertEqual('foo', obj1.about)
        obj2 = get_object(uuid=obj1.uid)
        self.assertTrue(obj2.uid)
        self.assertEqual('foo', obj2.about)
        obj3 = get_object()
        self.assertTrue(obj3.uid)
        self.assertRaises(Fluid404Error, getattr, obj3, "about")

    def test_make_namespace(self):
        name = str(uuid.uuid4())
        path = 'test/%s' % name
        desc = 'this is a test'
        # make a new namespace
        new_ns = make_namespace(path, name, desc)
        self.assertEqual(path, new_ns.path)
        # try to make an existing namespace with no 412 error
        same_ns = make_namespace(path, name, desc)
        self.assertEqual(new_ns.path, same_ns.path)
        # tidy up
        new_ns.delete()

    def test_push_to_fluiddb(self):
        result = push_to_fluiddb(PATH_TO_TEST_DIRECTORY, 'test/this/is/a/test',
                                 'test', 'flimp-test', 'A test for flimp')
        expected = [
            'test/this/is/a/test/bar/bar_child.txt',
            'test/this/is/a/test/foo/foo_child.txt',
            'test/this/is/a/test/readme.txt',
        ]
        # check the resulting object has the right tags
        self.assertEqual(len(expected), len(result.tag_paths))
        for item in expected:
            self.assertTrue(item in result.tag_paths)
            # while we're looping lets make sure the tag-value is correct (it
            # worked)
            value = result.get(item)
            relative_path = item.replace('test/this/is/a/test/', '')
            expected_file = open(os.path.join(PATH_TO_TEST_DIRECTORY,
                              relative_path), 'r')
            expected_value = expected_file.read()
            expected_file.close()
            self.assertEqual(expected_value, value[0])
            self.assertEqual('text/plain', value[1])
