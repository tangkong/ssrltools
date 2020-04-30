# Basic HiTp Operation outline

# Mount all hardware 

# Activate Environment

# Load User settings
from ssrltools.utils import setup_user_metadata
md = setup_user_metadata()
# user, sample-ID, 

# Test staging behavior of all hardware
## Signal checks
print(f'x position: {stage.stage_x.value}, y position: {stage.stage_y.value}')
print(f'theta: {stage.theta.value}')
print(f'laser range finder: {lrf.value}')

## Basic alignment (table height)

## Calibration (LaB6, range finder)


# Load sample

# Level sample
## print out heights of each location

## Leveling plan
RE(bps.mv(stage.center))
level_stage_single(lrf, stage.plate_x, stage.stage_x, -85, 85)
level_stage_single(lrf, stage.plate_y, stage.stage_y, 58, -58)


# Confirm sample locations
## Move to various samples
RE( bps.mv(stage.sample_loc_list(index=3)), 
    purpose='setup', operator='roberttk') 

## Update sample locations if necessary
# Assuming this sample is index 1
RE( bps.mv(stage.stage_x, 4, stage.stage_y, 5), 
    purpose='setup', operator='roberttk')
stage.save_sample_loc(5) # Saves current location to index 5

# Measure points on library
## Add metadata to plan
RE( list_scan([detector], stage.sample_loc_list(), # or stage.sapmle_loc_list(index=[1,3,4,5])
            sample_id='library A', purpose='measurement', operator='roberttk') )
## list_scan([detector], stage.sample_loc_list())
# Adaptive scan on library (picking points with highest priority?)
## Best way to hook into plan?  Passing dictionaries?

## ??? TBD With Jean

# Examine data.
db[-1].table()
db[-2].table()

headers = db(plan_name='list_scan')
headers = db(operator='roberttk')
headers = db('keyword')  # Searches start documents for keywords in mongo docs

# save thing
hdr = db[-1].table()
hdr.table().to_csv('filepath')
## mongo browser?
## Search database