from typing import Any, Dict, List
import numpy as np
from extract_kicad import PCB


def PCB_cleaner(pcb: PCB, clean_segments: bool=True, clean_vias: bool=True) -> None:
    
    if clean_segments:
        del_incomplete_segments(pcb)

    if clean_vias:
        del_unconnected_vias(pcb)

def del_incomplete_segments(pcb: PCB) -> None:
    net_pads = pcb.net_pads
    segments = pcb.wires


def del_unconnected_vias(pcb: PCB) -> None:
    pass
