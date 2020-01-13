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
from ophyd.areadetector.filestore_mixins import resource_factory


class ArraySignal(EpicsSignalBase):
    def __init__(self, read_pv, **kwargs):
        super().__init__(read_pv, **kwargs)
        cl = self.cl
        base_pv, _ = read_pv.split(':', maxsplit=1)
        self._size_pv = cl.get_pv( 
                            ':'.join((base_pv,'ArraySize_RBV')))
        self._last_ret = None
        self._asset_docs_cache = []

    def trigger(self):
        tmpRoot = 'C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\ssrltools\\fstore'
        tmpPath = '\\tmp'
        os.makedirs(tmpRoot+tmpPath, exist_ok=True)
        st = super().trigger() # re-evaluates self._func, puts into value
        # Returns NullType
        ret = super().read()    # Signal.read() exists, not SynSignal.read()
        # But using Signal.read() does not allow uid's to be passed into mem.
        val = ret[self.name]['value']
        
        resource, datum_factory = resource_factory(
                spec='npy',
                root=tmpRoot,
                resource_path=tmpRoot + f'\\tmp\\{uuid.uuid4()}.npy',
                resource_kwargs={},
                path_semantics='windows')
        datum = datum_factory({})
        
        self._asset_docs_cache.append(('resource', resource))
        self._asset_docs_cache.append(('datum', datum))
        fpath = Path(resource['root']) / resource['resource_path']
        np.save(fpath, val)
        
        # replace 'value' in read dict with some datum id
        ret[self.name]['value'] = datum['datum_id']
        self._last_ret = ret
        return st
    
    def describe(self):
        ret = super().describe()
        ret[self.name]['shape'] = [int(k)
                                   for k in
                                   self._size_pv.get()]
        ret[self.name]['external'] = 'FILESTORE:'
        del ret[self.name]['upper_ctrl_limit']
        del ret[self.name]['lower_ctrl_limit']
        return ret

    def read(self):
        if self._last_ret is None:
            raise Exception('read before being triggered')
        return self._last_ret

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item

class ShutterBase(Device):
    """
    Base class for all shutter type devices
    Adapted from apstools

    PARAMETERS...
    """
    valid_open_values = ["open", "opened",]   # lower-case strings ONLY
    valid_close_values = ["close", "closed",]
    open_value = 1      # value of "open"
    close_value = 0     # value of "close"
    delay_s = 0.0       # time to wait (s) after move is complete
    busy = Cpt(Signal, value=False)
    unknown_state = "unknown"       # cannot move to this position

    # - - - - likely to override these methods in subclass - - - -

    def open(self):
        """
        BLOCKING: request shutter to open, called by set()
        
        Must implement in subclass of ShutterBase()
        
        EXAMPLE::

            if not self.isOpen:
                self.signal.put(self.open_value)
                if self.delay_s > 0:
                    time.sleep(self.delay_s)    # blocking call OK here

        """
        raise NotImplementedError("must implement in subclass")

    def close(self):
        """
        BLOCKING: request shutter to close, called by set()
        
        Must implement in subclass of ShutterBase()
        
        EXAMPLE::

            if not self.isClosed:
                self.signal.put(self.close_value)
                if self.delay_s > 0:
                    time.sleep(self.delay_s)    # blocking call OK here

        """
        raise NotImplementedError("must implement in subclass")

    @property
    def state(self):
        """
        returns 'open', 'close', or 'unknown'
        
        Must implement in subclass of ShutterBase()
        
        EXAMPLE::

            if self.signal.value == self.open_value:
                result = self.valid_open_values[0]
            elif self.signal.value == self.close_value:
                result = self.valid_close_values[0]
            else:
                result = self.unknown_state
            return result

        """
        raise NotImplementedError("must implement in subclass")
    
    # - - - - - - possible to override in subclass - - - - - -

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valid_open_values = list(map(self.lowerCaseString, self.valid_open_values))
        self.valid_close_values = list(map(self.lowerCaseString, self.valid_close_values))
    
    @property
    def isOpen(self):
        """is the shutter open?"""
        return str(self.state) == self.valid_open_values[0]
    
    @property
    def isClosed(self):
        """is the shutter closed?"""
        return str(self.state) == self.valid_close_values[0]

    def inPosition(self, target):
        """is the shutter at the target position?"""
        self.validTarget(target)
        __value__ = self.lowerCaseString(target)
        if __value__ in self.valid_open_values and self.isOpen:
            return True
        elif __value__ in self.valid_close_values and self.isClosed:
            return True
        return False

    def set(self, value, **kwargs):
        """
        plan: request the shutter to open or close

        PARAMETERS
        
        value : str
            any from ``self.choices`` (typically "open" or "close")
        
        kwargs : dict
            ignored at this time

        """
        if self.busy.value:
            raise RuntimeError("shutter is operating")
        
        __value__ = self.lowerCaseString(value)
        self.validTarget(__value__)

        status = DeviceStatus(self)
        
        if self.inPosition(__value__):
            # no need to move, cut straight to the end
            status._finished(success=True)
        else:
            def move_it():
                # runs in a thread, no need to "yield from"
                self.busy.put(True)
                if __value__ in self.valid_open_values:
                    self.open()
                elif __value__ in self.valid_close_values:
                    self.close()
                self.busy.put(False)
                status._finished(success=True)
            # get it moving
            threading.Thread(target=move_it, daemon=True).start()
        return status
    
    # - - - - - - not likely to override in subclass - - - - - -

    def addCloseValue(self, text):
        """a synonym to close the shutter, use with set()"""
        self.valid_close_values.append(self.lowerCaseString(text))
        return self.choices     # return the list of acceptable values
    
    def addOpenValue(self, text):
        """a synonym to open the shutter, use with set()"""
        self.valid_open_values.append(self.lowerCaseString(text))
        return self.choices     # return the list of acceptable values

    @property
    def choices(self):
        """return list of acceptable choices for set()"""
        return self.valid_open_values + self.valid_close_values
    
    def lowerCaseString(self, value):
        """ensure any given value is a lower-case string"""
        return str(value).lower()

    def validTarget(self, target, should_raise=True):
        """
        return whether (or not) target value is acceptable for self.set()
        
        raise ValueError if not acceptable (default)
        """
        acceptable_values = self.choices
        ok = self.lowerCaseString(target) in acceptable_values
        if not ok and should_raise:
            msg = "received " + str(target)
            msg += " : should be only one of "
            msg += " | ".join(acceptable_values)
            raise ValueError(msg)
        return ok

class DexelaCam(CamBase):
    """
    Connect to all PV's except for image array PV
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

class DexelaDetector(DetectorBase):
    """
    Example:

    class MyDet(SingleTrigger, AreaDetector):
        pass

    prefix = 'dexela1'
    det = MyDet(prefix)
    """
    cam = Cpt(DexelaCam, 'cam1:')