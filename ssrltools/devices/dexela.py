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

class SSRLDexelaDet(SingleTrigger, DexelaDetector):
    """
    Contains main PV's
    """
    pass