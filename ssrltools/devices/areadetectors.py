"""
Devices (ohpyd) for use on SSRL beamlines running Bluesky

AREA DETECTOR SUPPORT

DEXELA

"""
import os
from pathlib import Path
import numpy as np
import uuid
import threading

from ophyd import Device, Component as Cpt, DeviceStatus, ADComponent as ADCpt
from ophyd import CamBase
from ophyd import AreaDetector, SingleTrigger

from ophyd.base import ADBase
from ophyd.signal import SignalRO, EpicsSignal, EpicsSignalBase, Signal
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV
from ophyd.areadetector.detectors import (DetectorBase, DexelaDetector, 
                                            PilatusDetector, MarCCDDetector)
from ophyd.areadetector.filestore_mixins import (resource_factory, 
                                            FileStoreTIFFIterativeWrite,
                                            FileStorePluginBase)
from ophyd.areadetector import TIFFPlugin, cam

class DexelaTiffPlugin(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass

class SSRLDexelaDet(SingleTrigger, DexelaDetector):
    """
    Contains main PV's
    """
    pass

class HackedCam(cam.DexelaDetectorCam):
    port_name = Cpt(SignalRO, value='DEX1')

class DexelaDet15(SSRLDexelaDet):
    """
    Final class for Dexela Detector on SSRL BL 1-5
    - add Plugins (TIFF plugin, etc)
    - set up read, configuration attrs

    det = DexelaDet15(prefix, name='name', read_attrs=['attr'])
    """
    # DexelaDetector from ophyd pulls in all Dexela specific PV's
    write_path = 'E:\\dexela_images\\'

    # Hack to get around EPICS strangeness. Port_name and nd_array_ports
    # don't match...
    cam = ADCpt(HackedCam, '')

    # In case where TIFF plugin is being used
    tiff = Cpt(DexelaTiffPlugin, 'TIFF:',
                       write_path_template=write_path,
                       read_path_template='/dexela_images/',
                       path_semantics='windows')
    # Else there should be an NDArrayData PV
    image = Cpt(EpicsSignal, 'IMAGE1:ArrayData')
    highest_pixel = Cpt(EpicsSignal, 'HighestPixel', labels=())

    # Could add more attributes to file_plugin
    # could add stage behavior, maybe to coerce pv's?


class PilatusTiffPlugin(TIFFPlugin, FileStoreTIFFIterativeWrite):
    """PilatusTiffPlugin... currently identical to Dexela. 
    """
    pass

class PilatusDet15(SingleTrigger, PilatusDetector):
    """PilatusDet15 
    det = PilatusDet15(prefix, name='name', read_attrs=['tiff'])
    """
    # file write path
    write_path = 'E:\\pilatus_images'

    tiff = Cpt(PilatusTiffPlugin, 'TIFF:', 
                write_path_template=write_path,
                read_path_template='/pilatus_images/',
                path_semantics='windows')
                
class MarTiffFakePlugin(ADBase, GenerateDatumInterface):
    """
    Connects to subset of PV's present in MarCCD, without the plugin-specific pv
    Look to stage sigs etc for which are necessary

    Hacking to connect to PV's with the same class structure, but without the
    plugin machinery

    Commented lines denote PV's that don't exist in this IOC
    """
    _default_suffix = ''
    # _html_docs = ['NDPluginFile.html']
    # _plugin_type = 'NDPluginFile'
    FileWriteMode = enum(SINGLE=0, CAPTURE=1, STREAM=2)

    auto_increment = Cpt(SignalWithRBV, 'AutoIncrement', kind='config')
    auto_save = Cpt(SignalWithRBV, 'AutoSave', kind='config')
    capture = Cpt(SignalWithRBV, 'Capture')
    delete_driver_file = Cpt(SignalWithRBV, 'DeleteDriverFile', kind='config')
    file_format = Cpt(SignalWithRBV, 'FileFormat', kind='config')
    file_name = Cpt(SignalWithRBV, 'FileName', string=True, kind='config')
    file_number = Cpt(SignalWithRBV, 'FileNumber')
    # file_number_sync = Cpt(EpicsSignal, 'FileNumber_Sync')
    file_number_write = Cpt(EpicsSignal, 'FileNumber_write')
    file_path = Cpt(SignalWithRBV, 'FilePath', string=True, kind='config')
    file_path_exists = Cpt(EpicsSignalRO, 'FilePathExists_RBV', kind='config')
    file_template = Cpt(SignalWithRBV, 'FileTemplate', string=True, kind='config')
    file_write_mode = Cpt(SignalWithRBV, 'FileWriteMode', kind='config')
    full_file_name = Cpt(EpicsSignalRO, 'FullFileName_RBV', string=True, kind='config')
    num_capture = Cpt(SignalWithRBV, 'NumCapture', kind='config')
    num_captured = Cpt(EpicsSignalRO, 'NumCaptured_RBV')
    read_file = Cpt(SignalWithRBV, 'ReadFile')
    write_file = Cpt(SignalWithRBV, 'WriteFile')
    write_message = Cpt(EpicsSignal, 'WriteMessage', string=True)
    write_status = Cpt(EpicsSignal, 'WriteStatus')

class MarFileStoreTIFF(FileStoreTIFFIterativeWrite, MarTiffFakePlugin):
    """
    Mostly mimicking FileStoreTIFF, and Xspress3FileStore
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.stage_sigs.update([('file_template', '%s%s_%6.6d.tiff'),
        #                         ('file_write_mode', 'Single'),
        #                         ])

        # 'Single' file mode means one image : one file
        # It does NOT mean 'num_images' is ignored

        # remove array_counter
        self.stage_sigs.pop('array_counter')

        # # add filestore_spec
        # self.filestore_spec = 'AD_TIFF'

        # add enable signal that's missing from lack of real plugin...?
        # checked by trigger dispatching
        self.enable = Signal(name='Enable', value='1')

    # def get_frames_per_point(self):
    #     return self.parent.cam.num_images.get()

    # def stage(self):
    #     super().stage()  ## apply stage sigs (BlueskyInterface.stage())

    #     self._fn = self._fp

    #     resource_kwargs = {'template': self.file_template.get(),
    #                         'filename': self.file_name.get(),
    #                         'frame_per_point': self.get_frames_per_point()}
    #     self._generate_resource(resource_kwargs)

class MarCCDDet15(SingleTrigger, MarCCDDetector):
    """MarCCDDet15 
    det = MarCCDDet15(prefix, name='name', read_attrs=['tiff'])
    """
    # file write path
    write_path = 'E:\\MarCCD_images'

    tiff = Cpt(DexelaTiffPlugin, 'TIFF:', 
                write_path_template=write_path,
                read_path_template='/MarCCD_images/',
                path_semantics='windows')