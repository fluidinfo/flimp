import logging
from flimp.utils import process_data_list, validate
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
