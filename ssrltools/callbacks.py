"""
Callbacks for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.callbacks import CallbackBase

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

        
def _doc_contents(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key + ' ==========================')
    for k, v in doc.items():
        print(f"\t{k}\t{v}")