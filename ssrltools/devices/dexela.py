"""
Devices (ohpyd) for use on SSRL beamlines running Bluesky

AREA DETECTOR SUPPORT

DETECTOR SUPPORT

MOTORS, POSITIONERS, AXES, ...

SHUTTERS


"""
import os
from pathlib import Path
import numpy as np
import uuid
import threading

from ophyd import Device, Component as Cpt, DeviceStatus
from ophyd import Signal, CamBase
from ophyd import AreaDetector, SingleTrigger

from ophyd.signal import EpicsSignal, EpicsSignalBase
from ophyd.areadetector import EpicsSignalWithRBV as SignalWithRBV
from ophyd.areadetector.detectors import DetectorBase, DexelaDetector
from ophyd.areadetector.filestore_mixins import (resource_factory, 
                                            FileStoreTIFFIterativeWrite)
from ophyd.areadetector import TIFFPlugin

class DexelaTiffPlugin(TIFFPlugin, FileStoreTIFFIterativeWrite):
    pass

class DexelaDet15(SingleTrigger, DexelaDetector):
    """
    Final class for Dexela Detector on SSRL BL 1-5

    det = DexelaDet15(prefix)
    """
    # DexelaDetector from ophyd pulls in all Dexela specific PV's
    write_path = 'C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\fstore\\tmpFileStore\\'
    # In case where TIFF plugin is being used
    tiff = Cpt(DexelaTiffPlugin, 'TIFF1:',
                        write_path_template=write_path,
                        read_path_template=write_path)
    # Else there should be an NDArrayData PV
    image = Cpt(EpicsSignal, 'ArrayData')

    def trigger(self):
        super().trigger()
        
    # Could add more attributes to file_plugin
    # could add stage behavior