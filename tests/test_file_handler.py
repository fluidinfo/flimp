import os
import unittest
import uuid
from flimp.file_handler import (get_preview, clean_data, traverse_preview,
                                process)
from fom.session import Fluid
from fom.mapping import Object

PATH_TO_FILES = os.path.join(os.getcwd(), os.path.dirname(__file__))

GOOD_JSON = os.path.join(PATH_TO_FILES, 'good.json')
UNKNOWN_TYPE = os.path.join(PATH_TO_FILES, 'unknown.txt')

# good data structure
TEMPLATE = [
    {
        'foo': 'bar',
        'baz': {
            'qux': '1'
        },
        'quux': ['ham', 'eggs'],
        'corge': [
            {
                'a': 1,
                'b': 2
            }
        ]
    }
]

class TestFileHandler(unittest.TestCase):

    def setUp(self):
        # sort out FluidDB
        fdb = Fluid('https://sandbox.fluidinfo.com')
        fdb.bind()
        fdb.login('test', 'test')

    def test_process(self):
        filename = GOOD_JSON
        name = str(uuid.uuid4())
        root_path = 'test/%s' % name
        desc = 'flimp unit-test suite'
        about = None
        output = process(filename, root_path, name, desc, about)
        self.assertEqual("Processed 2 records", output)
        # check we have two objects each with three tags attached
        result = Object.filter('has %s/foo' % root_path)
        self.assertEqual(2, len(result))
        for obj in result:
            self.assertEqual(1, len(obj.tag_paths))
        # make sure the function returns expected text
        # preview
        preview = process(filename, root_path, name, desc, about, preview=True)
        expected = """Preview of processing %r

The following namespaces/tags will be generated.

test/%s/foo

2 records will be imported into FluidDB
""" % (filename, name)
        self.assertEqual(expected, preview)
        # check
        check = process(filename, root_path, name, desc, about, check=True)
        self.assertEqual("Validation passed ok", check)

    def test_get_preview(self):
        result = get_preview(TEMPLATE, 'test/flimp-test')
        expected = ['test/flimp-test/foo',
                    'test/flimp-test/baz/qux',
                    'test/flimp-test/quux',
                    'test/flimp-test/corge',
                   ]
        self.assertEqual(len(expected), len(result))
        for item in expected:
            self.assertTrue(item in result)

    def test_traverse_preview(self):
        result = list()
        traverse_preview(TEMPLATE[0], 'test/flimp-test', result)
        expected = ['test/flimp-test/foo',
                    'test/flimp-test/baz/qux',
                    'test/flimp-test/quux',
                    'test/flimp-test/corge',
                   ]
        self.assertEqual(len(expected), len(result))
        for item in expected:
            self.assertTrue(item in result)

    def test_clean_data(self):
        # good
        result = clean_data(GOOD_JSON)
        self.assertTrue(isinstance(result, list))
        # bad
        self.assertRaises(TypeError, clean_data, UNKNOWN_TYPE)
