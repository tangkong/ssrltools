# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 15:43:38 2019

@author: roberttk
"""

import sys

from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import install_kicker

print('initializing RunEngine')
from bluesky import RunEngine
RE = RunEngine({})
    
# install kickers, callbacks
from ssrltools.callbacks import _doc_contents, _debugCB
bec = BestEffortCallback()
bec_UID = RE.subscribe(bec)
# Debugging callbacks
#ownCB_UID = RE.subscribe(debugCB())
#cont_UID = RE.subscribe(doc_contents)

# install_kicker()

# Set up data storage
import databroker
from databroker import Broker # has issues with Cython imagecodecs?...
db = Broker.named('mongoConfig-h5')
# install sentinels
#databroker.assets.utils.install_sentinels(db.reg.config, version=1)
db_UID = RE.subscribe(db.insert)

import matplotlib.pyplot as plt
plt.ion()

# Basic detector simulations
from ophyd.sim import hw
hw = hw()
det = hw.det
motor = hw.motor
motor1 = hw.motor1
motor2 = hw.motor2
det1 = hw.det1
det2 = hw.det2
from bluesky.plans import scan, count
from bluesky.callbacks.mpl_plotting import LivePlot

dets = [det1, det2]

# ========================================================================
# Try plotting some stuff
if True:
    print('Attempting LivePlot, basic plotting')    
    RE(scan([det], motor, -5, 5, 10), LivePlot('det', 'motor'))

    # Plot multiple detectors
    dets = [det1, det2]
    RE(count(dets))


# ========================================================================
# Work with custom callbacks
if False:
    RE.unsubscribe(bec_UID)
    
    from ssrltools.callbacks import debugCB
    
    ownCB_uid = RE.subscribe(debugCB())
    RE(count(dets))


# ========================================================================
# Look at adaptive feedback plans, likely best way to incorporate active search
if False:
    from bluesky.plans import adaptive_scan
    print('running adaptive scan test')
    RE(adaptive_scan([det], 'det', motor,
                 start=-15.0,
                 stop=15.0,
                 min_step=0.01,
                 max_step=5.0,
                 target_delta=.05,
                 backstep=True), LivePlot('det', 'motor'))
    
    
# =============================================================================
# Play with Msg objects
if False:
    from ssrltools.plans import stub_plan
    print('running stub plan')
    RE(stub_plan([det], motor))
    
# =============================================================================
# Play array simulator
if False:
    from ssrltools.sim import ArraySynGauss
    
    # Currently works with mongoDB, but not sql.  Can't bind value field
    # Document format more flexible
    areaDet = ArraySynGauss('areaDet', motor1, 'motor1', motor2, 
                        'motor2', center1=0, center2=0, Imax=5)
    
    # class SpotSim(Device):
    #     img = ArraySynGauss('areaDet', motor1, 'motor1', motor2, 
    #                     'motor2', center1=0, center2=0, Imax=5)
        
    #     def collect_asset_docs(`self):
    #         yield from self.img.collect_asset_docs()

    #     def trigger(self):
    #         return self.img.trigger()
        
    #     def read(self):
    #         return self.img.read()
    
    #spot = SpotSim('mini:dot', name='spot')
    
    RE(count([areaDet]))
    
    from ssrltools.plans import stub_plan
    #print('running stub plan')
    #RE(stub_plan([areaDet], motor))
    #hdr = db[-1].table(fill=True)

# Test meshcirc ================================================================
if False:
    from ssrltools.plans import meshcirc
    RE(meshcirc([det], motor1, 1, 10, 10, motor2, 1, 10, 10, 7))

if False:
    hdr = db[-1].table(fill=True)

# Test Simulated image detector, loading images then reading them back
if False: 
    from ssrltools.sim import SynImageDetector as SIDet
    imPath = 'C:\\Users\\roberttk\\Desktop\\SLAC_RA\\bluesky-dev\\fstore\\k3_012918_1_24x24_t45b_0248.tif'
    det = SIDet('imDet', imPath)

    RE(count([det]))

# Test caproto IOC, connect to IOC and try to read image
if False:
    from ssrltools.devices.dexela import DexelaDet15 as DEXdet

    det = DEXdet('simBL:dexela', name='dexela')

    RE(count([det]))