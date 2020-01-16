# -*- coding: utf-8 -*-
"""
Tests for bluesky, ophyd packages, some integration

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
        
    def test_bsRE(self):
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

    def test_ophyd_sim(self):
        """
        Test ophyd import and basic sim functionality
        """
        from ophyd.sim import det, motor

        self.assertEqual(det.get(), 1.0)
        det.put(5)
        self.assertEqual(det.get(), 5.0)

        self.assertEqual(motor.read()['motor']['value'], 0)
        motor.set(9.5)
        self.assertEqual(motor.read()['motor']['value'], 9.5)

    def test_count_sim_det(self):
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
# Run unit tests

if __name__ == '__main__':
    unittest.main()