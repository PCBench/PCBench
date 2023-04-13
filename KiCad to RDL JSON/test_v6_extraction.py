from collections import defaultdict
import json
import kicad_pcb_v6nc
import numpy as np
import os

print("\nTrying modified parser\n"+'-'*80)
pcb = kicad_pcb_v6nc.KicadPCB.load(os.path.join(
    os.path.dirname(__file__),'..','kicad files/12_24_boost_converter.kicad_pcb'))

# A footprint corresponds to a component, like
# a capacitor. For some reason, things are 
# singular that really shouldn't be.
footprints =pcb.footprint

# my_dict = {net_name: [[at1x,at1y][at2x,at2y]]}
my_dict = defaultdict(list)
for item in footprints:
    component_loc = item.at
    # print(component_loc)
    pads = item.pad
    for pad in pads:    # most components have 1 or more pad
        # print(f"{pad.net[1]}: {np.array(pad.at) + np.array(component_loc)}")
        coords = np.array(pad.at) + np.array(component_loc)
        
        my_dict[pad.net[1].strip("\"")].append(coords.tolist())

print(my_dict)
f = open('test_locs.json','w')
json.dump(my_dict,f)

