import os
import unittest
import uuid
from flimp.importer import (clean_data, create_schema, generate, create_class)
from fom.session import Fluid
from fom.mapping import Namespace

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

class TestImporter(unittest.TestCase):

    def setUp(self):
        # sort out FluidDB
        fdb = Fluid('https://sandbox.fluidinfo.com')
        fdb.bind()
        fdb.login('test', 'test')

    def test_get_argument(self):
        # TBD
        pass

    def test_clean_data(self):
        # good
        result = clean_data(GOOD_JSON)
        self.assertTrue(isinstance(result, list))
        # bad
        self.assertRaises(TypeError, clean_data, UNKNOWN_TYPE)

    def test_create_schema(self):
        tags = create_schema(TEMPLATE, 'test', 'flimp-test',
                             'flimp unit-test suite')
        self.assertEquals(4, len(tags))

    def test_generate(self):
        template = TEMPLATE[0]
        root_namespace = Namespace('test')
        name = str(uuid.uuid4())
        tags = {}
        generate(root_namespace, name, template, 'flimp unit-test suite',
                 'flimp-test', tags)
        self.assertEquals(4, len(tags))
        self.assertTrue('test_%s_foo' % name in tags)
        self.assertTrue('test_%s_baz_qux' % name in tags)
        self.assertTrue('test_%s_quux' % name in tags)
        self.assertTrue('test_%s_corge' % name in tags)

    def test_create_class(self):
        tags = create_schema(TEMPLATE, 'test', 'flimp-test',
                             'flimp unit-test suite')
        self.assertEquals(4, len(tags))
        fom_class = create_class(tags)
        attributes = dir(fom_class)
        for k in tags.keys():
            self.assertTrue(k in attributes)

    def test_push_to_fluiddb(self):
        pass
