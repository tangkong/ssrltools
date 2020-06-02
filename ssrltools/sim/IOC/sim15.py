from caproto.server import (pvproperty, PVGroup, SubGroup, 
                            ioc_arg_parser, run)
from ssrltools.sim.IOC.motors import IMSMotorsSSRL
#from ssrltools.sim.IOC.xspress import SSRLXspress3DetectorGroup
class BL15(PVGroup):
    '''
    Class combining PV groups assembling beamline.  
    Each Subgroup here represents an IOC running at the beamline
    '''
    # PV: BL00:IMS:MOTOR{1,2,3,4}
    motors = SubGroup(IMSMotorsSSRL, prefix='BL00:IMS:')
    # PV: BL00:PICOD1:MOTOR{2,3}

    # PV: XSPRESS3-EXAMPLE:{Plugin}:Field
    #xsp3 = SubGroup(Xspress3SSRL, prefix='XSPRESS3-EXAMPLE:')


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