import os
import unittest
import uuid
from flimp.file_handler import get_preview, clean_data
from fom.session import Fluid

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

    def test_clean_data(self):
        # good
        result = clean_data(GOOD_JSON)
        self.assertTrue(isinstance(result, list))
        # bad
        self.assertRaises(TypeError, clean_data, UNKNOWN_TYPE)

