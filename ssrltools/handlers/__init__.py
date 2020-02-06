# imports to expose out to world
from .xspress3 import Xspress3HDF5Handler

def register(db):
    from .xspress3 import register
    register(db)