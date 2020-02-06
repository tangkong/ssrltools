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
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.filestore_mixins import (resource_factory, 
                                            FileStoreTIFFIterativeWrite)


class DexelaCam(CamBase):
    """
    Connect to all PV's except for image array PV

    Instantiating as a component will prepend the prefix 
    provided at init to PV name
    """
    serial_number = Cpt(EpicsSignal, 'DEXSerialNumber')
    binning_mode = Cpt(SignalWithRBV, 'DEXBinningMode')
    full_well_mode = Cpt(SignalWithRBV, 'DEXFullWellMode')
    readout_mode = Cpt(SignalWithRBV, 'DEXReadoutMode')
    software_trigger = Cpt(EpicsSignal, 'DEXSoftwareTrigger')

    # Corrections Directory
    corr_dir = Cpt(EpicsSignal, 'DEXCorrectionsDirectory', string=True)

    # Offset Corrections (Dark field corrections)
    num_offset_frames = Cpt(EpicsSignal, 'DEXNumOffsetFrames')
    curr_offset_frame = Cpt(EpicsSignal, 'DEXCurrentOffsetFrame')
    acq_offset = Cpt(EpicsSignal, 'DEXAcquireOffset')
    use_offset = Cpt(EpicsSignal, 'DEXUseOffset')
    offset_available = Cpt(EpicsSignal, 'DEXOffsetAvailable')
    offset_file = Cpt(EpicsSignal, 'DEXOffsetFile', string=True)
    load_offset_file = Cpt(EpicsSignal, 'DEXLoadOffsetFile')
    save_offset_file = Cpt(EpicsSignal, 'DEXSaveOffsetFile')
    offset_constant = Cpt(SignalWithRBV, 'DEXOffsetConstant')

    # Gain Corrections (flat field corrections)
    num_gain_frames = Cpt(EpicsSignal, 'DEXNumGainFrames')
    curr_gain_frame = Cpt(EpicsSignal, 'DEXCurrentGainFrame')
    acq_gain = Cpt(EpicsSignal, 'DEXAcquireGain')
    use_gain = Cpt(EpicsSignal, 'DEXUseGain')
    gain_available = Cpt(EpicsSignal, 'DEXGainAvailable')
    gain_file = Cpt(EpicsSignal, 'DEXGainFile', string=True)
    load_gain_file = Cpt(EpicsSignal, 'DEXLoadGainFile')
    save_gain_file = Cpt(EpicsSignal, 'DEXSaveGainFile')

    # Defect Map Corections (bad pixel corrections)
    use_defect_map = Cpt(EpicsSignal, 'DEXUseDefectMap')
    defect_map_available = Cpt(EpicsSignal, 'DEXdefectmapAvailable')
    defect_map_file = Cpt(EpicsSignal, 'DEXDefectMapFile', string=True)
    load_defect_map_file = Cpt(EpicsSignal, 'DEXLoadDefectMapFile')

class DexelaDetector(AreaDetector):
    """
    Dexela Detector class. 
    AreaDetector init takes a prefix which gets passed through to DexelaCam class

    Example:

    class MyDet(SingleTrigger, AreaDetector):
        pass

    prefix = 'dexela1'
    det = MyDet(prefix, name)
    """
    # PV's within DexelaCam are labeled "{prefix}cam1:{PVname}"
    cam = Cpt(DexelaCam, 'cam1:', 
                read_attrs=[], 
                configuration_attrs=['image_mode', 'trigger_mode',
                                     'acquire_time', 'acquire_period']
            )

class DexelaDet15(SingleTrigger, DexelaDetector):
    """
    Final class for Dexela Detector on SSRL BL 1-5

    det = DexelaDet15(prefix)
    """
    write_path = '~/tmpFileStore/'
    file_plugin = Cpt(FileStoreTIFFIterativeWrite, 
                        write_path_template=write_path)
    # Could add more attributes to file_plugin
    # could add stage behavior


