# -*- coding: utf-8 -*-
"""
Tests for hitp simulation classes

@author: RTK
"""

import unittest

class HiTpSimTests(unittest.TestCase):
    def test__create(self):
        """
        Test isntantiation of hitp sim classes
        """
        from ssrltools.sim.hitp import SynHiTpStage, SynHiTpDet
        
        stg = SynHiTpStage(prefix='simBL:', name='SynStage')
        det = SynHiTpDet('SynDet', stg.stage_x, stg.stage_y)

if __name__ == '__main__':
    unittest.main()