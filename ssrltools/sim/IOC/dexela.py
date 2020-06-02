'''
     # Functionality items
    # TODO: Initialize image array
    #   Write to ArrayData PV
    # TODO: Acquire triggering image refresh -> Update ROIs and other info
    # TODO: Deal with filestore plugin, rudimentary operation 
    #   Write array data as TIFF with every trigger
'''

from caproto.server import (pvproperty, PVGroup, ioc_arg_parser,
                             run, get_pv_pair_wrapper, SubGroup)

import numpy as np
from scipy import signal

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class DexelaDet15noTiffGroup(PVGroup):
    # configuration_names = pvproperty(name=None, dtype=float)

    class DexelaDetectorCamGroup(PVGroup):
        # configuration_names = pvproperty(name=None, dtype=float)
        array_counter = pvproperty_with_rbv(name='ArrayCounter', dtype=float)
        array_rate = pvproperty(name='ArrayRate_RBV', dtype=float, read_only=True)
        asyn_io = pvproperty(name='AsynIO', dtype=float)
        nd_attributes_file = pvproperty(name='NDAttributesFile', dtype=str)
        pool_alloc_buffers = pvproperty(name='PoolAllocBuffers', dtype=float, read_only=True)
        pool_free_buffers = pvproperty(name='PoolFreeBuffers', dtype=float, read_only=True)
        pool_max_buffers = pvproperty(name='PoolMaxBuffers', dtype=float, read_only=True)
        pool_max_mem = pvproperty(name='PoolMaxMem', dtype=float, read_only=True)
        pool_used_buffers = pvproperty(name='PoolUsedBuffers', dtype=float, read_only=True)
        pool_used_mem = pvproperty(name='PoolUsedMem', dtype=float, read_only=True)
        port_name = pvproperty(name='PortName_RBV', dtype=str, read_only=True)
        acquire = pvproperty_with_rbv(name='Acquire', dtype=float)
        acquire_period = pvproperty_with_rbv(name='AcquirePeriod', dtype=float)
        acquire_time = pvproperty_with_rbv(name='AcquireTime', dtype=float)
        array_callbacks = pvproperty_with_rbv(name='ArrayCallbacks', dtype=float)

        class ArraySizeGroup(PVGroup):
            array_size_x = pvproperty(name='ArraySizeX_RBV', dtype=float, read_only=True)
            array_size_y = pvproperty(name='ArraySizeY_RBV', dtype=float, read_only=True)
            array_size_z = pvproperty(name='ArraySizeZ_RBV', dtype=float, read_only=True)

        array_size = SubGroup(ArraySizeGroup, prefix='')

        array_size_bytes = pvproperty(name='ArraySize_RBV', dtype=float, read_only=True)
        bin_x = pvproperty_with_rbv(name='BinX', dtype=float)
        bin_y = pvproperty_with_rbv(name='BinY', dtype=float)
        color_mode = pvproperty_with_rbv(name='ColorMode', dtype=float)
        data_type = pvproperty_with_rbv(name='DataType', dtype=float)
        detector_state = pvproperty(name='DetectorState_RBV', dtype=float, read_only=True)
        frame_type = pvproperty_with_rbv(name='FrameType', dtype=float)
        gain = pvproperty_with_rbv(name='Gain', dtype=float)
        image_mode = pvproperty_with_rbv(name='ImageMode', dtype=float)
        manufacturer = pvproperty(name='Manufacturer_RBV', dtype=float, read_only=True)

        class MaxSizeGroup(PVGroup):
            max_size_x = pvproperty(name='MaxSizeX_RBV', dtype=float, read_only=True)
            max_size_y = pvproperty(name='MaxSizeY_RBV', dtype=float, read_only=True)

        max_size = SubGroup(MaxSizeGroup, prefix='')

        min_x = pvproperty_with_rbv(name='MinX', dtype=float)
        min_y = pvproperty_with_rbv(name='MinY', dtype=float)
        model = pvproperty(name='Model_RBV', dtype=float, read_only=True)
        num_exposures = pvproperty_with_rbv(name='NumExposures', dtype=float)
        num_exposures_counter = pvproperty(name='NumExposuresCounter_RBV', dtype=float, read_only=True)
        num_images = pvproperty_with_rbv(name='NumImages', dtype=float)
        num_images_counter = pvproperty(name='NumImagesCounter_RBV', dtype=float, read_only=True)
        read_status = pvproperty(name='ReadStatus', dtype=float)

        class ReverseGroup(PVGroup):
            reverse_x = pvproperty_with_rbv(name='ReverseX', dtype=float)
            reverse_y = pvproperty_with_rbv(name='ReverseY', dtype=float)

        reverse = SubGroup(ReverseGroup, prefix='')

        shutter_close_delay = pvproperty_with_rbv(name='ShutterCloseDelay', dtype=float)
        shutter_close_epics = pvproperty(name='ShutterCloseEPICS', dtype=float)
        shutter_control = pvproperty_with_rbv(name='ShutterControl', dtype=float)
        shutter_control_epics = pvproperty(name='ShutterControlEPICS', dtype=float)
        shutter_fanout = pvproperty(name='ShutterFanout', dtype=float)
        shutter_mode = pvproperty_with_rbv(name='ShutterMode', dtype=float)
        shutter_open_delay = pvproperty_with_rbv(name='ShutterOpenDelay', dtype=float)
        shutter_open_epics = pvproperty(name='ShutterOpenEPICS', dtype=float)
        shutter_status_epics = pvproperty(name='ShutterStatusEPICS_RBV', dtype=float, read_only=True)
        shutter_status = pvproperty(name='ShutterStatus_RBV', dtype=float, read_only=True)

        class SizeGroup(PVGroup):
            size_x = pvproperty_with_rbv(name='SizeX', dtype=float)
            size_y = pvproperty_with_rbv(name='SizeY', dtype=float)

        size = SubGroup(SizeGroup, prefix='')

        status_message = pvproperty(name='StatusMessage_RBV', dtype=str, read_only=True)
        string_from_server = pvproperty(name='StringFromServer_RBV', dtype=str, read_only=True)
        string_to_server = pvproperty(name='StringToServer_RBV', dtype=str, read_only=True)
        temperature = pvproperty_with_rbv(name='Temperature', dtype=float)
        temperature_actual = pvproperty(name='TemperatureActual', dtype=float)
        time_remaining = pvproperty(name='TimeRemaining_RBV', dtype=float, read_only=True)
        trigger_mode = pvproperty_with_rbv(name='TriggerMode', dtype=float)
        acquire_gain = pvproperty(name='DEXAcquireGain', dtype=float)
        acquire_offset = pvproperty(name='DEXAcquireOffset', dtype=float)
        binning_mode = pvproperty_with_rbv(name='DEXBinningMode', dtype=float)
        corrections_dir = pvproperty(name='DEXCorrectionsDir', dtype=str)
        current_gain_frame = pvproperty(name='DEXCurrentGainFrame', dtype=float)
        current_offset_frame = pvproperty(name='DEXCurrentOffsetFrame', dtype=float)
        defect_map_available = pvproperty(name='DEXDefectMapAvailable', dtype=float)
        defect_map_file = pvproperty(name='DEXDefectMapFile', dtype=str)
        full_well_mode = pvproperty_with_rbv(name='DEXFullWellMode', dtype=float)
        gain_available = pvproperty(name='DEXGainAvailable', dtype=float)
        gain_file = pvproperty(name='DEXGainFile', dtype=str)
        load_defect_map_file = pvproperty(name='DEXLoadDefectMapFile', dtype=float)
        load_gain_file = pvproperty(name='DEXLoadGainFile', dtype=float)
        load_offset_file = pvproperty(name='DEXLoadOffsetFile', dtype=float)
        num_gain_frames = pvproperty(name='DEXNumGainFrames', dtype=float)
        num_offset_frames = pvproperty(name='DEXNumOffsetFrames', dtype=float)
        offset_available = pvproperty(name='DEXOffsetAvailable', dtype=float)
        offset_constant = pvproperty_with_rbv(name='DEXOffsetConstant', dtype=float)
        offset_file = pvproperty(name='DEXOffsetFile', dtype=str)
        save_gain_file = pvproperty(name='DEXSaveGainFile', dtype=float)
        save_offset_file = pvproperty(name='DEXSaveOffsetFile', dtype=float)
        serial_number = pvproperty(name='DEXSerialNumber', dtype=float)
        software_trigger = pvproperty(name='DEXSoftwareTrigger', dtype=float)
        use_defect_map = pvproperty(name='DEXUseDefectMap', dtype=float)
        use_gain = pvproperty(name='DEXUseGain', dtype=float)
        use_offset = pvproperty(name='DEXUseOffset', dtype=float)

    cam = SubGroup(DexelaDetectorCamGroup, prefix='')

    image = pvproperty(name='ArrayData', dtype=float)

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
            default_prefix='SSRL:DEX2923:',
            desc='Run IOC simulating Xspress3')

    # Instantiate IOC, assigning prefix for PV names
    ioc = DexelaDet15noTiffGroup(**ioc_options)
    print('PVs:', list(ioc.pvdb))

    # Run IOC
    run(ioc.pvdb, **run_options)