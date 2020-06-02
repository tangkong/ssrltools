'''
Classes for use in simulated caproto beamline 
Classes here extend PV groups and add functionality


'''
import time
import random

from caproto import ChannelType
from caproto.server import pvproperty, PVGroup, get_pv_pair_wrapper
from caproto.server.records import MotorFields, register_record

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')

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

class IMSMotorsSSRL(PVGroup):
    '''
    Group for IMS motor IOC
    '''
    # Define records, try custom motor record
    stagex = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR1')
    stagey = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR2')
    stagez = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR3')
    stageth = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR4')

    # Functionality items
    # TODO: Initialize values for (limits, position, velo, accl)
    # TODO: Update of RBV with setpoint update
    # TODO: 

    @stagex.startup
    async def stagex(self, instance, async_lib):
        # Could initialize PV values here.  
        await instance.write(9)
        await instance.fields['VELO'].write(1)
        print(f'on startup, write {instance.value} to stagex')
        print('velocity: {}'.format(self.stagex.fields['VELO'].value)) 
        ## ???? Why doesn't f-string work
