from ophyd.areadetector.plugins import PluginBase
import time as ttime
import logging
import uuid

from pathlib import PurePath
from .utils import makedirs

from collections import OrderedDict
import itertools

import h5py

from ophyd.areadetector import (DetectorBase, CamBase,
                                EpicsSignalWithRBV as SignalWithRBV)
from ophyd import (Signal, EpicsSignal, EpicsSignalRO, DerivedSignal)

from ophyd import (Device, Component as Cpt, FormattedComponent as FC,
                   DynamicDeviceComponent as DDC)
from ophyd.areadetector.plugins import PluginBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase

from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector import ADBase
from ophyd.device import (BlueskyInterface, Staged)
from ophyd.sim import NullStatus  # TODO: remove after complete/collect are defined

from hxntools.detectors.xspress3 import (XspressTrigger, Xspress3Detector, 
                                        Xspress3Channel, Xspress3FileStore)

from collections import deque

logger = logging.getLogger(__name__)

"""
Modules taken from HXN, CSX beamlines at NSLS-II.  
Repackaged and customized here for use at SSRL.
"""

class SSRLXspress3Detector(XspressTrigger, Xspress3Detector):
    roi_data = Cpt(PluginBase, 'ROIDATA:')
    channel1 = Cpt(Xspress3Channel, 'C1_', channel_num=1, read_attrs=['rois'])
    channel2 = Cpt(Xspress3Channel, 'C2_', channel_num=2, read_attrs=['rois'])
    channel3 = Cpt(Xspress3Channel, 'C3_', channel_num=3, read_attrs=['rois'])
    channel4 = Cpt(Xspress3Channel, 'C4_', channel_num=4, read_attrs=['rois'])

    hdf5 = Cpt(Xspress3FileStore, 'HDF5:',
               read_path_template='/ssrl/beamline/data/xspress/%Y/%m/%d/',
               root='/ssrl/beamline/data/',
               write_path_template='/ssrl/beamline/data/xspress/%Y/%m/%d/',
               )

    def __init__(self, prefix, *, configuration_attrs=None, read_attrs=None,
                 **kwargs): 
        if configuration_attrs is None:
            configuration_attrs = ['external_trig', 'total_points',
                                   'spectra_per_point', 'settings',
                                   'rewindable']
        if read_attrs is None:
            read_attrs = ['channel1', 'channel2', 'channel3', 'channel4', 'hdf5']
        super().__init__(prefix, configuration_attrs=configuration_attrs,
                         read_attrs=read_attrs, **kwargs)

        self._asset_docs_cache = deque()
        self._datum_counter = None

    def stop(self):
        # .stop() walks back to Device class... which does not return anything
        ret = super().stop()
        self.hdf5.stop()
        return ret

    def stage(self):
        if self.spectra_per_point.get() != 1:
            raise NotImplementedError(
                "multi spectra per point not supported yet")
        ret = super().stage()
        self._datum_counter = itertools.count()
        return ret

    def unstage(self):
        self.settings.trigger_mode.put(0)  # 'Software'
        super().unstage()
        self._datum_counter = None

    def complete(self, *args, **kwargs):
        for resource in self.hdf5._asset_docs_cache:
            self._asset_docs_cache.append(('resource', resource[1]))

        self._datum_ids = []

        num_frames = self.hdf5.num_captured.get()

        for frame_num in range(num_frames):
            for channel_num in self.hdf5.channels:  # Channels (1, 2, 3, 4) as of 12/16/2019
                datum_id = '{}/{}'.format(self.hdf5._resource_uid, next(self._datum_counter))
                datum = {'resource': self.hdf5._resource_uid,
                         'datum_kwargs': {'frame': frame_num,
                                          'channel': channel_num},
                         'datum_id': datum_id}
                self._asset_docs_cache.append(('datum', datum))
                self._datum_ids.append(datum_id)

        return NullStatus()

    def collect(self):
        now = ttime.time()
        for datum_id in self._datum_ids:
            data = {self.name: datum_id}
            yield {'data': data,
                   'timestamps': {key: now for key in data}, 'time': now,  # TODO: use the proper timestams from the mono start and stop times
                   'filled': {key: False for key in data}}

    def collect_asset_docs(self):
        items = list(self._asset_docs_cache)
        self._asset_docs_cache.clear()
        for item in items:
            yield item