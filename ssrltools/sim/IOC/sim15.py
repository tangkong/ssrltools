from caproto.server import (pvproperty, PVGroup, SubGroup, 
                            ioc_arg_parser, run)
from ssrltools.sim.IOC.server import MotorFieldsSSRL, Xspress3SSRL

class IMSMotorsIOC(PVGroup):
    # Define records, try motor
    stagex = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR1')
    stagey = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR2')
    stagez = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR3')
    stageth = pvproperty(value=0.0, mock_record='SSRL_motor', name='MOTOR4')

    @stagex.startup
    async def stagex(self, instance, async_lib):
        # Could initialize PV values here.  
        await instance.write(9)
        await instance.fields['VELO'].write(1)
        print(f'on startup, write {instance.value} to stagex')
        print('velocity: {}'.format(self.stagex.fields['VELO'].value)) 
        ## ???? Why doesn't f-string work

class BL15(PVGroup):
    # PV: BL00:IMS:MOTOR{1,2,3,4}
    motors = SubGroup(IMSMotorsIOC, prefix='BL00:IMS:')
    # PV: BL00:PICOD1:MOTOR{2,3}

    # PV: XSPRESS3-EXAMPLE:{Plugin}:Field
    xsp3 = SubGroup(Xspress3SSRL, prefix='XSPRESS3-EXAMPLE:')


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
            default_prefix='',
            desc='Run IOC simulating BL1-5')

    # Instantiate IOC, assigning prefix for PV names
    print(ioc_options)

    ioc = BL15(**ioc_options)
    
    # Print all PV's
    print('PVs:', list(ioc.pvdb))

    # Print out all record fields
    # print('Fields of stagex:', list(ioc_ims.stagex.fields.keys()))
    # xspress3 organized as subgroups, no fields dictionary
    # print('Fields of xsp3:', list(ioc.xsp3.fields.keys()))


    # Run IOC.  Can only run once per startup....
    run(ioc.pvdb, **run_options)