"""
Setup script for simulating HiTp setup at BL1-5

@author: roberttk
"""
# Setup 
import os
import numpy as np
from pathlib import Path
import uuid

from ophyd import Device, Component
from ophyd import Signal
from ophyd.sim import SynAxis, SynGauss, SynSignal
from ophyd.signal import EpicsSignal
from ophyd.areadetector.filestore_mixins import resource_factory

from ssrltools.devices import ShutterBase
from ssrltools.sim import ArraySynSignal
import time

p_x = SynAxis(name='plate_x', labels={'motors'})
p_y = SynAxis(name='plate_y', labels={'motors'})
p_z = SynAxis(name='plate_z', labels={'motors'})
p_th = SynAxis(name='plate_th', labels={'motors'})



class SynShutter(ShutterBase):
    """
    Simulated shutter.  No unknown states allowed.  
    """
    # set value outside of __init__ to add to component list
    sig = Component(Signal, value=0)

    def open(self):
        """
        Open simulated shutter
        Pause to allow motion to complete.  
        """
        if not self.isOpen:
            self.sig.put(1)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    def close(self):
        """
        Close simulated shutter
        Pause to allow motion to complete.  
        """
        if self.isOpen:
            self.sig.put(0)
            if self.delay_s > 0:
                time.sleep(self.delay_s)    # blocking call OK here

    @property
    def state(self):
        """
        returns 'open', 'close'
        """
        if self.sig.value == self.open_value:
            return 'open'
        elif self.sig.value == self.close_value:
            return 'close'
        else:
            return 'unknown'

class SynSlits(Device):
    """
    Simulated blocking slits class composed of left/right slits
    Can use simple Signal class for holding values

    Methods:
    setGap

    """
    lslit = Component(Signal, value=0)
    rslit = Component(Signal, value=0)

    def __init__(self, name, gap):
        self.__name__ = name
        self.lslit.put(gap / 2) # distance from center
        self.rslit.put(gap / 2) # 0 = closed
        self.delay_s = 0

    @property
    def gap(self):
        """ Return total gap (sum of two slit distances) """
        return self.lslit.value + self.rslit.value

    def set_gap(self,gap_size):
        """
        set gap between slits symmetrically 
        """
        self.lslit = gap_size / 2
        self.rslit = gap_size / 2
        if self.delay_s > 0:
            time.sleep(self.delay_s)        

class SynFilters(Device):
    """
    Simulated filter box
    Composed of 4 filters with 1,2,4,8 thickness
    Attenuation follows Beer-Lambert law
    """
    def __init__(self, name, filters):
        self.__name__ = name
        self.filt0 = filters[0]
        self.filt1 = filters[1]
        self.filt2 = filters[2]
        self.filt3 = filters[3]

    @property
    def atten(self):
        return np.exp(self.filt0 + 2*self.filt1 + 4*self.filt2 + 8*self.filt3)

    def put(self, filters):
        self.filt0 = filters[0]
        self.filt1 = filters[1]
        self.filt2 = filters[2]
        self.filt3 = filters[3]

# Experimental setup ------------------------------------------------------
# In real operation, moving motors/monos will affect detector results.
# For simulated beamline, need to tie components together

class ArraySynLocator(ArraySynSignal):
    """
    Base class for synthetic array signals. 
    Same interface as a normal ArraySignal, but with simulated data and 
    standard filestore
    
    Example
    -------
    motor1 = SynAxis(name='motor1')
    motor2 = SynAxis(name='motor2')
    det = ArraySynLocator('det', motor1, 'motor1', motor2, 'motor2', 
                   Imax=1, sigma1=1, sigma2=1)
    """
    
    def __init__(self, name, motor1, motor_field1, motor2, motor_field2, 
                 slits, slit_field, filters, filters_field,
                 Imax=100,
                 noise=None, random_state=None, 
                 size=10, pt_density=20, noise_multiplier=1, **kwargs):
        if noise not in ('poisson', 'uniform', None):
            raise ValueError("Noise must be one of 'poisson', 'uniform', None")
            
        self._motor1 = motor1
        self._motor2 = motor2
        self._slits = slits
        self._filters = filters

        self.__name__ = name
        
        if random_state is None:
            random_state = np.random
                                
        # Function to simulate calls to pv
        def func():
            """
            Gaussian centered at motor positions.  Image identifies x, y positions
            Center of image is 0, 0.

            Returns
            -------
            Array imitating image   

            """
            m1 = motor1.read()[motor_field1]['value']
            m2 = motor2.read()[motor_field2]['value']

            # atten = filters.get()

            # generate mesh for evauation
            x = np.linspace(-size/2, size/2, pt_density)
            y = np.linspace(-size/2, size/2, pt_density)
            xx, yy = np.meshgrid(x, y, sparse=True)
            
            v = Imax * np.exp(-( ((xx-m1)**2 / 2) +  \
                                 ((yy-m2)**2 / 2) ))
            if noise == 'poisson':
                v = int(random_state.poission(np.round(v), 1))
            elif noise == 'uniform':
                v += random_state.uniform(-1, 1) * noise_multiplier
        
            return v
        
        super().__init__(func=func, name=name, **kwargs)
        # Sets self.value to func evaluation. 