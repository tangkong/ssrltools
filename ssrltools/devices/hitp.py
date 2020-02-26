import bluesky.plan_stubs as bps
from ophyd import EpicsMotor, Device, Component as Cpt
from ophyd import EpicsSignalRO
from ophyd.sim import SynAxis, SynSignal
import pandas as pd 
from pathlib import Path

from numpy import random


class HiTpStage(Device):
    """
    Combined class for HiTp stage.  
    * Gathers stage and plate motors
    * Stores sample locations

    Simplifies task of aligning and remembering sample positions
    Instantiate with: HiTpStage('simBL', name='HS')
    """
    #stage x, y
    stage_x = Cpt(EpicsMotor, ':suffix', kind='hinted')
    stage_y = Cpt(EpicsMotor, ':suffix', kind='hinted')

    # plate vert adjust motor 1, 2
    plate_x = Cpt(EpicsMotor, ':suffix')
    plate_y = Cpt(EpicsMotor, ':suffix')

    theta = Cpt(EpicsMotor, ':suffix')

    # Laser Range finder?... 
    height = Cpt(EpicsSignalRO, ':suffix')

    # TODO: Figure out how to access component names within the class 
    # Until then, hard code things I guess
        
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
        
        self.center = { 'stage_x': 0,
                        'stage_y': 0,
                        'plate_x': 0, #self.plate_x.position,
                        'plate_y': 0, #self.plate_y.position,
                        'theta':   0 #self.theta.position
                      }
        super().__init__(*args, **kwargs)

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

    def set_all_vert_theta(self):
        """
        After aligning plate and theta, set all sample locations to have
        same plate_x, plate_y, theta.
        """
        for i in range(len(self.sample_locs)):
            self.sample_locs[i]['theta'] = self.theta.position
            self.sample_locs[i]['plate_x'] = self.plate_x.position
            self.sample_locs[i]['plate_y'] = self.plate_y.position


    def sample_loc_list(self, index=None):
        """
        Returns motor-location list pairs for consumption by bp.list_scan
        motor1, [m1_loc1, m1_loc2, ...], 
        motor2, [m2_loc1, m2_loc2, ...], ...

        usage: 
            stage = HiTpStage('prefix', name='name')
            RE( bp.list_scan(*stage.sample_loc_list()) )

            OR

            RE( bps.mv(*stage.sample_loc_list(index=1)) )
        """
        result = []

        if not index:
            loc_lists = {}
            for name in self.component_names:
                loc_lists[name] = []

            for pos in self.sample_locs.values():
                for motor in pos.keys():
                    loc_lists[motor].append(pos[motor])

            # format as * unpackable args
            for name in self.component_names:
                result.append(getattr(self, name))
                result.append(loc_lists[name])

            return result

        elif index is 'center':
            for key, val in self.center.items():
                result.append(getattr(self, key)) # grab motor instance
                result.append(val) # return value

            return result

        elif isinstance(index, (int, list)): 
            # return locations from chosen indexes.  Also catches int case
            indices = list(index)
            for i in indices:
                for key, val in self.sample_locs[i].items():
                    result.append(getattr(self, key))
                    result.append(val)

            return result