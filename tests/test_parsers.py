import os
import unittest
from flimp.parser import parse_json

PATH_TO_FILES = os.path.join(os.getcwd(), os.path.dirname(__file__))

GOOD_JSON = os.path.join(PATH_TO_FILES, 'good.json')
BAD_JSON = os.path.join(PATH_TO_FILES, 'bad.json')
EMPTY_JSON = os.path.join(PATH_TO_FILES, 'empty.json')

class TestParseJson(unittest.TestCase):

    def test_parse(self):
        good = open(GOOD_JSON, 'r')
        bad = open(BAD_JSON, 'r')
        empty = open(EMPTY_JSON, 'r')

        self.assertTrue(isinstance(parse_json.parse(good), list))
        self.assertRaises(TypeError, parse_json.parse, bad)
        self.assertRaises(ValueError, parse_json.parse, empty)
