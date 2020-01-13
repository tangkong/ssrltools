"""
Callbacks for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.callbacks import CallbackBase

class ownCB(CallbackBase):
    def start(self, doc):
        print('start of run')
    
    def event(self, doc):
        #print('name: {}'.format(name))
        print('data: {}'.format(doc['data']))
        
    def stop(self, doc):
        print('run completed')
        