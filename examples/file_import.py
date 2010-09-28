import logging
from flimp.file_handler import process, clean_data
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
filename = 'data.json' # location of the file to import
root_path = 'test/foo'# Namespace where imported namespaces/tags are created
name = 'dataset_name' # used when creating namespace/tag descriptions 
desc = 'Plain English dataset description' # exactly what it says
about = 'id' # field whose value to use for the about tag
preview = False # True will cause flimp to print out the preview

# A basic example
process(filename, root_path, name, desc, about, preview)

# If you only want to get the data structure from the file try this.
data = clean_data(filename)

# The variable "data" now contains a list of dictionaries where each
# dictionary defines the tags to be added to an individual object.
