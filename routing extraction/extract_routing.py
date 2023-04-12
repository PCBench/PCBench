from collections import defaultdict
import json
import re
import kicad_pcb_v6nc
import numpy as np
import os
import logging

from sexp_parser import Sexp
# region Helper Functions
def repl_func(match: re.Match):
    # JSON formatting helper
    return " ".join(match.group().split())

# TODO: Buggy - throws Sexp Errors
def extract_recursive(sexp_obj: Sexp, 
                      exclude:list = [], only:list = None, 
                      parents:list = None):
    """
    Recursively builds a dictionary from a Sexp object
    containing the primitives or collections composing its 
    base values. Currently knows how to exclude things. 
    Will eventually know how to recursively search for them
    too. 
    """
    ret_dict = {}
    for item in sexp_obj._value:
        if item not in exclude:
            if isinstance(item, Sexp):
                ret_dict[item._key] = extract_recursive(item, exclude=exclude)
            else:
                curr_val = sexp_obj[item]
                ret_dict[item] = curr_val\
                                        if not isinstance(curr_val, Sexp) \
                                        else extract_recursive(curr_val, exclude=exclude)

    return ret_dict
# endregion

error_pads = 0
error_files = 0
print('-'*30+"EXTRACTING FILES"+'-'*30)

for file in os.listdir('kicad files'):
    if file.endswith('.kicad_pcb'):
        print(f"Extracting routes from {file}")
        try:
            pcb = kicad_pcb_v6nc.KicadPCB.load(f"kicad files/{file}")
        except Exception as e:
            error_files += 1
            logging.error(f"error in {file}\n\t{str(e)}")

        routing = {}
        routing['board_settings'] = {} # extract_recursive(pcb.setup, exclude=['pcbplotparams'])
        routing['net classes'] ={}
        routing['net routes'] = {net[0]: {
                            'name': str(net[1]).strip('"'),
                            'class': "TODO",  
                            'pads':[],
                            'tracks':{
                                'segments':[],
                                'arcs': ["TODO: extract arc info. Most samples don't have arcs to help test :("],
                                'vias': ["TODO: are vias necessary for our routing interests?"]
                            },
                            'errors': []
                            } 
                        for net in pcb.net}
        routing['errors'] = []
        # region Collect pads by net idx
        footprints =pcb.module
        for item in footprints:
            # Pad locs are stored relative to their modules loc.
            component_loc = item.at[:2] 

            # Each component will have a number of pads.
            pads = item.pad # Each 
            for pad in pads:
                try:
                    comp_name = str(item[0]).strip('\"')
                    routing['net routes'][pad.net[0]]['pads'].append({f"{comp_name} pad {pad[0]}":{
                                                'abs_pos': (np.array(pad.at[:2]) + np.array(component_loc)).tolist()
                                                }
                                            })
                except AttributeError as e:
                    routing["errors"].append({f"{item[0]} at {item.at}": f"pad {pad[0]} {pad[1]} {pad[2]} at {pad.at[:2]} has error {e}"})
        # endregion 
        # region Collect tracks by net idx
        for track in pcb.segment:
            routing['net routes'][track.net]['tracks']['segments'].append({'start':track.start,
                                                        'end': track.end,
                                                        'width': track.width,
                                                        'layer': track.layer
                                                        })
        # TODO
        for track in pcb.arc:
            continue
        for track in pcb.via:
            continue
        # endregion

        with open(os.path.join(
                                os.path.dirname(__file__),
                                '../',f'unfiltered jsons/{file.split(".kicad_pcb")[0]} routing.json'
                                ), 
                  "w", encoding='utf-8'
                  ) as fd:
            
            s = json.dumps(routing,indent=2)
            s = re.sub("(?<=\[)[^\[\]]+(?=])", repl_func, s)
            fd.write(s)




