import os
import matplotlib

from IPython import get_ipython
import matplotlib.pyplot

from ophyd import Device, Component, EpicsSignal
from ophyd.signal import EpicsSignalBase
from ophyd.areadetector.filestore_mixins import resource_factory
import uuid
import os
from pathlib import Path
import numpy as np


# Set up a RunEngine and use metadata backed by a mongo databse l.
from bluesky import RunEngine
from ssrltools.utils import PersistentDict
RE = RunEngine({})
RE.md = PersistentDict(str(Path(
        '~\\Desktop\\SLAC_RA\\bluesky-dev\\ssrltools\\fstore\\tmp').expanduser()))

# Set up SupplementalData.
from bluesky import SupplementalData
sd = SupplementalData()
RE.preprocessors.append(sd)

# Set up a Broker.
import databroker
# grab configuration from ~/mongoConfig.yml
db = databroker.Broker.named('mongoConfig')
# install sentinels
try:
    databroker.assets.utils.install_sentinels(db.reg.config, version=1)
except RuntimeError as e:
    # Sentinel already installed
    print('sentinel already installed')

# and subscribe it to the RunEngine
RE.subscribe(db.insert)

# Add a progress bar.
# from bluesky.utils import ProgressBarManager
# pbar_manager = ProgressBarManager()
# RE.waiting_hook = pbar_manager

# Register bluesky IPython magics.
# from bluesky.magics import BlueskyMagics
# get_ipython().register_magics(BlueskyMagics)

# Set up the BestEffortCallback.
from bluesky.callbacks.best_effort import BestEffortCallback
bec = BestEffortCallback()
RE.subscribe(bec)
peaks = bec.peaks

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
# from bluesky.utils import install_nb_kicker
# install_nb_kicker()

# convenience imports
# some of the * imports are for 'back-compatibility' of a sort -- we have
# taught BL staff to expect LiveTable and LivePlot etc. to be in their
# namespace
import numpy as np

import bluesky.callbacks
from bluesky.callbacks import *

import bluesky.plans
from bluesky.plans import *

import bluesky.plan_stubs
from bluesky.plan_stubs import *

import bluesky.preprocessors
import bluesky.simulators
from bluesky.simulators import *
