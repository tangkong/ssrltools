# -*- coding: utf-8 -*-
"""
Simulated hardware for use at SSRL beamlines running Bluesky

.. autosummary::

"""
import numpy as np
import random

from ophyd import Signal
from ophyd.sim import SynSignal #reads namespace of simulated motors, detectors

import tifffile
import fabio


def testModule():
    return 9

class Syn2DRings(SynSignal):
    """
    Synthetic Signal that returns concentric circles with sigma spread
    when triggered.  Built using Syn2DGauss as an example.
    
    Parameters
    ----------
    
    """
    def __init__(self, name, 
                 motor0, motor_field0, motor1, motor_field1,
                 center, Imax, spacing=10, sigma=1, 
                 noise=None, noise_multiplier=1, random_state=None, **kwargs):
        
        if noise not in ('poisson', 'uniform', None):
            raise ValueError("Noise must be one of 'poisson', 'uniform', None")
        self._motor = motor0
        self._motor1 = motor1
        if random_state is None:
            random_state = np.random
            
        def func():
            """
            Return value at motor position of a patter of concentric circles. 
            For simplicity, only generate circle   
            """
            x = motor0.read()[motor_field0]['value']
            y = motor1.read()[motor_field1]['value']
            m = np.array([x, y]) # point to evaluate at
            
            v = Imax * np.exp(-np.sum((m - center) ** 2) / (2 * sigma ** 2))
            return v
        
        super().__init__(name=name, func=func, **kwargs)

#---------------- Building class for array simulator
from ophyd.sim import SynSignal
from ophyd.areadetector.filestore_mixins import resource_factory
from pathlib import Path
import os
import numpy as np
import uuid

class ArraySynSignal(SynSignal):
    """
    Base class for synthetic array signals. 
    Same interface as a normal ArraySignal, but with simulated data and 
    filestore
    """
    _asset_docs_cache = []
    _last_ret = None
    point_number = 0

    def trigger(self):
        # not running at the moment.... but super.trigger() is.  
        tmpRoot = 'C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\fstore'
        tmpPath = '\\tmp'
        os.makedirs(tmpRoot+tmpPath, exist_ok=True)
        st = super().trigger() # re-evaluates self._func, puts into value
        # Returns NullType
        ret = super().read()    # Signal.read() exists, not SynSignal.read()
        # But using Signal.read() does not allow uid's to be passed into mem.
        val = ret[self.name]['value']
        
        # AD_TIFF handler generates filename by populating template
        # self.template % (self.path, self.filename, self.point_number)
        self.point_number += 1 
        resource, datum_factory = resource_factory(
                spec='AD_TIFF',
                root=tmpRoot,
                resource_path=tmpRoot + '\\tmp\\',
                resource_kwargs={'template': '%s%s_%d.tiff' , 
                                    'filename': f'{uuid.uuid4()}'},
                path_semantics='windows')
        datum = datum_factory({'point_number': self.point_number})
        
        self._asset_docs_cache.append(('resource', resource))
        self._asset_docs_cache.append(('datum', datum))

        fname = (resource['resource_kwargs']['filename'] 
                    + f'_{self.point_number}.tiff')
        fpath = Path(resource['root']) / resource['resource_path'] / fname
        # for tiff spec
        tifffile.imsave(fpath, val)
        
        # replace 'value' in read dict with some datum id
        ret[self.name]['value'] = datum['datum_id']
        self._last_ret = ret
        return st
    
    def describe(self):
        ret = super().describe()
        ret[self.name]['external'] = 'FILESTORE:'
        return ret
    
    def read(self):
        '''Put the status of the signal into a simple dictionary format
        for data acquisition

        Returns
        -------
            dict
        '''
        # Appears to break things, throw resource sentinel issue... 
        # need to initialize sentinel when starting RunEngine
        # Is ostensibly the same as Signal.read()?...
        if self._last_ret is not None:
            return self._last_ret
            # return {self.name: {'value': self._last_ret,
            #                     'timestamp': self.timestamp}}
        else: # If detector has not been triggered already
            raise Exception('read before being triggered')
            # return {self.name: {'value': self.get(),
            #                      'timestamp': self.timestamp}}

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item

class ArraySynGauss(ArraySynSignal):
    """
    Output a 2D Gaussian spot at centered at motor position.  

    Example
    -------
    motor1 = SynAxis(name='motor1')
    motor2 = SynAxis(name='motor2')
    det = SynGauss('det', motor1, 'motor1', motor2, 'motor2', 
                   center1=0, center2=0, Imax=1, sigma1=1, sigma2=1)
    """
    def __init__(self, name, motor1, motor_field1, motor2, motor_field2, 
                 center1, center2, Imax, sigma1=1, sigma2=2,
                 noise='poisson', random_state=None, 
                 size=5, pt_density=5, noise_multiplier=1, **kwargs):
        if noise not in ('poisson', 'uniform', None):
            raise ValueError("Noise must be one of 'poisson', 'uniform', None")
            
        self._motor1 = motor1
        self._motor2 = motor2
        self.__name__ = name
        
        if random_state is None:
            random_state = np.random
                    
        # Function to simulate calls to pv
        def func():
            """
            2D gaussian signal, centered around center1, center2
            Assume image is square

            Returns
            -------
            Array imitating image

            """
            m1 = motor1.read()[motor_field1]['value']
            m2 = motor2.read()[motor_field2]['value']
            
            # generate mesh for evauation
            x = np.linspace(m1-size/2, m1+size/2, pt_density)
            y = np.linspace(m2-size/2, m2+size/2, pt_density)
            
            xx, yy = np.meshgrid(x, y, sparse=True)
            
            v = Imax * np.exp(-( ((xx-center1)**2 / (2*sigma1**2)) +  \
                                 ((yy-center2)**2 / (2*sigma2**2)) ))
            if noise == 'poisson':
                v += random_state.poisson(np.mean(v), np.shape(v))
            elif noise == 'uniform':
                v += random_state.uniform(low=-1, high=1, size=np.shape(v)) * noise_multiplier
        
            return v
        
        super().__init__(func=func, name=name, **kwargs)
        # Sets self.value to func evaluation. 
        

class SynImageDetector(ArraySynSignal):
    """
    Simulates an area detector by returning an image from file.  
    """
    def __init__(self, name, imPath, ext='.tif', **kwargs):
        self.__name__ = name
        self.im_path = Path(imPath)
        if not os.path.exists(self.im_path):
            raise FileNotFoundError
        
        def func():
            """Return np.ndarray with image data from specified path
            """
            if os.path.isfile(self.im_path):
                print('file found')
                image = fabio.open(self.im_path)
                return np.array(image.data)
            elif os.path.isdir(self.im_path):
                print('path found')
                ims = list(self.im_path.glob('*'+ext))
                i = random.randint(0,len(ims))
                image = fabio.open(ims[i])

                return np.array(image.data)

        super().__init__(func=func, name=name, **kwargs)

class SynXspress3(SynSignal):
    """
    Simulates Xspress3 Energy Discerning detector
    """
    def __init__(self, name, **kwargs):
        self.__name__ = name

        def func():
            return 1

        super(SynXspress3, self).__init__(func=func, name=name, **kwargs)