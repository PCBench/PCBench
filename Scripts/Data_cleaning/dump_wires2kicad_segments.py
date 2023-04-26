from typing import Any, Dict, List, Optional
from kicad_pcb import *
import os

def delete_segment_via(pcb: KicadPCB) -> None:

    seg_len = len(pcb.segment)
    for i in range(seg_len):
        del pcb.segment[0]

    via_len = len(pcb.via)
    for i in range(via_len):
        del pcb.via[0]


def dump_wires(
        origianl_kicad_file: str, 
        wires: List[Dict[str, Any]],
        vias: List[Dict[str, Any]],
        del_pads_infos: Optional[List[Dict[str, Any]]] = None
    ) -> None:

    pcb = KicadPCB.load(origianl_kicad_file)
    delete_segment_via(pcb)
    for seg in wires:
        seg_str = f"""(segment (start {seg.start[0]} {seg.start[1]}) (end {seg.end[0]} {seg.end[1]}) (width {seg.width}) (layer {seg.layer}) (net {seg.net}))"""
        pcb.segment = SexpParser(parseSexp(seg_str))
    
    for via in vias:
        via_str = f"""(via (at {via.at[0]} {via.at[1]}) (size {via.size}) (layers {via.layers[0]} {via.layers[1]}) (net {via.net}))"""
        pcb.via = SexpParser(parseSexp(via_str))
    
    if del_pads_infos is not None:
        for del_pad_info in del_pads_infos:
            m_i, p_i = del_pad_info["m_p_index"]
            if "net" in pcb.module[m_i].pad[p_i]:
                del pcb.module[m_i].pad[p_i]["net"]

    file_path = origianl_kicad_file.split('/')
    file_path[-1] = 'processed.kicad_pcb'
    output_filename = '/'.join(file_path)
    pcb.export(output_filename)