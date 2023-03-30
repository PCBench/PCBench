from typing import Any, Dict, List
from thirdparty.kicad_parser.kicad_pcb import *


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
        vias: List[Dict[str, Any]]
    ) -> None:

    pcb = KicadPCB.load(origianl_kicad_file)
    delete_segment_via(pcb)
    for seg in wires:
        seg_str = f"""(segment (start {seg.start[0]} {seg.start[1]}) (end {seg.end[0]} {seg.end[1]}) (width {seg.width}) (layer {seg.layer}) (net {seg.net}))"""
        pcb.segment = SexpParser(parseSexp(seg_str))
    
    for via in vias:
        via_str = f"""(via (at {via.at[0]} {via.at[1]}) (size {via.size}) (layers {via.layers[0]} {via.layers[1]}) (net {via.net}))"""
        pcb.via = SexpParser(parseSexp(via_str))
    
    file_path = origianl_kicad_file.split("/")
    file_path[file_path.index("real_world")] = "processed_kicad"
    output_filename = '/'.join(file_path)
    pcb.export(output_filename)