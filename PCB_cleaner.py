from typing import Any, Dict, List, Set, Tuple
from extract_kicad import PCB
from collections import defaultdict
import math

PAD_NODE_DIST_THRESHOLD = 0.001

def PCB_cleaner(
        pcb: PCB, 
        clean_segments: bool=True, 
        clean_vias: bool=True, 
        clean_pads: bool=True
    ) -> None:
    
    if clean_segments:
        del_incomplete_segments(pcb)

    if clean_vias:
        del_unconnected_vias(pcb)

    if clean_pads:
        del_isolate_pads(pcb)


def del_incomplete_segments(pcb: PCB) -> None:
    # extract net segments
    net2segs = defaultdict(list)
    for seg in pcb.wires:
        layer_idx = pcb.layers.index(seg.layer)
        net2segs[seg.net].append([tuple(seg.start + [layer_idx]), tuple(seg.end + [layer_idx])])
    # need to treat vias as a segment to create a graph for wires/paths
    for via in pcb.vias:
        l1, l2 = pcb.layers.index(via.layers[0]), pcb.layers.index(via.layers[1])
        net2segs[via.net].append([tuple(via.at + [l1]), tuple(via.at + [l2])])

    net2seggraph = dict()
    for net, segs in net2segs.items():
        # convert a net segments into a graph
        seg_graph = defaultdict(list)
        for seg in segs:
            seg_graph[seg[0]].append(seg[1])
            seg_graph[seg[1]].append(seg[0])
        # delete unconnected segments/edges from graph
        for node in seg_graph:
            curr_node = node
            while len(seg_graph[curr_node]) == 1 and not is_pad_node(curr_node, pcb.net_pads[net], pcb.layers):
                next_node = seg_graph[curr_node].pop()
                seg_graph[next_node].pop(seg_graph[next_node].index(curr_node))
                curr_node = next_node
        
        net2seggraph[net] = seg_graph
    
    new_segments = []
    for seg in pcb.wires:
        start_node = tuple(seg.start + [pcb.layers.index(seg.layer)])
        end_node = tuple(seg.end + [pcb.layers.index(seg.layer)])
        net_idx = seg.net
        if len(net2seggraph[net_idx][start_node]) > 0 and len(net2seggraph[net_idx][end_node]) > 0:
            new_segments.append(seg)

    pcb.wires = new_segments


def del_unconnected_vias(pcb: PCB) -> None:
    """ If a via is not connected by any given paths/wires of the given routed circuits, 
        then this via is viewed as an unconnected one and deleted.
    """
    seg_nodes = get_segment_end_nodes(pcb.wires, pcb.layers)
    new_vias = []
    for via in pcb.vias:
        l1 = pcb.layers.index(via.layers[0])
        l2 = pcb.layers.index(via.layers[1])
        via_node_l1 = tuple(via.at + [l1])
        via_node_l2 = tuple(via.at + [l2])
        if via_node_l1 in seg_nodes or via_node_l2 in seg_nodes:
            new_vias.append(via)

    pcb.vias = new_vias


def del_isolate_pads(pcb: PCB) -> None:
    """ If a pad/pin is not connected by any given paths/wires of the given routed circuits, 
        then this pad/pin is viewed as an isolated one and deleted.
    """
    seg_nodes = get_segment_end_nodes(pcb.wires, pcb.layers)
    obs_pads = []
    for net, pads in pcb.net_pads.items():
        new_pads = []
        for pad_info in pads:
            pad_pos = pad_info["pad_center_xy"] + (pcb.layers.index(pad_info["pad_layer"]),)
            if is_path_end_node(pad_pos, seg_nodes):
                new_pads.append(pad_info)
            else:
                obs_pads.append(pad_info)
        pcb.net_pads[net] = new_pads

    if pcb.obs_pad_value not in pcb.net_pads:
        pcb.net_pads[pcb.obs_pad_value] = []
    pcb.net_pads[pcb.obs_pad_value] += obs_pads


def get_segment_end_nodes(segments: List[Dict[str, Any]], layers: List[str]) -> Set[Tuple[float, float, float]]:
    # get all segment end nodes
    seg_nodes = set()
    for seg in segments:
        layer_idx = layers.index(seg.layer)
        start_node, end_node = tuple(seg.start + [layer_idx]), tuple(seg.end + [layer_idx])
        seg_nodes.add(start_node)
        seg_nodes.add(end_node)

    return seg_nodes


def is_path_end_node(
        node_xyz: Tuple[float, float, float], 
        seg_nodes: Set[Tuple[float, float, float]]
    ) -> bool:

    for node in seg_nodes:
        if math.dist(node, node_xyz) < PAD_NODE_DIST_THRESHOLD:
            return True
    return False


def is_pad_node(
        node_xyz: Tuple[float, float, float], 
        net_pads: List[Dict[str, Any]], 
        layers: List[str]
    ) -> bool:
    for pad_info in net_pads:
        pad_pos = pad_info["pad_center_xy"] + (layers.index(pad_info["pad_layer"]),)
        dist = math.dist(node_xyz, pad_pos)
        if dist < PAD_NODE_DIST_THRESHOLD:
            return True
    
    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        kicad_filename = sys.argv[1]
    else:
        kicad_filename = "./circuits_sources/other_sources/candleLight.kicad_pcb"
    pcb = PCB(kicad_filename)

    PCB_cleaner(pcb=pcb)

    from dump_wires2kicad_segments import dump_wires

    dump_wires(kicad_filename, pcb.wires, pcb.vias)