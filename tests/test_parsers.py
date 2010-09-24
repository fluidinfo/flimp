import os
import unittest
from flimp.parser import parse_json, parse_csv, parse_yaml

PATH_TO_FILES = os.path.join(os.getcwd(), os.path.dirname(__file__))

# JSON files
GOOD_JSON = os.path.join(PATH_TO_FILES, 'good.json')
BAD_JSON = os.path.join(PATH_TO_FILES, 'bad.json')
EMPTY_JSON = os.path.join(PATH_TO_FILES, 'empty.json')
# CSV files
GOOD_CSV = os.path.join(PATH_TO_FILES, 'good.csv')
BAD_CSV = os.path.join(PATH_TO_FILES, 'bad.csv')
HEADER_ONLY_CSV = os.path.join(PATH_TO_FILES, 'header_only.csv')
EMPTY_CSV = os.path.join(PATH_TO_FILES, 'empty.csv')
# YAML files
GOOD_YAML = os.path.join(PATH_TO_FILES, 'good.yaml')
BAD_YAML = os.path.join(PATH_TO_FILES, 'bad.yaml')
EMPTY_YAML = os.path.join(PATH_TO_FILES, 'empty.yaml')

class TestParseJson(unittest.TestCase):

    def test_parse(self):
        good = open(GOOD_JSON, 'r')
        bad = open(BAD_JSON, 'r')
        empty = open(EMPTY_JSON, 'r')

        self.assertTrue(isinstance(parse_json.parse(good), list))
        self.assertRaises(TypeError, parse_json.parse, bad)
        self.assertRaises(ValueError, parse_json.parse, empty)

class TestParseCsv(unittest.TestCase):

    def test_parse(self):
        good = open(GOOD_CSV, 'r')
        bad = open(BAD_CSV, 'r')
        header = open(HEADER_ONLY_CSV, 'r')
        empty = open(EMPTY_CSV, 'r')

        result = parse_csv.parse(good)
        self.assertTrue(isinstance(result, list))
        self.assertEqual(3, len(result))
        self.assertTrue(isinstance(result[0], dict))
        self.assertEqual(3, len(result[0].keys()))
        self.assertRaises(ValueError, parse_csv.parse, header)
        self.assertRaises(Exception, parse_csv.parse, empty)

        # Just confirm that zip is producing the appropriately sized
        # dictionaries
        result = parse_csv.parse(bad)
        for item in result[:-1]:
            self.assertEqual(3, len(item))
        self.assertEqual(2, len(result[3]))

    def test_clean_header(self):
        header = "  THIS IS A TEST   "
        self.assertEqual("this_is_a_test", parse_csv.clean_header(header))

class TestParseYaml(unittest.TestCase):

    def test_parse(self):
        good = open(GOOD_YAML, 'r')
        bad = open(BAD_YAML, 'r')
        empty = open(EMPTY_YAML, 'r')

        self.assertTrue(isinstance(parse_yaml.parse(good), list))
        self.assertRaises(TypeError, parse_yaml.parse, bad)
        self.assertRaises(ValueError, parse_yaml.parse, empty)
