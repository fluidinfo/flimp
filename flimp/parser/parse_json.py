"""
Turns a filename into a list of deserialized items based upon json data
"""

import sys

if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

def parse(raw_file):
    """
    Given a filename, will load it and attempt to de-serialize the json
    therein.

    Also makes sure we have a non-empty list as a result.
    """
    data = json.loads(raw_file.read())
    if not isinstance(data, list):
        raise TypeError('The json file *MUST* supply a list of items to be '
                        'turned into objects in FluidDB')

    # Final check that we actually got some data.
    if data:
        return data
    else:
        raise ValueError('JSON list was empty.')
