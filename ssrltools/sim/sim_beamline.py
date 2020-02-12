from caproto.server import (pvproperty, PVGroup, SubGroup, 
                            ioc_arg_parser, run)
import numpy as np
import time
import functools
import math
import fabio

image_width, image_height = 2048, 2048

class CameraIOC(PVGroup):
    acquire = pvproperty(value=[0], 
                         doc='Process to acquire an image', 
                         mock_record='bo') # mock record does....?
    shape = pvproperty(value=[image_width, image_height],
                       doc='Image dimensions',
                       read_only=True)
    image = pvproperty(value=[0] * (image_width*image_height), 
                       doc='Image data',
                       read_only=True)

    # Putting anything into "acquire" PV fills image with the data from this
    # Image shape must already agree with loaded image
    @acquire.putter
    async def acquire(self, instance, value):
        imPath = "C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\fstore\\k3_012918_1_24x24_t45b_0248.tif"
        image = fabio.open(imPath)
        await self.image.write(image.data.flatten().astype(np.uint32))

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(default_prefix='simBL:',
                                            desc='cameraIOC')
    ioc = CameraIOC(**ioc_options)
    run(ioc.pvdb, **run_options)
    # run with python -m ssrltools.sim.sim_beamline --list-pvs