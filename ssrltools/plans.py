"""
Plans for use at SSRL beamlines running Bluesky

.. autosummary::


"""

import bluesky.plan_stubs as bps
import bluesky.plans as bp
from bluesky.utils import Msg
from bluesky import preprocessors as bpp
from bluesky import plan_patterns

from collections import OrderedDict
import numpy as np
import datetime
import logging


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
        return (yield from bp.count(detectors))
    
    
    
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


def meshcirc(detectors, motor1, s1, f1, int1, mot2, s2, f2, int2, 
            radius, md=None):
    """
    Scan points in a mesh, including only coordinates inside the radius
    Hooks bluesky.plans.grid_scan
    motor1: 
    s1 = start
    f = end
    int = number
    """
    # Verification (check non-negative, motors are motors, non-zero steps?)
    # Basic plan logic
    motor_args = list([motor1, s1, f1, int1, mot2, s2, f2, int2, False])

    # metadata addition
    _md = {'radius': radius}
    _md.update(md or {})

    # inject logic via per_step 
    def per_step_fn(detectors, step, pos_cache):
        """
        has signature of bps.one_nd_step, but with added logic of skipping 
        a point if it is outside of 
        """
        vals = list(step.values())
        pos_rad = sum(map(lambda x: x*x , list(vals))) # calculate radius^2
        pt_past_radius = (pos_rad > radius*radius)
        if pt_past_radius: # condition 
            pass
        else: # run normal scan
            yield from bps.one_nd_step(detectors, step, pos_cache)
        
    # plan logic
    return (yield from bp.grid_scan(detectors, *motor_args, 
                                    per_step=per_step_fn, md=_md))

def mesh_grid_circ(detectors, mot1, s1, f1, int1, mot2, s2, f2, int2, 
            radius, pin=None, partial=0, md=None):
    """
    Scan points in a mesh, including only coordinates inside the radius.
    Grid is aligned inside the circular boundary based on pin variable. If pin 
    argument is not provided, take the current positions of motor1, motor2 to be
    on a sample. 

    Currently has no way of correcting for rotation of grid.

    Hooks bluesky.plans.grid_scan
    detectors: list of detectors to count at each point

    motor1: 
    s1 = start 
    f1 = end
    int2 = spacing between points along motor1 axis

    motor2: 
    s2 = start 
    f2 = end
    int2 = spacing between points along motor1 axis

    radius = radius from the center point (f1-s1, f2-s2)
    """
    # Verification (check non-negative, motors are motors, non-zero steps?)
    # Basic plan logic
    ## Define new bounds
    if not pin: # no pinning tuple provided
        pin = (mot1.position, mot2.position) 

    ## subtract fraction of interval to account for edges
    s1_new = np.arange(pin[0], s1-int1/2, -int1)[-1]
    f1_new = np.arange(pin[0], f1+int1/2, int1)[-1]

    s2_new = np.arange(pin[1], s2-int2/2, -int2)[-1]
    f2_new = np.arange(pin[1], f2+int2/2, int2)[-1]

    ## add half of interval to include endpoints if interval is perfect
    num1 = len(np.arange(s1_new, f1_new+int1/2, int1))
    num2 = len(np.arange(s2_new, f2_new+int2/2, int2))
    
    center = (s1+(f1-s1)/2, s2+(f2-s2)/2)

    motor_args = list([mot1, s1_new, f1_new, num1, 
                        mot2, s2_new, f2_new, num2, False])

    # metadata addition
    _md = {'radius': radius}
    _md.update(md or {})

    # inject logic via per_step 
    def per_step_fn(detectors, step, pos_cache):
        """
        has signature of bps.one_nd_step, but with added logic of skipping 
        a point if it is outside of provided radius
        """
        vals = list(step.values())
        pos_rad = sum([(x-y)**2 for x, y in zip(vals, center)]) # calculate radius^2
        pt_past_radius = (pos_rad > radius*radius)
        if pt_past_radius: # condition 
            pass
        else: # run normal scan
            yield from bps.one_nd_step(detectors, step, pos_cache)
        
    # plan logic
    return (yield from bp.grid_scan(detectors, *motor_args, 
                                    per_step=per_step_fn, md=_md))

def nscan(detectors, *motor_sets, num=11, per_step=None, md=None):
    """
    Scan over ``n`` variables moved together, each in equally spaced steps.
    Adapted from Pete Jemian's apstools

    PARAMETERS

    detectors : list
        list of 'readable' objects
    motor_sets : list
        sequence of one or more groups of: motor, start, finish
    motor : object
        any 'settable' object (motor, temp controller, etc.)
    start : float
        starting position of motor
    finish : float
        ending position of motor
    num : int
        number of steps (default = 11)
    per_step : callable, optional
        hook for customizing action of inner loop (messages per step)
        Expected signature: ``f(detectors, step_cache, pos_cache)``
    md : dict, optional
        metadata
    
    See the `nscan()` example in a Jupyter notebook:
    https://github.com/BCDA-APS/apstools/blob/master/docs/source/resources/demo_nscan.ipynb
    """
    def take_n_at_a_time(args, n=2):
        yield from zip(*[iter(args)]*n)
        
    if len(motor_sets) < 3:
        raise ValueError("must provide at least one movable")
    if len(motor_sets) % 3 > 0:
        raise ValueError("must provide sets of movable, start, finish")

    motors = OrderedDict()
    for m, s, f in take_n_at_a_time(motor_sets, n=3):
        if not isinstance(s, (int, float)):
            msg = "start={} ({}): is not a number".format(s, type(s))
            raise ValueError(msg)
        if not isinstance(f, (int, float)):
            msg = "finish={} ({}): is not a number".format(f, type(f))
            raise ValueError(msg)
        motors[m.name] = dict(motor=m, start=s, finish=f, 
                              steps=np.linspace(start=s, stop=f, num=num))

    _md = {'detectors': [det.name for det in detectors],
           'motors': [m for m in motors.keys()],
           'num_points': num,
           'num_intervals': num - 1,
           'plan_args': {'detectors': list(map(repr, detectors)), 
                         'num': num,
                         'motors': repr(motor_sets),
                         'per_step': repr(per_step)},
           'plan_name': 'nscan',
           'plan_pattern': 'linspace',
           'hints': {},
           'iso8601': datetime.datetime.now(),
           }
    _md.update(md or {})

    try:
        m = list(motors.keys())[0]
        dimensions = [(motors[m]["motor"].hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        _md['hints'].setdefault('dimensions', dimensions)

    if per_step is None:
        per_step = bps.one_nd_step

    @bpp.stage_decorator(list(detectors) 
                         + [m["motor"] for m in motors.values()])
    @bpp.run_decorator(md=_md)
    def inner_scan():
        for step in range(num):
            step_cache, pos_cache = {}, {}
            for m in motors.values():
                next_pos = m["steps"][step]
                m = m["motor"]
                pos_cache[m] = m.read()[m.name]["value"]
                step_cache[m] = next_pos
            yield from per_step(detectors, step_cache, pos_cache)

    return (yield from inner_scan())


def level_stage_single(distdet, dist_motor, horz_motor, point1, point2):
        """
        Plan for leveling hitp stage.  
        Assumes:
            dist_motor is at horz_motor=point1
            point1 to point2 are on horz_motor axis
            stage is currently on horz_motor axis
            distdet is a simple signal.  

        Usage: 
            bps.mv(stage.center)
            level_stage_single(stage.height, stage.plate_y, stage.stage_y, 
                                            pt1, pt2)
            bps.mv(stage.center)
            level_stage_single(stage.height, stage.plate_x, stage.stage_x,
                                            pt1, pt2)
        """

        # Conversion from voltage to distance
        def v2mm(V):
            """ Convert laser range finder V to mm (calib w/ ims motor) """
            return V*0.46782

        # Iteration parameters
        thresh = 0.01
        step_size = 5.0
        iter_limit = 20
        
        for thresh_mult in [20, 10, 5, 2]: # various steps, coarse and fine
            # Grab initial values
            yield from bps.mv(horz_motor, point2)
            # If actual epics detector, need to trigger and read?
            # Else can just get value
            distdet.read()
            v2 = v2mm(distdet.read()[distdet.name]['value'])
            yield from bps.mv(horz_motor, point1)
            distdet.read()
            v1 = v2mm(distdet.read()[distdet.name]['value'])

            # Coarse adjustment, move in large steps
            iter_cnt = 0
            while ((np.abs(v2 - v1) > (thresh * thresh_mult)) 
                    and (iter_cnt < iter_limit)):

                if v1 > v2: # if motor closer to range finder
                    # LRF signal increases as pico pushes +z
                    # LRF measures height from bottom
                    yield from bps.mvr(dist_motor, -step_size*thresh_mult/2) # raise motor
                else: 
                    yield from bps.mvr(dist_motor, step_size*thresh_mult/2)

                # re-measure points for iteration condition
                yield from bps.mv(horz_motor, point1)
                distdet.read()
                v1 = v2mm(distdet.read()[distdet.name]['value'])

                iter_cnt += 1
            print(f'{iter_cnt} iters for thresh_mult={thresh_mult}')