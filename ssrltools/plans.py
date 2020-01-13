"""
Plans for use at SSRL beamlines running Bluesky

.. autosummary::


"""

from bluesky.plan_stubs import mv
from bluesky.plans import count
from bluesky.utils import Msg
from bluesky import preprocessors as bpp

def ownScan(detectors, motor, start, stop, num_steps, *, md=None):
    # Do basic input checking, verification
    if num_steps < 20:
        num_steps = 20
    
    # Standard metadata collection, organization
    _md = {'detectors': [det.name for det in detectors],
        'motors': [motor.name],
        'plan_args': {'detectors': list(map(repr, detectors)),
                      'motor': repr(motor)},
        'plan_name': 'ownScan',
        'hints': {} }  
        
    # adds metadata from md if passed through
    _md.update(md or {})  
    
    # grab dimensions, add their names as hints to metadata
    try:
        dimensions = [(motor.hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        # _md['hints'] is a dictionary
        # if 'dimensions' exists, 
        _md['hints'].setdefault('dimensions', dimensions)
    
    
    # Wrap inner plan in decorators, then define inner plan
    @bpp.stage_decorator(detectors)
    @bpp.run_decorator(md=_md)
    def inner_scan():
        return (yield from count(detectors))
    
    
    
    return (yield from inner_scan())

def stub_plan(detectors, motor):
    def core():
        print('---open_run--------------------------------')
        yield Msg('open_run')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        print('---create--------------------------------')
        yield Msg('create', name='stub_plan')
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
        for det in detectors:
            print(f'    >>> trigger:')
            yield Msg('trigger', det)
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            print(f'    >>> read:')
            readOut = yield Msg('read', det)
            print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
            print(readOut)
        print('---save--------------------------------')
        yield Msg('save')        
        print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
    return (yield from core())