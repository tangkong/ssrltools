"""
Callbacks for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.callbacks import CallbackBase
from collections import OrderedDict
from datetime import datetime
import getpass
import logging
import os
import socket
import time

logger = logging.getLogger(__name__)
print(__name__)
logger.debug('test debug')

class _debugCB(CallbackBase):
    """For debugging documents.  Spits everything to console.
    Need to instantiate before subscribing of inserting into RunEngine
    RE(count([det]), _debugCB())
    """
    def start(self, doc):
        print('>>> start of run <<<  \n')
        print(doc)
        print('-----------------------\n')
    
    def event(self, doc):
        #print('name: {}'.format(name))
        print('>>> Event <<< ')
        print(doc)
        print('-----------------------\n')

    def stop(self, doc):
        print('>>> end of run <<< \n')
        print(doc)
        print('-----------------------\n')

    def descriptor(self, doc):
        print('>>> descriptor <<<')
        print(doc)
        print('-----------------------\n')

def _doc_contents(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key + ' ==========================')
    for k, v in doc.items():
        print(f"\t{k}\t{v}")


class SpecCSVCallback(CallbackBase):
    """SpecCSVCallback generate spec CSV file from data (event docs)
    write file on stop document
    """

    def __init__(self, filename=None):
        if filename is None or not os.path.exists(filename):
            now  = datetime.now()
            self.filename = datetime.strftime(now, '%Y%m%d-%H%M%S') + '.csv'
        else:
            self.filename = filename

        self.data = OrderedDict() # store everything here
        self.num_primary_data = 0
        super().__init__()
    
    def descriptor(self, doc):
        """ handle descriptor docs, prepping for scan data
        """
        logger.debug('descriptor method')
        keyset = list(doc['data_keys'].keys())
        self.data.update({k: [] for k in keyset})
        self.data.update({'seq_num': []})

    def event(self, doc):
        """ handle event documents by pulling from data keys
        """

        self.data['seq_num'].append(doc['seq_num'])
        for k in doc['data'].keys():
            self.data[k].append(doc['data'].get(k, 0))
        self.num_primary_data += 1

    def stop(self, doc):
        """ write files at the stop document trigger.  
        """
        print(self.data)
        # self.write_scan
        # prepare lines
        lines = []
        if len(self.data.keys()) > 0:
            lines.append(','.join(self.data.keys()))
            for i in range(self.num_primary_data):
                s = []
                for k in self.data.keys():
                    datum = self.data[k][i]
                    s.append(str(datum))
                
                lines.append(','.join(s))
        
        # write lines
        with open(self.filename, 'w') as f:
            f.write('\n'.join(lines))
