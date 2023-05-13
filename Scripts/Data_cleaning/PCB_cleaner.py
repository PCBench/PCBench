import sys
sys.path.append('..')

from typing import Any, Dict, List, Set, Tuple
from Data_extraction.extract_kicad import PCB
from collections import defaultdict
import math
import networkx as nx


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
    """ delete all segments for a net if its connections use fill zones or there are some incomplete connections
    """
    # extract net segments
    net2segs = defaultdict(list)
    for seg in pcb.wires:
        layer_idx = pcb.layers.index(seg.layer)
        net2segs[seg.net].append([tuple(seg.start + [layer_idx]), tuple(seg.end + [layer_idx])])
    # need to treat vias as a segment to create a graph for wires/paths
    for via in pcb.vias:
        l1, l2 = pcb.layers.index(via.layers[0]), pcb.layers.index(via.layers[1])
        ls, le = min(l1, l2), max(l1, l2)
        for l in range(ls, le):
            net2segs[via.net].append([tuple(via.at + [l]), tuple(via.at + [l+1])])

    net2seggraph = dict()
    for net, segs in net2segs.items():
        # convert a net segments into a graph
        if net not in pcb.net_pads:
            net2seggraph[net] = []
            continue
        seg_graph = defaultdict(list)
        for seg in segs:
            if seg[0] != seg[1]:
                seg_graph[seg[0]].append(seg[1])
                seg_graph[seg[1]].append(seg[0])

        # delete unconnected segments/edges from graph
        for node in seg_graph:
            curr_node = node
            while len(seg_graph[curr_node]) == 1 and not is_pad_node(curr_node, pcb.net_pads[net], pcb.layers):
                next_node = seg_graph[curr_node].pop()
                seg_graph[next_node].pop(seg_graph[next_node].index(curr_node))
                curr_node = next_node

        all_nodes = list(seg_graph.keys())
        for node in all_nodes:
            if len(seg_graph[node]) == 0 and not is_pad_node(node, pcb.net_pads[net], pcb.layers):
                del seg_graph[node]
        # check if the cleaned graph is fully connected, if not, delete this net
        if is_graph_fully_connected(seg_graph):
            net2seggraph[net] = seg_graph
        else:
            net2seggraph[net] = []
    
    new_segments = []
    for seg in pcb.wires:
        start_node = tuple(seg.start + [pcb.layers.index(seg.layer)])
        end_node = tuple(seg.end + [pcb.layers.index(seg.layer)])
        net_idx = seg.net
        if len(net2seggraph[net_idx]) > 0 and len(net2seggraph[net_idx][start_node]) > 0 and len(net2seggraph[net_idx][end_node]) > 0:
            new_segments.append(seg)

    pcb.wires = new_segments


def del_unconnected_vias(pcb: PCB) -> None:
    """ If a via is not connected by any given paths/wires of the given routed circuits, 
        then this via is viewed as an unconnected one and deleted.
    """
    seg_nodes = get_segment_end_nodes(pcb.wires, pcb.layers)
    new_vias = []
    for via in pcb.vias:
        l1, l2 = pcb.layers.index(via.layers[0]), pcb.layers.index(via.layers[1])
        ls, le = min(l1, l2), max(l1, l2)
        for l in range(ls, le+1):
            via_node_l = tuple(via.at + [l])
            if via_node_l in seg_nodes:
                new_vias.append(via)
                break

    pcb.vias = new_vias


def del_isolate_pads(pcb: PCB) -> None:
    """ If a pad/pin is not connected by any given paths/wires of the given routed circuits, 
        then this pad/pin is viewed as an isolated one and deleted.
    """
    seg_nodes = get_segment_end_nodes(pcb.wires, pcb.layers)
    obs_pads = []
    for net, pads in pcb.net_pads.items():
        new_pads = []
        drill_holes = dict()
        single_layer_pads = []
        for pad_info in pads:
            if pad_info["drill_hole"]:
                drill_holes[pad_info['m_p_index']] = pad_info
            else:
                single_layer_pads.append(pad_info)
        for pad_info in single_layer_pads:
            pad_pos = pad_info["pad_center_xy"] + (pcb.layers.index(pad_info["pad_layer"]),)
            if is_path_end_node(pad_pos, min(pad_info["pad_size"]), seg_nodes):
                new_pads.append(pad_info)
            else:
                obs_pads.append(pad_info)
        for _, dhs in drill_holes.items():
            dh_obs = True
            for l in dhs["pad_layer"]:
                dh_pos = dhs["pad_center_xy"] + (pcb.layers.index(l),)
                if is_path_end_node(dh_pos, min(pad_info["pad_size"]), seg_nodes):
                    dh_obs = False
            if dh_obs:
                obs_pads.append(dhs)
            else:
                new_pads.append(dhs)

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
        pad_size: float,
        seg_nodes: Set[Tuple[float, float, float]]
    ) -> bool:

    for node in seg_nodes:
        if node_xyz[-1] == node[-1] and math.dist([node[0], node[1]], [node_xyz[0], node_xyz[1]]) < PAD_NODE_DIST_THRESHOLD:
            return True
    return False


def is_pad_node(
        node_xyz: Tuple[float, float, float], 
        net_pads: List[Dict[str, Any]], 
        layers: List[str]
    ) -> bool:
    for pad_info in net_pads:
        pad_layers = [layers.index(pl) for pl in pad_info["pad_layer"]]
        if node_xyz[-1] not in pad_layers:
            continue
        pad_xy = pad_info["pad_center_xy"]
        pad_size = min(pad_info["pad_size"])
        dist = math.dist([node_xyz[0], node_xyz[1]], pad_xy)
        if dist < PAD_NODE_DIST_THRESHOLD:
            return True
    
    return False


def is_graph_fully_connected(
        graph: Dict[Tuple[float, float, float], List[Tuple[float, float, float]]],
    ) -> bool:

    edges = []
    for node in graph:
        for next_node in graph[node]:
            edges.append([node, next_node])
    if len(edges) == 0:
        return False
    G = nx.Graph()
    G.add_edges_from(edges)
    return nx.is_connected(G)


if __name__ == "__main__":
    import sys
    kicad_filename = sys.argv[1]

    pcb = PCB(kicad_filename)
    PCB_cleaner(pcb=pcb)
    del_pads = pcb.net_pads[pcb.obs_pad_value]

    from dump_wires2kicad_segments import dump_wires

    dump_wires(kicad_filename, pcb.wires, pcb.vias, del_pads)