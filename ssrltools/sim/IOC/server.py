'''
Classes for use in simulated caproto beamline 
Classes here extend PV groups and add functionality



'''
import time
import random

from caproto import ChannelType
from caproto.server import pvproperty, PVGroup
from caproto.server.records import MotorFields, register_record

from ssrltools.sim.IOC.xspress import SSRLXspress3DetectorGroup

@register_record
class MotorFieldsSSRL(MotorFields):
    _record_type = 'SSRL_motor'

    # Need to duplicate motor field to extend or override
    user_readback_value = pvproperty(name='RBV', dtype=ChannelType.DOUBLE,
                                     doc='User Readback Value', read_only=True)

    # scanner updates RBV periodically based on setpoint value
    @user_readback_value.scan(period=1)
    async def user_readback_value(self, instance, async_lib):
        setpoint = self.parent.value    
        pos = setpoint + random.random() / 100.0

        # Set use, dial, raw readbacks
        timestamp = time.time()
        await instance.write(pos, timestamp=timestamp) # user_readback_value
        # self here is MotorFields, with attributes other than user_readback_value
        await self.dial_readback_value.write(pos, timestamp=timestamp)
        await self.raw_readback_value.write(int(pos * 100000.), 
                                            timestamp=timestamp) 
    
class Xspress3SSRL(SSRLXspress3DetectorGroup):
    '''
    Define behavior for Xspress3 simulated detector
    Features:---------------
    * Defining image dimensions on startup (normally requires a trigger)
    * Generation of MCA
    * Calculation of channel info from MCA with data from bin PV's
    * 
    '''
    pass
    # acquire = pvproperty(name='Acquire', dtype=int)

