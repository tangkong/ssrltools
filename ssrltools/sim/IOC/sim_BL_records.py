from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run

class SimBL15IOC(PVGroup):
    # Define records, try motor
    stagex = pvproperty(value=0.0, mock_record='motor')

    @stagex.putter
    async def stagex(self, instance, value):
        print(f'Writing to stagex: {value}')

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
            default_prefix='simBL:',
            desc='Run IOC simulating BL1-5')

    # Instantiate IOC, assigning prefix for PV names
    ioc = SimBL15IOC(**ioc_options)
    print('PVs:', list(ioc.pvdb))

    # Print out all record fields
    print('Fields of stagex:', list(ioc.stagex.fields.keys()))

    # Run IOC
    run(ioc.pvdb, **run_options)