"""
Callbacks for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.callbacks import CallbackBase

class own_CB(CallbackBase):
    def start(self, doc):
        print('>>> start of run <<<  \n')
    
    def event(self, doc):
        #print('name: {}'.format(name))
        print('>>> data: {} <<< '.format(doc['data']))
        
    def stop(self, doc):
        print('>>> run completed <<<')
        
def doc_contents(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key + ' ==========================')
    for k, v in doc.items():
        print(f"\t{k}\t{v}")