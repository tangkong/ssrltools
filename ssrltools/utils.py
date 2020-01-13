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