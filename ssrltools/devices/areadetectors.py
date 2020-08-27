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
from ophyd import SignalRO, CamBase
from ophyd import AreaDetector, SingleTrigger

from ophyd.signal import EpicsSignal, EpicsSignalBase
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV
from ophyd.areadetector.detectors import (DetectorBase, DexelaDetector, 
                                            PilatusDetector, MarCCDDetector)
from ophyd.areadetector.filestore_mixins import (resource_factory, 
                                            FileStoreTIFFIterativeWrite)
from ophyd.areadetector import TIFFPlugin

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