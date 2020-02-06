"""
Callbacks for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.callbacks import CallbackBase

class debugCB(CallbackBase):
    """For debugging documents.  Spits everything to console.
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

        
def doc_contents(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key + ' ==========================')
    for k, v in doc.items():
        print(f"\t{k}\t{v}")