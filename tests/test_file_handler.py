import os
import unittest
import uuid
from flimp.file_handler import (clean_data, create_schema, generate,
                                 create_class, push_to_fluiddb, get_values,
                                 build_attribute_name, get_preview)
from fom.session import Fluid
from fom.mapping import Namespace, Object

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
        result = get_preview(TEMPLATE, 'test', 'test/flimp-test')
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

    def test_create_schema(self):
        tags = create_schema(TEMPLATE, 'test/this/is/a/test', 'test',
                             'flimp-test', 'flimp unit-test suite')
        self.assertEqual(4, len(tags))

    def test_generate(self):
        template = TEMPLATE[0]
        root_namespace = Namespace('test')
        name = str(uuid.uuid4())
        tags = {}
        generate(root_namespace, name, template, 'flimp unit-test suite',
                 'flimp-test', tags)
        self.assertEqual(4, len(tags))
        self.assertTrue('test_%s_foo' % name in tags)
        self.assertTrue('test_%s_baz_qux' % name in tags)
        self.assertTrue('test_%s_quux' % name in tags)
        self.assertTrue('test_%s_corge' % name in tags)

    def test_create_class(self):
        tags = create_schema(TEMPLATE, 'test/this/is/a/test', 'test',
                             'flimp-test', 'flimp unit-test suite')
        self.assertEqual(4, len(tags))
        fom_class = create_class(tags)
        attributes = dir(fom_class)
        for k in tags.keys():
            self.assertTrue(k in attributes)

    def test_push_to_fluiddb(self):
        # setting stuff up...
        name = str(uuid.uuid4())
        root_path = 'test/%s' % name
        tags = create_schema(TEMPLATE, root_path, 'test', 'flimp_test',
                             'flimp unit-test suite')
        self.assertEqual(4, len(tags))
        fom_class = create_class(tags)
        # the good case
        push_to_fluiddb(TEMPLATE, root_path, fom_class, 'foo',
                        'flimp_test', 'test')
        # check an object was created
        result = Object.filter("has %s/foo" % root_path)
        self.assertEqual(1, len(result))
        # lets try the other good case where we don't have an about tag field
        push_to_fluiddb(TEMPLATE, root_path, fom_class, None,
                        'flimp_test', 'test')
        # we should have *two* objects now
        result = Object.filter("has %s/foo" % root_path)
        self.assertEqual(2, len(result))
        # check we have all the expected tags on the objects
        for obj in result:
            tag_paths = obj.tag_paths
            for k in tags.keys():
                tag_name = k.replace('_', '/')
                self.assertTrue(tag_name in tag_paths)

    def test_get_values(self):
        item = TEMPLATE[0]
        result = get_values(item, 'test_flimp_test')
        self.assertEqual(4, len(result))
        # do we have the expected attribute names..?
        self.assertTrue('test_flimp_test_foo' in result)
        self.assertTrue('test_flimp_test_baz_qux' in result)
        self.assertTrue('test_flimp_test_quux' in result)
        self.assertTrue('test_flimp_test_corge' in result)
        # and are the associated values correct..?
        self.assertEqual(item['foo'], result['test_flimp_test_foo'])
        self.assertEqual(item['baz']['qux'],
                         result['test_flimp_test_baz_qux'])
        self.assertEqual(item['quux'], result['test_flimp_test_quux'])
        self.assertEqual(item['corge'], result['test_flimp_test_corge'])

    def test_build_attribute_name(self):
        items = ['foo_bar', 'baz']
        self.assertEqual('foo_bar_baz', build_attribute_name(items))
