from typing import Iterable
import kicad_pcb_v6nc
import extract_kicad
from sexp_parser import *

def extract_recursive(sexp_obj: Sexp, 
                      exclude:list = [], only:list = None, 
                      parents:list = None):
    ret_dict = {}
    # if any(isinstance(item, Sexp) for item in sexp_obj._value):
    if not isinstance(sexp_obj._value,str):
        for item in sexp_obj._value:
            if item not in exclude:
                if isinstance(item, Sexp):
                    ret_dict[item._key] = extract_recursive(item, exclude=exclude)
                else:
                    curr_val = sexp_obj[item]
                    ret_dict[item] = curr_val\
                                            if not isinstance(curr_val, Sexp) \
                                            else extract_recursive(curr_val, exclude=exclude) if not isinstance(curr_val, Iterable)\
                                            else [extract_recursive(sub_item) for sub_item in curr_val]
                    
    else: 
        ret_dict[sexp_obj._key] = sexp_obj._value

    return ret_dict
    
file = "kicad files/antenna_analyser.kicad_pcb"
pcb = extract_kicad.PCB(file)
pcb.dump_to_PBCRDL_json()
# pcb = kicad_pcb_v6nc.KicadPCB.load(file)
# my_dict = {'net_class': [extract_recursive(net_class) for net_class in pcb.net_class]}
# print(my_dict)