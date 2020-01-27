"""
Test python classes, for personal edification.

@author: RTK
"""

import unittest

class pythonTests(unittest.TestCase):

    def test_namespace(self):
        """
        Figure out if importing from own packages works
        """
        
        from ssrltools.sim import testModule
        print(testModule())
        
        self.assertEqual(9, testModule())
                
    def test_super(self):
        """
        Test super with multiple layers of inheritance

        Returns
        -------
        None.

        """

        class OriginClass():
            def daMethod(self):
                return 4

        class Child1(OriginClass):
            pass

        class FinalChild(Child1):
            def daMethod(self):
                super().daMethod()
                
        CC = FinalChild()
        
        self.assertEqual(CC.daMethod(), 4)

    def test_sig_inherit(self):
        """
        Test method/property overwriting properties of Signal/EpicsSignal 
        classes.  
        """
        
        class Sig():
            def __init__(self):
                self._readback = 0 # Initial value
            def get(self):
                return self._readback
            
            @property
            def value(self):
                return self.get()
            
            @value.setter
            def value(self, value):
                # Set _readback value 
                self._readback = value
            
        class ESBase(Sig):
            def __init__(self):
                super().__init__()
                            
            def get(self):
                ret = super().get()
                return 40
            def read(self):
                return { 'device_name': {'value': self.value,
                                         'timestamp': 10101010 }}
        
        ES = ESBase()
        self.assertEqual(ES.read()['device_name']['value'], 40)
        # even though ESBase does not have a value method, takes Sigs. 
        # Now Sig.value calls .get(), but takes from ESBase
        
        # setting self.value affects self._readback
        ES.value = 333
        # no .value() in ES, calls Sig.value() -> calls self.get=ESBase.get -> returns 40
        self.assertEqual(ES.value, 40) 
        self.assertEqual(ES._readback, 333)
        # self.value routes to self.get()
        self.assertEqual(ES.read()['device_name']['value'], 40)
        
        self.assertEqual(ES.get(), 40)
        
    
    def test_pyplot(self):
        
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

if __name__ == '__main__':
    unittest.main()