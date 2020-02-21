"""
Utilities for use at SSRL beamlines running Bluesky

..autosummary::
"""
import zict
import msgpack_numpy
import msgpack

class PersistentDict(zict.Func):
    def __init__(self, directory):
        self._directory = directory
        self._file = zict.File(directory)
        super().__init__(self._dump, self._load, self._file)

    @property
    def directory(self):
        return self._directory

    def __repr__(self):
        return f"<{self.__class__.__name__} {dict(self)!r}>"

    @staticmethod
    def _dump(obj):
        "Encode as msgpack using numpy-aware encoder."
        # See https://github.com/msgpack/msgpack-python#string-and-binary-type
        # for more on use_bin_type.
        return msgpack.packb(
            obj,
            default=msgpack_numpy.encode,
            use_bin_type=True)

    def _load(self, file):
        return msgpack.unpackb(
            file,
            object_hook=msgpack_numpy.decode,
            raw=False)

            
from caproto.server.conversion import ophyd_device_to_caproto_ioc as o2c
basep = 'C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\fstore\\'

def ophyd_to_caproto_to_file(device, savepath=basep):
    ioc = o2c(device)

    for key in ioc.keys():
        with open(savepath + str(key) + '.py', 'w+') as fp:
            for ln in ioc[key]:
                fp.write(ln)
                fp.write('\n')