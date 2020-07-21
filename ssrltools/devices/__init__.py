import os
from pathlib import Path
import numpy as np
import uuid
import threading

from ophyd import Device, Component as Cpt, DeviceStatus
from ophyd import Signal, CamBase
from ophyd import AreaDetector, SingleTrigger

from ophyd.signal import EpicsSignal, EpicsSignalBase
from ophyd.areadetector.filestore_mixins import (resource_factory, 
                                            FileStoreTIFFIterativeWrite)

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
