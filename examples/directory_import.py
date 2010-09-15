import logging
from flimp.directory_handler import process
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
root_dir = 'test_dir' # the path to the directory you want to import
root_path = 'test/foo' # the namespace in FluidDB that maps to root_dir
name = 'dataset_name' # the name of the filesystem data to be imported
desc = 'Plain English dataset description' # exactly what it says
uuid = None # the uuid of the object to tag
about = None # the about value of the object to tag
preview = False # True will cause flimp to print out the preview

# Make magic happen...
obj = process(root_dir, root_path, name, desc, uuid, about, preview)
# obj is a fom.mapping.Object instance representing the FluidDB object that
# has just been tagged
print obj.uid
