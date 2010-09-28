import logging
from flimp.utils import process_data_list, validate
from flimp.parser import parse_csv
from fom.session import Fluid

# optionally create a logger - you don't need to do this but it's good to be
# able to see what's been going on since flimp logs pretty much everything
# it's doing.
logger = logging.getLogger("flimp")
logger.setLevel(logging.DEBUG)
logfile_handler = logging.FileHandler('flimp.log')
logfile_handler.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - "\
                               "%(message)s")
logfile_handler.setFormatter(log_format)
logger.addHandler(logfile_handler)

# Use fom to create a session with FluidDB - remember flimp uses fom for
# connecting to FluidDB
fdb = Fluid('https://sandbox.fluidinfo.com') # we'll use the sandbox
fdb.login('test', 'test') # replace these with something that works
fdb.bind()

# Values to pass into the "process" function
data_list = [
    {
        'foo': 'a',
        'bar': 'b',
        'baz': 'c'
    },
    {
        'foo': 'x',
        'bar': 'y',
        'baz': 'z'
    },
] # the Python list of dictionaries you want to process
root_path = 'test/foo'# Namespace where imported namespaces/tags are created
name = 'dataset_name' # used when creating namespace/tag descriptions 
desc = 'Plain English dataset description' # exactly what it says
about = 'foo' # field whose value to use for the about tag
preview = False # True will cause flimp to print out the preview

# Make magic happen...
process_data_list(data_list, root_path, name, desc, about)

# You can also validate the list to check for dictionaries that don't match
# the "template" taken from the first entry in the list.

# missing = missing fields, extras = extra fields not in the template - both
# are lists of instances of these problems.
missing, extras = validate(data_list)

# In the case of cleaning csv data you have several ways to normalise / clean
# the input
def clean_header(header):
    """
    A function that takes a column name header and normalises / cleans it into
    something we'll use as the name of a tag
    """
    # remove leading/trailing whitespace, replace inline whitespace with
    # underscore and any slashes with dashes.
    return header.strip().replace(' ', '_').replace('/', '-')

def clean_row_item(item):
    """
    A function that takes the string value of an individual item of data that
    will become a tag-value in FluidDB.

    The default version of this function in flimp will attempt to cast the
    value into something appropriate - see
    flimp.parser.csv_parser.clean_row_item for the source.
    """
    # We just want to make sure we return None for empty values. By default
    # flimp will ignore tags with None as a value (this can be overridden)
    value = item.strip()
    if value:
        return value
    else:
        return None

csv_file = open("data.csv", "r")
data = parse_csv.parse(csv_file, clean_header, clean_row_item)

"""
Given the following CSV file:

' Header 1 ':'Header 2':'Header 3/4'
A: B :C
X::Z

and the functions defined above then parse_csv.parse will produce something
like this:

[
    {
        'Header_3-4': 'C',
        'Header_2': 'B',
        'Header_1': 'A'
    },
    {
        'Header_3-4': 'Z',
        'Header_2': None,
        'Header_1': 'X'
    }
]
"""
