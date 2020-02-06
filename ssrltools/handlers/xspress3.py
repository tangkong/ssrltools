import logging

# imort XRF_DATA_KEY for back-compat
from databroker.assets.handlers import (Xspress3HDF5Handler,
                                        XS3_XRF_DATA_KEY as XRF_DATA_KEY)


logger = logging.getLogger(__name__)

FMT_ROI_KEY = 'entry/instrument/detector/NDAttributes/CHAN{}ROI{}'


def register(db):
    db.reg.register_handler(Xspress3HDF5Handler.HANDLER_NAME,
                            Xspress3HDF5Handler)