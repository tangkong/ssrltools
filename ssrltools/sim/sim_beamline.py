import numpy as np
import time
import functools
import math
import fabio

import asyncio
from caproto.server import (pvproperty, get_pv_pair_wrapper,
                            PVGroup, SubGroup, 
                            ioc_arg_parser, run)
import logging

logger = logging.getLogger('caproto')

image_width, image_height = 2048, 2048

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')

class DexelaDet15Group(PVGroup):
    # configuration_names = pvproperty(name=None, dtype=int)

    class DexelaDetectorCamGroup(PVGroup):
        # configuration_names = pvproperty(name=None, dtype=int)
        array_counter = pvproperty_with_rbv(name='ArrayCounter', dtype=int)
        array_rate = pvproperty(name='ArrayRate_RBV', dtype=float, read_only=True)
        asyn_io = pvproperty(name='AsynIO', dtype=int)
        nd_attributes_file = pvproperty(name='NDAttributesFile', dtype=str, max_length=256)
        pool_alloc_buffers = pvproperty(name='PoolAllocBuffers', dtype=int, read_only=True)
        pool_free_buffers = pvproperty(name='PoolFreeBuffers', dtype=int, read_only=True)
        pool_max_buffers = pvproperty(name='PoolMaxBuffers', dtype=int, read_only=True)
        pool_max_mem = pvproperty(name='PoolMaxMem', dtype=float, read_only=True)
        pool_used_buffers = pvproperty(name='PoolUsedBuffers', dtype=float, read_only=True)
        pool_used_mem = pvproperty(name='PoolUsedMem', dtype=float, read_only=True)
        port_name = pvproperty(name='PortName_RBV', dtype=str, read_only=True)
        acquire = pvproperty_with_rbv(name='Acquire', dtype=int)
        acquire_period = pvproperty_with_rbv(name='AcquirePeriod', dtype=float)
        acquire_time = pvproperty_with_rbv(name='AcquireTime', dtype=float)
        array_callbacks = pvproperty_with_rbv(name='ArrayCallbacks', dtype=int)

        class ArraySizeGroup(PVGroup):
            array_size_x = pvproperty(name='ArraySizeX_RBV', dtype=int, read_only=True)
            array_size_y = pvproperty(name='ArraySizeY_RBV', dtype=int, read_only=True)
            array_size_z = pvproperty(name='ArraySizeZ_RBV', dtype=int, read_only=True)

        array_size = SubGroup(ArraySizeGroup, prefix='')

        array_size_bytes = pvproperty(name='ArraySize_RBV', dtype=int, read_only=True)
        bin_x = pvproperty_with_rbv(name='BinX', dtype=int)
        bin_y = pvproperty_with_rbv(name='BinY', dtype=int)
        color_mode = pvproperty_with_rbv(name='ColorMode', dtype=int)
        data_type = pvproperty_with_rbv(name='DataType', dtype=int)
        detector_state = pvproperty(name='DetectorState_RBV', dtype=int, read_only=True)
        frame_type = pvproperty_with_rbv(name='FrameType', dtype=int)
        gain = pvproperty_with_rbv(name='Gain', dtype=float)
        image_mode = pvproperty_with_rbv(name='ImageMode', dtype=int)
        manufacturer = pvproperty(name='Manufacturer_RBV', dtype=str, read_only=True)

        # image_mode is a subgroup, need to access attribute
        @image_mode.setpoint.putter  
        async def image_mode(obj, instance, value):    
            await obj.readback.write(value)

        class MaxSizeGroup(PVGroup):
            max_size_x = pvproperty(name='MaxSizeX_RBV', dtype=int, read_only=True)
            max_size_y = pvproperty(name='MaxSizeY_RBV', dtype=int, read_only=True)

        max_size = SubGroup(MaxSizeGroup, prefix='')

        min_x = pvproperty_with_rbv(name='MinX', dtype=int)
        min_y = pvproperty_with_rbv(name='MinY', dtype=int)
        model = pvproperty(name='Model_RBV', dtype=str, read_only=True)
        num_exposures = pvproperty_with_rbv(name='NumExposures', dtype=int)
        num_exposures_counter = pvproperty(name='NumExposuresCounter_RBV', dtype=int, read_only=True)
        num_images = pvproperty_with_rbv(name='NumImages', dtype=int)
        num_images_counter = pvproperty(name='NumImagesCounter_RBV', dtype=int, read_only=True)
        read_status = pvproperty(name='ReadStatus', dtype=int)

        class ReverseGroup(PVGroup):
            reverse_x = pvproperty_with_rbv(name='ReverseX', dtype=int)
            reverse_y = pvproperty_with_rbv(name='ReverseY', dtype=int)

        reverse = SubGroup(ReverseGroup, prefix='')

        shutter_close_delay = pvproperty_with_rbv(name='ShutterCloseDelay', dtype=float)
        shutter_close_epics = pvproperty(name='ShutterCloseEPICS', dtype=float)
        shutter_control = pvproperty_with_rbv(name='ShutterControl', dtype=int)
        shutter_control_epics = pvproperty(name='ShutterControlEPICS', dtype=int)
        shutter_fanout = pvproperty(name='ShutterFanout', dtype=int)
        shutter_mode = pvproperty_with_rbv(name='ShutterMode', dtype=int)
        shutter_open_delay = pvproperty_with_rbv(name='ShutterOpenDelay', dtype=float)
        shutter_open_epics = pvproperty(name='ShutterOpenEPICS', dtype=float)
        shutter_status_epics = pvproperty(name='ShutterStatusEPICS_RBV', dtype=int, read_only=True)
        shutter_status = pvproperty(name='ShutterStatus_RBV', dtype=int, read_only=True)

        class SizeGroup(PVGroup):
            size_x = pvproperty_with_rbv(name='SizeX', dtype=int)
            size_y = pvproperty_with_rbv(name='SizeY', dtype=int)

        size = SubGroup(SizeGroup, prefix='')

        status_message = pvproperty(name='StatusMessage_RBV', dtype=str, 
                                    max_length=256, read_only=True)
        string_from_server = pvproperty(name='StringFromServer_RBV', dtype=str, 
                                        max_length=256, read_only=True)
        string_to_server = pvproperty(name='StringToServer_RBV', dtype=str, 
                                        max_length=256, read_only=True)
        temperature = pvproperty_with_rbv(name='Temperature', dtype=float)
        temperature_actual = pvproperty(name='TemperatureActual', dtype=float)
        time_remaining = pvproperty(name='TimeRemaining_RBV', dtype=float, read_only=True)
        trigger_mode = pvproperty_with_rbv(name='TriggerMode', dtype=int)

        acquire_gain = pvproperty(name='DEXAcquireGain', dtype=int)
        acquire_offset = pvproperty(name='DEXAcquireOffset', dtype=int)
        binning_mode = pvproperty_with_rbv(name='DEXBinningMode', dtype=int)
        corrections_dir = pvproperty(name='DEXCorrectionsDir', dtype=str)
        current_gain_frame = pvproperty(name='DEXCurrentGainFrame', dtype=int)
        current_offset_frame = pvproperty(name='DEXCurrentOffsetFrame', dtype=int)
        defect_map_available = pvproperty(name='DEXDefectMapAvailable', dtype=int)
        defect_map_file = pvproperty(name='DEXDefectMapFile', dtype=str)
        full_well_mode = pvproperty_with_rbv(name='DEXFullWellMode', dtype=int)
        gain_available = pvproperty(name='DEXGainAvailable', dtype=int)
        gain_file = pvproperty(name='DEXGainFile', dtype=str)
        load_defect_map_file = pvproperty(name='DEXLoadDefectMapFile', dtype=int)
        load_gain_file = pvproperty(name='DEXLoadGainFile', dtype=int)
        load_offset_file = pvproperty(name='DEXLoadOffsetFile', dtype=int)
        num_gain_frames = pvproperty(name='DEXNumGainFrames', dtype=int)
        num_offset_frames = pvproperty(name='DEXNumOffsetFrames', dtype=int)
        offset_available = pvproperty(name='DEXOffsetAvailable', dtype=int)
        offset_constant = pvproperty_with_rbv(name='DEXOffsetConstant', dtype=int)
        offset_file = pvproperty(name='DEXOffsetFile', dtype=str)
        save_gain_file = pvproperty(name='DEXSaveGainFile', dtype=int)
        save_offset_file = pvproperty(name='DEXSaveOffsetFile', dtype=int)
        serial_number = pvproperty(name='DEXSerialNumber', dtype=int)
        software_trigger = pvproperty(name='DEXSoftwareTrigger', dtype=int)
        use_defect_map = pvproperty(name='DEXUseDefectMap', dtype=int)
        use_gain = pvproperty(name='DEXUseGain', dtype=int)
        use_offset = pvproperty(name='DEXUseOffset', dtype=int)

    cam = SubGroup(DexelaDetectorCamGroup, prefix='cam1:')



    class DexelaTiffPluginGroup(PVGroup):
        # configuration_names = pvproperty(name=None, dtype=int)
        array_counter = pvproperty_with_rbv(name='ArrayCounter', dtype=int)
        array_rate = pvproperty(name='ArrayRate_RBV', dtype=int, read_only=True)
        asyn_io = pvproperty(name='AsynIO', dtype=int)
        nd_attributes_file = pvproperty(name='NDAttributesFile', dtype=str)
        pool_alloc_buffers = pvproperty(name='PoolAllocBuffers', dtype=int, read_only=True)
        pool_free_buffers = pvproperty(name='PoolFreeBuffers', dtype=int, read_only=True)
        pool_max_buffers = pvproperty(name='PoolMaxBuffers', dtype=int, read_only=True)
        pool_max_mem = pvproperty(name='PoolMaxMem', dtype=int, read_only=True)
        pool_used_buffers = pvproperty(name='PoolUsedBuffers', dtype=int, read_only=True)
        pool_used_mem = pvproperty(name='PoolUsedMem', dtype=int, read_only=True)
        port_name = pvproperty(name='PortName_RBV', dtype=str, read_only=True)
        # asyn_pipeline_config = pvproperty(name=None, dtype=int)
        # width = pvproperty(name='ArraySize0_RBV', dtype=int, read_only=True)
        # height = pvproperty(name='ArraySize1_RBV', dtype=int, read_only=True)
        # depth = pvproperty(name='ArraySize2_RBV', dtype=int, read_only=True)

        class ArraySizeGroup(PVGroup):
            height = pvproperty(name='ArraySize1_RBV', dtype=int, read_only=True)
            width = pvproperty(name='ArraySize0_RBV', dtype=int, read_only=True)
            depth = pvproperty(name='ArraySize2_RBV', dtype=int, read_only=True)

        array_size = SubGroup(ArraySizeGroup, prefix='')

        bayer_pattern = pvproperty(name='BayerPattern_RBV', dtype=int, read_only=True)
        blocking_callbacks = pvproperty_with_rbv(name='BlockingCallbacks', dtype=str)
        color_mode = pvproperty(name='ColorMode_RBV', dtype=int, read_only=True)
        data_type = pvproperty(name='DataType_RBV', dtype=str, read_only=True)
        # dim0_sa = pvproperty(name='Dim0SA', dtype=int)
        # dim1_sa = pvproperty(name='Dim1SA', dtype=int)
        # dim2_sa = pvproperty(name='Dim2SA', dtype=int)

        class DimSaGroup(PVGroup):
            dim0 = pvproperty(name='Dim0SA', dtype=int)
            dim1 = pvproperty(name='Dim1SA', dtype=int)
            dim2 = pvproperty(name='Dim2SA', dtype=int)

        dim_sa = SubGroup(DimSaGroup, prefix='')

        dimensions = pvproperty(name='Dimensions_RBV', dtype=int, 
                                max_length=10, read_only=True)
        dropped_arrays = pvproperty_with_rbv(name='DroppedArrays', dtype=int)
        enable = pvproperty_with_rbv(name='EnableCallbacks', dtype=str)
        min_callback_time = pvproperty_with_rbv(name='MinCallbackTime', dtype=float)
        nd_array_address = pvproperty_with_rbv(name='NDArrayAddress', dtype=int)
        nd_array_port = pvproperty_with_rbv(name='NDArrayPort', dtype=str)
        ndimensions = pvproperty(name='NDimensions_RBV', dtype=int, read_only=True)
        # plugin_type = pvproperty(name='PluginType_RBV', dtype=str, 
        #                             read_only=True, value='TIFFPlugin')
        queue_free = pvproperty(name='QueueFree', dtype=float)
        queue_free_low = pvproperty(name='QueueFreeLow', dtype=float)
        queue_size = pvproperty(name='QueueSize', dtype=int)
        queue_use = pvproperty(name='QueueUse', dtype=float)
        queue_use_high = pvproperty(name='QueueUseHIGH', dtype=float)
        queue_use_hihi = pvproperty(name='QueueUseHIHI', dtype=float)
        time_stamp = pvproperty(name='TimeStamp_RBV', dtype=float, read_only=True)
        unique_id = pvproperty(name='UniqueId_RBV', dtype=int, read_only=True)

        auto_increment = pvproperty_with_rbv(name='AutoIncrement', dtype=int)
        auto_save = pvproperty_with_rbv(name='AutoSave', dtype=int)
        capture = pvproperty_with_rbv(name='Capture', dtype=int)
        delete_driver_file = pvproperty_with_rbv(name='DeleteDriverFile', dtype=int)
        file_format = pvproperty_with_rbv(name='FileFormat', dtype=int)
        file_name = pvproperty_with_rbv(name='FileName', dtype=str)
        file_number = pvproperty_with_rbv(name='FileNumber', dtype=int)
        file_number_sync = pvproperty(name='FileNumber_Sync', dtype=int)
        file_number_write = pvproperty(name='FileNumber_write', dtype=int)
        file_path = pvproperty_with_rbv(name='FilePath', dtype=str)
        file_path_exists = pvproperty(name='FilePathExists_RBV', dtype=int, read_only=True)
        file_template = pvproperty_with_rbv(name='FileTemplate', dtype=str)
        file_write_mode = pvproperty_with_rbv(name='FileWriteMode', dtype=int)
        full_file_name = pvproperty(name='FullFileName_RBV', dtype=str, read_only=True)
        num_capture = pvproperty_with_rbv(name='NumCapture', dtype=int)
        num_captured = pvproperty(name='NumCaptured_RBV', dtype=int, read_only=True)
        read_file = pvproperty_with_rbv(name='ReadFile', dtype=int)
        write_file = pvproperty_with_rbv(name='WriteFile', dtype=int)
        write_message = pvproperty(name='WriteMessage', dtype=str)
        write_status = pvproperty(name='WriteStatus', dtype=int)

    tiff = SubGroup(DexelaTiffPluginGroup, prefix='TIFF1:')


class EpicsMotorGroup(PVGroup):
    # Read-only does not restrict write access within IOC (for implanting logic)
    user_readback = pvproperty(name='.RBV', dtype=int, read_only=True)
    user_setpoint = pvproperty(name='.VAL', dtype=int)
    user_offset = pvproperty(name='.OFF', dtype=int)
    user_offset_dir = pvproperty(name='.DIR', dtype=int)
    offset_freeze_switch = pvproperty(name='.FOFF', dtype=int)
    set_use_switch = pvproperty(name='.SET', dtype=int)
    velocity = pvproperty(name='.VELO', dtype=int, value=1)
    acceleration = pvproperty(name='.ACCL', dtype=int, value=1)
    motor_egu = pvproperty(name='.EGU', dtype=str, value='m/s')
    motor_is_moving = pvproperty(name='.MOVN', dtype=bool, read_only=True)
    motor_done_move = pvproperty(name='.DMOV', dtype=bool, read_only=True)
    high_limit_switch = pvproperty(name='.HLS', dtype=int)
    low_limit_switch = pvproperty(name='.LLS', dtype=int)
    direction_of_travel = pvproperty(name='.TDIR', dtype=int)
    motor_stop = pvproperty(name='.STOP', dtype=int)
    home_forward = pvproperty(name='.HOMF', dtype=int)
    home_reverse = pvproperty(name='.HOMR', dtype=int)

    @user_setpoint.putter
    async def user_setpoint(self, instance, val):
        await asyncio.sleep(2)
        # Write to readback value
        await self.user_readback.write(value=val, timestamp=time.time())


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

        # to print, use logger... ? This only logs with debug level. 
        logger.debug('acquiring image, filling pv')

        # .write() method returns a coroutine object to "await on" (to yield from)
        await self.image.write(image.data.flatten().astype(np.uint32))

class MainPVGroup(PVGroup):
    # Dexela subgroup
    dexela = SubGroup(DexelaDet15Group, prefix='dexela:')

    # CameraIOC subgroup
    camera = SubGroup(CameraIOC)

    # motor group
    stagex = SubGroup(EpicsMotorGroup, prefix='stagex')

if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(default_prefix='simBL:',
                                            desc='cameraIOC')
    ioc = MainPVGroup(**ioc_options)
    run(ioc.pvdb, **run_options)
    # run with python -m ssrltools.sim.sim_beamline --list-pvs