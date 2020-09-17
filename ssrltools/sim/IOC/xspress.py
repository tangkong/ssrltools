'''
Xspress3 caproto group setup
    # Functionality items.  
    # TODO: Initialize array MCA 
    #   What does MCA look like?
    # TODO: Acquire triggering image refresh -> Update ROIs and other info
    # TODO: Deal with filestore plugin, rudimentary operation 
    #   Write file with MCA with every trigger
'''

from caproto.server import (pvproperty, PVGroup, ioc_arg_parser,
                             run, get_pv_pair_wrapper, SubGroup)

import numpy as np
from scipy import signal

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')

def generate_sim_MCA(num_peaks, length):
    '''
    Output sample MCA with some noise
    '''
    out = np.zeros(length)
    def gauss(mean, std, length):
        ''' Quick gaussian distribution function '''
        x = np.arange(length)
        return 1/(std * np.sqrt(2*np.pi)) * np.exp(-(x - mean)**2/(2*std**2))

    for _ in range(num_peaks): # Add 3 gaussian peaks
        std = np.random.randint(40, 60)
        mean = np.random.randint(60, 4000)
        out += gauss(mean, std, 4096)

    return out

class SSRLXspress3DetectorGroup(PVGroup):
    # configuration_names = pvproperty(name=None, dtype=int)

    class Xspress3DetectorSettingsGroup(PVGroup):
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
        acquire = pvproperty_with_rbv(name='Acquire', dtype=int)    
        acquire_period = pvproperty_with_rbv(name='AcquirePeriod', dtype=int)
        acquire_time = pvproperty_with_rbv(name='AcquireTime', dtype=int)
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
        gain = pvproperty_with_rbv(name='Gain', dtype=int)
        image_mode = pvproperty_with_rbv(name='ImageMode', dtype=int)
        manufacturer = pvproperty(name='Manufacturer_RBV', dtype=int, read_only=True)

        class MaxSizeGroup(PVGroup):
            max_size_x = pvproperty(name='MaxSizeX_RBV', dtype=int, read_only=True)
            max_size_y = pvproperty(name='MaxSizeY_RBV', dtype=int, read_only=True)

        max_size = SubGroup(MaxSizeGroup, prefix='')

        min_x = pvproperty_with_rbv(name='MinX', dtype=int)
        min_y = pvproperty_with_rbv(name='MinY', dtype=int)
        model = pvproperty(name='Model_RBV', dtype=int, read_only=True)
        num_exposures = pvproperty_with_rbv(name='NumExposures', dtype=int)
        num_exposures_counter = pvproperty(name='NumExposuresCounter_RBV', dtype=int, read_only=True)
        num_images = pvproperty_with_rbv(name='NumImages', dtype=int)
        num_images_counter = pvproperty(name='NumImagesCounter_RBV', dtype=int, read_only=True)
        read_status = pvproperty(name='ReadStatus', dtype=int)

        class ReverseGroup(PVGroup):
            reverse_x = pvproperty_with_rbv(name='ReverseX', dtype=int)
            reverse_y = pvproperty_with_rbv(name='ReverseY', dtype=int)

        reverse = SubGroup(ReverseGroup, prefix='')

        shutter_close_delay = pvproperty_with_rbv(name='ShutterCloseDelay', dtype=int)
        shutter_close_epics = pvproperty(name='ShutterCloseEPICS', dtype=int)
        shutter_control = pvproperty_with_rbv(name='ShutterControl', dtype=int)
        shutter_control_epics = pvproperty(name='ShutterControlEPICS', dtype=int)
        shutter_fanout = pvproperty(name='ShutterFanout', dtype=int)
        shutter_mode = pvproperty_with_rbv(name='ShutterMode', dtype=int)
        shutter_open_delay = pvproperty_with_rbv(name='ShutterOpenDelay', dtype=int)
        shutter_open_epics = pvproperty(name='ShutterOpenEPICS', dtype=int)
        shutter_status_epics = pvproperty(name='ShutterStatusEPICS_RBV', dtype=int, read_only=True)
        shutter_status = pvproperty(name='ShutterStatus_RBV', dtype=int, read_only=True)

        class SizeGroup(PVGroup):
            size_x = pvproperty_with_rbv(name='SizeX', dtype=int)
            size_y = pvproperty_with_rbv(name='SizeY', dtype=int)

        size = SubGroup(SizeGroup, prefix='')

        status_message = pvproperty(name='StatusMessage_RBV', dtype=str, read_only=True)
        string_from_server = pvproperty(name='StringFromServer_RBV', dtype=str, read_only=True)
        string_to_server = pvproperty(name='StringToServer_RBV', dtype=str, read_only=True)
        temperature = pvproperty_with_rbv(name='Temperature', dtype=int)
        temperature_actual = pvproperty(name='TemperatureActual', dtype=int)
        time_remaining = pvproperty(name='TimeRemaining_RBV', dtype=int, read_only=True)
        trigger_mode = pvproperty_with_rbv(name='TriggerMode', dtype=int)
        config_path = pvproperty_with_rbv(name='CONFIG_PATH', dtype=str)
        config_save_path = pvproperty_with_rbv(name='CONFIG_SAVE_PATH', dtype=str)
        connect = pvproperty(name='CONNECT', dtype=int)
        connected = pvproperty(name='CONNECTED', dtype=int)
        ctrl_dtc = pvproperty_with_rbv(name='CTRL_DTC', dtype=int)
        ctrl_mca_roi = pvproperty_with_rbv(name='CTRL_MCA_ROI', dtype=int)
        debounce = pvproperty_with_rbv(name='DEBOUNCE', dtype=int)
        disconnect = pvproperty(name='DISCONNECT', dtype=int)
        erase = pvproperty(name='ERASE', dtype=int)
        frame_count = pvproperty(name='FRAME_COUNT_RBV', dtype=int, read_only=True)
        invert_f0 = pvproperty_with_rbv(name='INVERT_F0', dtype=int)
        invert_veto = pvproperty_with_rbv(name='INVERT_VETO', dtype=int)
        max_frames = pvproperty(name='MAX_FRAMES_RBV', dtype=int, read_only=True)
        max_frames_driver = pvproperty(name='MAX_FRAMES_DRIVER_RBV', dtype=int, read_only=True)
        max_num_channels = pvproperty(name='MAX_NUM_CHANNELS_RBV', dtype=int, read_only=True)
        max_spectra = pvproperty_with_rbv(name='MAX_SPECTRA', dtype=int)
        xsp_name = pvproperty(name='NAME', dtype=int)
        num_cards = pvproperty(name='NUM_CARDS_RBV', dtype=int, read_only=True)
        num_channels = pvproperty_with_rbv(name='NUM_CHANNELS', dtype=int)
        num_frames_config = pvproperty_with_rbv(name='NUM_FRAMES_CONFIG', dtype=int)
        reset = pvproperty(name='RESET', dtype=int)
        restore_settings = pvproperty(name='RESTORE_SETTINGS', dtype=int)
        run_flags = pvproperty_with_rbv(name='RUN_FLAGS', dtype=int)
        save_settings = pvproperty(name='SAVE_SETTINGS', dtype=int)
        trigger_signal = pvproperty(name='TRIGGER', dtype=int)

        # acquire is pair setpt/rbv, need to watch the setpoint part
        @acquire.setpoint.putter
        async def acquire(self, instance, value):
            image = generate_sim_MCA(4, 4096)
            print('acquire triggered, generated sample MCA')
            # Can navigate out of subgroup into other subgroups
            await self.parent.parent.hdf5.width.write(4)

    settings = SubGroup(Xspress3DetectorSettingsGroup, prefix='')

    # @settings.acquire.startup
    # async def settings(self, instance, async_lib):
    #     #instance.
    #     print(instance.fields['Acquire'])

    # external_trig = pvproperty(name=None, dtype=int)
    # total_points = pvproperty(name=None, dtype=int)
    # spectra_per_point = pvproperty(name=None, dtype=int)
    # make_directories = pvproperty(name=None, dtype=int)
    # rewindable = pvproperty(name=None, dtype=int)

    class PluginBaseGroup(PVGroup):
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
        width = pvproperty(name='ArraySize0_RBV', dtype=int, read_only=True)
        height = pvproperty(name='ArraySize1_RBV', dtype=int, read_only=True)
        depth = pvproperty(name='ArraySize2_RBV', dtype=int, read_only=True)

        bayer_pattern = pvproperty(name='BayerPattern_RBV', dtype=int, read_only=True)
        blocking_callbacks = pvproperty_with_rbv(name='BlockingCallbacks', dtype=str)
        color_mode = pvproperty(name='ColorMode_RBV', dtype=int, read_only=True)
        data_type = pvproperty(name='DataType_RBV', dtype=str, read_only=True)
        dim0_sa = pvproperty(name='Dim0SA', dtype=int)
        dim1_sa = pvproperty(name='Dim1SA', dtype=int)
        dim2_sa = pvproperty(name='Dim2SA', dtype=int)


        dimensions = pvproperty(name='Dimensions_RBV', dtype=int, read_only=True)
        dropped_arrays = pvproperty_with_rbv(name='DroppedArrays', dtype=int)
        # enable = pvproperty_with_rbv(name='EnableCallbacks', dtype=str)
        min_callback_time = pvproperty_with_rbv(name='MinCallbackTime', dtype=int)
        nd_array_address = pvproperty_with_rbv(name='NDArrayAddress', dtype=int)
        nd_array_port = pvproperty_with_rbv(name='NDArrayPort', dtype=int)
        ndimensions = pvproperty(name='NDimensions_RBV', dtype=int, read_only=True)
        plugin_type = pvproperty(name='PluginType_RBV', dtype=int, read_only=True)
        queue_free = pvproperty(name='QueueFree', dtype=int)
        queue_free_low = pvproperty(name='QueueFreeLow', dtype=int)
        queue_size = pvproperty(name='QueueSize', dtype=int)
        queue_use = pvproperty(name='QueueUse', dtype=int)
        queue_use_high = pvproperty(name='QueueUseHIGH', dtype=int)
        queue_use_hihi = pvproperty(name='QueueUseHIHI', dtype=int)
        time_stamp = pvproperty(name='TimeStamp_RBV', dtype=int, read_only=True)
        unique_id = pvproperty(name='UniqueId_RBV', dtype=int, read_only=True)

    roi_data = SubGroup(PluginBaseGroup, prefix='ROIDATA:')

    class Xspress3ChannelGroup(PVGroup):
        # configuration_names = pvproperty(name=None, dtype=int)

        class RoisGroup(PVGroup):

            class Xspress3ROIGroup(PVGroup):
                # configuration_names = pvproperty(name=None, dtype=int)
                bin_low = pvproperty_with_rbv(name='bin_low', dtype=int)
                bin_high = pvproperty_with_rbv(name='bin_high', dtype=int)
                # ev_low = pvproperty(name=None, dtype=int)
                # ev_high = pvproperty(name=None, dtype=int)
                value = pvproperty(name='Value_RBV', dtype=int, read_only=True)
                value_sum = pvproperty(name='ValueSum_RBV', dtype=int, read_only=True)
                enable = pvproperty_with_rbv(name='EnableCallbacks', dtype=int)

            roi01 = SubGroup(Xspress3ROIGroup, prefix='ROI1:')


            class Xspress3ROISettingsGroup(PVGroup):
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
                width = pvproperty(name='ArraySize0_RBV', dtype=int, read_only=True)
                height = pvproperty(name='ArraySize1_RBV', dtype=int, read_only=True)
                depth = pvproperty(name='ArraySize2_RBV', dtype=int, read_only=True)

                bayer_pattern = pvproperty(name='BayerPattern_RBV', dtype=int, read_only=True)
                blocking_callbacks = pvproperty_with_rbv(name='BlockingCallbacks', dtype=str)
                color_mode = pvproperty(name='ColorMode_RBV', dtype=int, read_only=True)
                data_type = pvproperty(name='DataType_RBV', dtype=str, read_only=True)
                dim0_sa = pvproperty(name='Dim0SA', dtype=int)
                dim1_sa = pvproperty(name='Dim1SA', dtype=int)
                dim2_sa = pvproperty(name='Dim2SA', dtype=int)

                dimensions = pvproperty(name='Dimensions_RBV', dtype=int, read_only=True)
                dropped_arrays = pvproperty_with_rbv(name='DroppedArrays', dtype=int)
                #enable = pvproperty_with_rbv(name='EnableCallbacks', dtype=str)
                min_callback_time = pvproperty_with_rbv(name='MinCallbackTime', dtype=int)
                nd_array_address = pvproperty_with_rbv(name='NDArrayAddress', dtype=int)
                nd_array_port = pvproperty_with_rbv(name='NDArrayPort', dtype=int)
                ndimensions = pvproperty(name='NDimensions_RBV', dtype=int, read_only=True)
                plugin_type = pvproperty(name='PluginType_RBV', dtype=int, read_only=True)
                queue_free = pvproperty(name='QueueFree', dtype=int)
                queue_free_low = pvproperty(name='QueueFreeLow', dtype=int)
                queue_size = pvproperty(name='QueueSize', dtype=int)
                queue_use = pvproperty(name='QueueUse', dtype=int)
                queue_use_high = pvproperty(name='QueueUseHIGH', dtype=int)
                queue_use_hihi = pvproperty(name='QueueUseHIHI', dtype=int)
                time_stamp = pvproperty(name='TimeStamp_RBV', dtype=int, read_only=True)
                unique_id = pvproperty(name='UniqueId_RBV', dtype=int, read_only=True)
                array_data = pvproperty(name='ArrayData_RBV', dtype=int, read_only=True)

            ad_attr01 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI1:')

            roi02 = SubGroup(Xspress3ROIGroup, prefix='ROI2:')

            ad_attr02 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI2:')

            roi03 = SubGroup(Xspress3ROIGroup, prefix='ROI3:')

            ad_attr03 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI3:')

            roi04 = SubGroup(Xspress3ROIGroup, prefix='ROI4:')

            ad_attr04 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI4:')

            roi05 = SubGroup(Xspress3ROIGroup, prefix='ROI5:')

            ad_attr05 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI5:')

            roi06 = SubGroup(Xspress3ROIGroup, prefix='ROI6:')

            ad_attr06 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI6:')

            roi07 = SubGroup(Xspress3ROIGroup, prefix='ROI7:')

            ad_attr07 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI7:')

            roi08 = SubGroup(Xspress3ROIGroup, prefix='ROI8:')

            ad_attr08 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI8:')

            roi09 = SubGroup(Xspress3ROIGroup, prefix='ROI9:')

            ad_attr09 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI9:')

            roi10 = SubGroup(Xspress3ROIGroup, prefix='ROI10:')

            ad_attr10 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI10:')

            roi11 = SubGroup(Xspress3ROIGroup, prefix='ROI11:')

            ad_attr11 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI11:')

            roi12 = SubGroup(Xspress3ROIGroup, prefix='ROI12:')

            ad_attr12 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI12:')

            roi13 = SubGroup(Xspress3ROIGroup, prefix='ROI13:')

            ad_attr13 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI13:')

            roi14 = SubGroup(Xspress3ROIGroup, prefix='ROI14:')

            ad_attr14 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI14:')

            roi15 = SubGroup(Xspress3ROIGroup, prefix='ROI15:')

            ad_attr15 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI15:')

            roi16 = SubGroup(Xspress3ROIGroup, prefix='ROI16:')

            ad_attr16 = SubGroup(Xspress3ROISettingsGroup, prefix='ROI16:')

            # num_rois = pvproperty(name=None, dtype=int)

        rois = SubGroup(RoisGroup, prefix='')

        vis_enabled = pvproperty(name='PluginControlVal', dtype=int)

    channel1 = SubGroup(Xspress3ChannelGroup, prefix='C1_')
    channel2 = SubGroup(Xspress3ChannelGroup, prefix='C2_')

    class Xspress3FileStoreGroup(PVGroup):
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
        width = pvproperty(name='ArraySize0_RBV', dtype=int, read_only=True, value=1)
        height = pvproperty(name='ArraySize1_RBV', dtype=int, read_only=True, value=1)
        depth = pvproperty(name='ArraySize2_RBV', dtype=int, read_only=True, value=1)
        
        bayer_pattern = pvproperty(name='BayerPattern_RBV', dtype=int, read_only=True)
        blocking_callbacks = pvproperty_with_rbv(name='BlockingCallbacks', dtype=str)
        color_mode = pvproperty(name='ColorMode_RBV', dtype=int, read_only=True)
        data_type = pvproperty(name='DataType_RBV', dtype=str, read_only=True)
        dim0_sa = pvproperty(name='Dim0SA', dtype=int)
        dim1_sa = pvproperty(name='Dim1SA', dtype=int)
        dim2_sa = pvproperty(name='Dim2SA', dtype=int)

        dimensions = pvproperty(name='Dimensions_RBV', dtype=int, read_only=True)
        dropped_arrays = pvproperty_with_rbv(name='DroppedArrays', dtype=int)
        enable = pvproperty_with_rbv(name='EnableCallbacks', dtype=str)
        min_callback_time = pvproperty_with_rbv(name='MinCallbackTime', dtype=int)
        nd_array_address = pvproperty_with_rbv(name='NDArrayAddress', dtype=int)
        nd_array_port = pvproperty_with_rbv(name='NDArrayPort', dtype=int)
        ndimensions = pvproperty(name='NDimensions_RBV', dtype=int, read_only=True)
        plugin_type = pvproperty(name='PluginType_RBV', dtype=int, read_only=True)
        queue_free = pvproperty(name='QueueFree', dtype=int)
        queue_free_low = pvproperty(name='QueueFreeLow', dtype=int)
        queue_size = pvproperty(name='QueueSize', dtype=int)
        queue_use = pvproperty(name='QueueUse', dtype=int)
        queue_use_high = pvproperty(name='QueueUseHIGH', dtype=int)
        queue_use_hihi = pvproperty(name='QueueUseHIHI', dtype=int)
        time_stamp = pvproperty(name='TimeStamp_RBV', dtype=int, read_only=True)
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
        boundary_align = pvproperty_with_rbv(name='BoundaryAlign', dtype=int)
        boundary_threshold = pvproperty_with_rbv(name='BoundaryThreshold', dtype=int)
        compression = pvproperty_with_rbv(name='Compression', dtype=int)
        data_bits_offset = pvproperty_with_rbv(name='DataBitsOffset', dtype=int)

        class ExtraDimNameGroup(PVGroup):
            name_x = pvproperty(name='ExtraDimNameX_RBV', dtype=int, read_only=True)
            name_y = pvproperty(name='ExtraDimNameY_RBV', dtype=int, read_only=True)
            name_n = pvproperty(name='ExtraDimNameN_RBV', dtype=int, read_only=True)

        extra_dim_name = SubGroup(ExtraDimNameGroup, prefix='')


        class ExtraDimSizeGroup(PVGroup):
            size_x = pvproperty_with_rbv(name='ExtraDimSizeX', dtype=int)
            size_y = pvproperty_with_rbv(name='ExtraDimSizeY', dtype=int)
            size_n = pvproperty_with_rbv(name='ExtraDimSizeN', dtype=int)

        extra_dim_size = SubGroup(ExtraDimSizeGroup, prefix='')

        io_speed = pvproperty(name='IOSpeed', dtype=int)
        num_col_chunks = pvproperty_with_rbv(name='NumColChunks', dtype=int)
        num_data_bits = pvproperty_with_rbv(name='NumDataBits', dtype=int)
        num_extra_dims = pvproperty_with_rbv(name='NumExtraDims', dtype=int)
        num_frames_chunks = pvproperty_with_rbv(name='NumFramesChunks', dtype=int)
        num_frames_flush = pvproperty_with_rbv(name='NumFramesFlush', dtype=int)
        num_row_chunks = pvproperty_with_rbv(name='NumRowChunks', dtype=int)
        run_time = pvproperty(name='RunTime', dtype=int)
        szip_num_pixels = pvproperty_with_rbv(name='SZipNumPixels', dtype=int)
        store_attr = pvproperty_with_rbv(name='StoreAttr', dtype=str)
        store_perform = pvproperty_with_rbv(name='StorePerform', dtype=str)
        zlevel = pvproperty_with_rbv(name='ZLevel', dtype=int)
        num_capture_calc = pvproperty(name='NumCapture_CALC', dtype=int)
        num_capture_calc_disable = pvproperty(name='NumCapture_CALC.DISA', dtype=int)

    hdf5 = SubGroup(Xspress3FileStoreGroup, prefix='HDF5:')

    



if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
            default_prefix='XSPRESS3-EXAMPLE:',
            desc='Run IOC simulating Xspress3')

    # Instantiate IOC, assigning prefix for PV names
    ioc = SSRLXspress3DetectorGroup(**ioc_options)
    print('PVs:', list(ioc.pvdb))

    # Run IOC
    run(ioc.pvdb, **run_options)