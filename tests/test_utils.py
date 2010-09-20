import unittest
import uuid

from fom.session import Fluid
from fom.mapping import Namespace, Object
from flimp.utils import (create_schema, generate,
                                 create_class, push_to_fluiddb, get_values,
                                 validate, make_namespace, make_tag,
                                make_namespace_path)

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

    def test_validate(self):
        # good
        data = [
            {
                'foo': 'a',
                'bar': {
                    'baz': 'b'
                },
                'bof': 'c'
            },
            {
                'foo': 'x',
                'bar': {
                    'baz': 'y'
                },
                'bof': 'z'
            },
        ]
        errors, warnings = validate(data)
        self.assertEqual([], errors) # no problem
        self.assertEqual([], warnings) # no problem
        # missing key
        data = [
            {
                'foo': 'a',
                'bar': {
                    'baz': 'b'
                },
                'bof': 'c'
            },
            {
                'foo': 'x',
                'bar': {
                    'baz': 'y'
                },
            },
        ]
        errors, warnings = validate(data)
        self.assertEqual([], warnings) # no problem
        self.assertEqual(1, len(errors))
        self.assertTrue("Missing field 'bof'" in errors[0])
        # additional key
        data = [
            {
                'foo': 'a',
                'bar': {
                    'baz': 'b'
                },
                'bof': 'c'
            },
            {
                'foo': 'x',
                'bar': {
                    'baz': 'y',
                },
                'bof': 'z',
                'qux': 'quux'
            },
        ]
        errors, warnings = validate(data)
        self.assertEqual([], errors) # no problem
        self.assertEqual(1, len(warnings))
        self.assertTrue("Extra field 'qux' in record" in warnings[0])
        # check validation includes sub-dictionaries
        data = [
            {
                'foo': 'a',
                'bar': {
                    'baz': 'b'
                },
                'bof': 'c'
            },
            {
                'foo': 'x',
                'bar': {
                    'quux': 'bif'
                },
                'bof': 'z'
            },
        ]
        errors, warnings = validate(data)
        self.assertEqual(1, len(warnings))
        self.assertTrue("Extra field 'quux' in record" in  warnings[0])
        self.assertEqual(1, len(errors))
        self.assertTrue("Missing field 'baz' in record" in errors[0])

    def test_create_schema(self):
        tags = create_schema(TEMPLATE, 'test/this/is/a/test', 'flimp-test',
                             'flimp unit-test suite')
        self.assertEqual(4, len(tags))

    def test_generate(self):
        template = TEMPLATE[0]
        root_namespace = Namespace('test')
        name = str(uuid.uuid4())
        tags = {}
        generate(root_namespace, name, template, 'flimp unit-test suite',
                 'flimp-test', tags)
        self.assertEqual(4, len(tags))
        self.assertTrue('test/%s/foo' % name in tags)
        self.assertTrue('test/%s/baz/qux' % name in tags)
        self.assertTrue('test/%s/quux' % name in tags)
        self.assertTrue('test/%s/corge' % name in tags)

    def test_create_class(self):
        tags = create_schema(TEMPLATE, 'test/this/is/a/test', 'flimp-test',
                             'flimp unit-test suite')
        self.assertEqual(4, len(tags))
        fom_class = create_class(tags)
        attributes = dir(fom_class)
        for k in tags:
            self.assertTrue(k in attributes)

    def test_push_to_fluiddb(self):
        # setting stuff up...
        name = str(uuid.uuid4())
        root_path = 'test/%s' % name
        tags = create_schema(TEMPLATE, root_path, 'flimp_test',
                             'flimp unit-test suite')
        self.assertEqual(4, len(tags))
        fom_class = create_class(tags)
        # the good case
        push_to_fluiddb(TEMPLATE, root_path, fom_class, 'foo',
                        'flimp_test')
        # check an object was created
        result = Object.filter("has %s/foo" % root_path)
        self.assertEqual(1, len(result))
        # lets try the other good case where we don't have an about tag field
        push_to_fluiddb(TEMPLATE, root_path, fom_class, None,
                        'flimp_test')
        # we should have *two* objects now
        result = Object.filter("has %s/foo" % root_path)
        self.assertEqual(2, len(result))
        # check we have all the expected tags on the objects
        for obj in result:
            tag_paths = obj.tag_paths
            for k in tags:
                tag_name = k.replace('_', '/')
                self.assertTrue(tag_name in tag_paths)

    def test_get_values(self):
        item = TEMPLATE[0]
        result = get_values(item, 'test/flimp/test')
        self.assertEqual(4, len(result))
        # do we have the expected attribute names..?
        self.assertTrue('test/flimp/test/foo' in result)
        self.assertTrue('test/flimp/test/baz/qux' in result)
        self.assertTrue('test/flimp/test/quux' in result)
        self.assertTrue('test/flimp/test/corge' in result)
        # and are the associated values correct..?
        self.assertEqual(item['foo'], result['test/flimp/test/foo'])
        self.assertEqual(item['baz']['qux'],
                         result['test/flimp/test/baz/qux'])
        self.assertEqual(item['quux'], result['test/flimp/test/quux'])
        self.assertEqual(item['corge'], result['test/flimp/test/corge'])

