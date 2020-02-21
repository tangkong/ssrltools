import bluesky.plan_stubs as bps
from ophyd import EpicsMotor, Device, Component as Cpt
from ophyd.sim import SynAxis, SynSignal
import pandas as pd 
from pathlib import Path

from numpy import random


class SynHiTpStage(Device):
    """
    Combined class for HiTp stage.  
    * Gathers stage and plate motors
    * Stores sample locations

    Simplifies task of aligning and remembering sample positions
    """
    #stage x, y
    stage_x = Cpt(SynAxis, prefix=':X', name='stage_x', kind='hinted')
    stage_y = Cpt(SynAxis, prefix=':Y', name='stage_y', kind='hinted')

    # plate vert adjust motor 1, 2
    plate_x = Cpt(SynAxis, prefix=':pY', name='plate_x')
    plate_y = Cpt(SynAxis, prefix=':pX', name='plate_y')

    theta = Cpt(SynAxis, prefix=':theta', name='theta')

    # TODO: Figure out how to access component names within the class 
    # Until then, hard code things I guess
    motors = [stage_x, stage_y, plate_x, plate_y, theta]
        
    def __init__(self, *args, **kwargs):
        # Default sample location list.  Save all location information
        # Component names found in self.component_names, 
        # only accessible from self once instantiated
        
        # hard coding plate positions for now
        path177 = Path(__file__).parent / 'positions' / '177.csv'
        df = pd.read_csv(path177)
        print('loaded 177 positions')
        
        self.sample_locs = {}
        for i in range(len(df)):
            self.sample_locs[i] = { 'stage_x': df['Plate X'][i],
                                    'stage_y': df['Plate Y'][i],
                                    'plate_x': 0, #self.plate_x.position,
                                    'plate_y': 0, #self.plate_y.position,
                                    'theta':   0 #self.theta.position
                                  }
        super().__init__(*args, **kwargs)

    def sample_loc_list(self, paired=False):
        """
        Returns motor-location list pairs for consumption by bp.list_scan
        motor1, [m1_loc1, m1_loc2, ...], 
        motor2, [m2_loc1, m2_loc2, ...], ...

        Can also be formatted as tuples:
        (m1_loc1, m2_loc1, ... ), (m1_loc2, m2_loc2, ...)
        """
        loc_lists = {}
        for name in self.component_names:
            loc_lists[name] = []

        for pos in self.sample_locs.values():
            for motor in pos.keys():
                loc_lists[motor].append(pos[motor])

        # format as * unpackable args
        result = []
        for name in self.component_names:
            result.append(getattr(self, name))
            result.append(loc_lists[name])

        return result

    def sample(self, index):
        return self.sample_locs[index]

    def save_sample_loc(self, index):
        """
        Save sample location to location list
        """
        self.sample_locs[index] = { 'stage_x': self.stage_x.position,
                                    'stage_y': self.stage_y.position,
                                    'plate_x': self.plate_x.position,
                                    'plate_y': self.plate_y.position,
                                    'theta':   self.theta.position
                                  }


    def move_to_sample_plan(self, index):
        """
        Plan to move to sample index.  Pass this into the active run engine.
        """
        result = []
        for key, val in self.sample_locs[index].items():
            result.append(getattr(self, key))
            result.append(val)
        print(result)
        yield from bps.mv(*result)

class SynHiTpDet(SynSignal):
    """
    Simulated detector for HiTp simulations.  
    Returns tuple with motor positions?...
    """
    def __init__(self, name, motorx, motory, **kwargs):
        self.__name__ = name

        def func():
            """
            Returns random int from 1-10
            """
            return random.randint(1, 10)

        super().__init__(func=func, name=name, **kwargs)

    def trigger(self):
        print('triggered')
        ret = super().trigger()
        return ret

def _per_grid_step_thresh(threshold, radius):
    """
    Hook function for dumb threshold tests
    .... Moves before triggering.  So if you have a threshold set, 
        once the threshold has caused it to pass, it won't trigger again, 
        causing all to pass. 

        this is probably desirable behavior, as the detector doesn't change  
        before you move to the position
    """  
    def per_step_fn(detectors, step, pos_cache):
        vals = list(step.values())
        pos_rad = sum(map(lambda x: x*x, list(vals)))
        pt_past_radius = (pos_rad > radius*radius)
        over_thresh = False
        for det in detectors:
            if det.value > threshold:
                #print(f'threshold greater than allowed: {det.value}')
                over_thresh = True

        if pt_past_radius or over_thresh:
            pass
        else: 
            yield from bps.one_nd_step(detectors, step, pos_cache)

    return per_step_fn