# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 13:38:46 2019

@author: RTK
"""

import unittest

class BSTests(unittest.TestCase):
    def setupRE(self):
        """
        Set up and return RunEngine with basic callback for unit testing
        Also subscribe it to basic callbacks
        """
    
        try:
            RE
        except NameError as e: 
            print('RE not configured, importing now')
            print(e)
            from bluesky import RunEngine
            
            RE = RunEngine({})    
        
        from bluesky.callbacks.best_effort import BestEffortCallback
        bec = BestEffortCallback()
        RE.subscribe(bec)
        
        from databroker import Broker
        db = Broker.named('temp')
        RE.subscribe(db.insert)
        
        
        return RE, db
        
    def test1_bsRE(self):
        """
        Test if we can instantiate Bluesky
        """
        print('Testing Bluesky RunEngine instatiation')
        
        try:
            RE
        except NameError as e: 
            print('RE not configured, importing now')
            print(e)
            from bluesky import RunEngine
            
            RE = RunEngine({})    
        
        print(type(RE))
        
        # establish callbacks and basic data storage
        from bluesky.callbacks.best_effort import BestEffortCallback
        bec = BestEffortCallback()
        RE.subscribe(bec)
        
        from databroker import Broker
        db = Broker.named('temp')
        RE.subscribe(db.insert)
        
        # Read a detector and output 
        from ophyd.sim import det1
        from bluesky.plans import count
        RE(count([det1]))
        
        # Assert RE counted value of 5 from det1
        head = db[-1]
        val = head.table()['det1'][1]
        
        self.assertEqual(val, 5.0)
        
        
    def test2_bsRE(self):
        """
        Test instatiation and passing of RE
        """
        
        RE, db = self.setupRE()
        from ophyd.sim import det1
        from bluesky.plans import count
        RE(count([det1]))
        
        # Assert RE counted value of 5 from det1
        head = db[-1]
        val = head.table()['det1'][1]
        
        self.assertEqual(val, 5.0)


class pythonTests(unittest.TestCase):

    def testNamespace(self):
        """
        Figure out if importing from own packages works
        """
        
        from ssrltools.customSim import testModule
        print(testModule())
        
        self.assertEqual(9, testModule())
                
    def testSuper(self):
        """
        Test super with multiple layers of inheritance

        Returns
        -------
        None.

        """
        
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  daMethod Testing')
        class OriginClass():
            def daMethod(self):
                print('OriginClass Method')
                
        class Child1(OriginClass):
            pass

        class FinalChild(Child1):
            def daMethod(self):
                super().daMethod()
                print('FinalChild method')
                
        CC = FinalChild()
        CC.daMethod()
        
        
        self.assertEqual(9, 9)
        
        
        
    def testSignalInheritance(self):
        """
        Test method/property overwriting properties of Signal/EpicsSignal 
        classes.  
        """
        
        
        class Sig():
            def __init__(self):
                self._readback = 0 # Initial value
                print('Sig init called')
            def get(self):
                return self._readback
            
            @property
            def value(self):
                print('Sig value method')
                return self.get()
            
            @value.setter
            def value(self, value):
                # Set _readback value 
                self._readback = value
            
        class ESBase(Sig):
            def __init__(self):
                super().__init__()
                            
            def get(self):
                print('ESBase get method')
                ret = super().get()
                return 40
            def read(self):
                return { 'device_name': {'value': self.value,
                                         'timestamp': 10101010 }}
            
        class AS(ESBase):
            pass
        ES = ESBase()
        print(ES.read())
        # even though ESBase does not have a value method, takes Sigs. 
        # Now Sig.value calls .get(), but takes from ESBase
        
        print('-----------------')
        ES.value = 333
        print(ES.value)
        print(ES._readback)
        print(ES.read())
        
        print('-----------------')
        print(ES.get())
        
    
    def testPyplot(self):
        
        import matplotlib.pyplot as plt
        import numpy as np
        m1 = 0 # Location of frame
        m2 = 0
        size = 5
        pt_density = 20
        Imax = 5
        center1 = 0
        center2 = 0
        sigma1 = 1
        sigma2 = 2
        
        fig, ax = plt.subplots(1,1,figsize=(10,10))
        
        x = np.linspace(m1-size/2, m1+size/2, pt_density)
        y = np.linspace(m2-size/2, m2+size/2, pt_density)
    
        xx, yy = np.meshgrid(x, y, sparse=True)
                
        v = Imax * np.exp(-( ((xx-center1)**2 / (2*sigma1**2)) +  \
                             ((yy-center2)**2 / (2*sigma2**2)) ))
        
        im = ax.imshow(v)
        cb = plt.colorbar(im)
        
# Run unit tests

if __name__ == '__main__':
    unittest.main()