# Json Data Format

`example.json` provides an example of the json file we want that contain information extracted from kicad file. The following shows the meaning of each term/keys

```
{
    "pcbname": "example", # pcb file name
    "circuit_region": [min_x, min_y, max_x, max_y],  # this is is region of circuit, expressed by xy coordinates 

    # this is a list containing all the boundaries lines
    "boundaries": [[[line1_start_node_x, line1_start_node_x], [line1_end_node_x, line1_end_node_x], line_width], 
                   [[line2_start_node_x, line2_start_node_x], [line2_end_node_x, line2_end_node_x], line_width]],
    "net_indices": [1,2,3],  # a list of indices of all nets to be routed
    "nets": {
        net_index : {
            "net_name": "/VIN",  # net name
            "clearance": 0.149,  # net clearance
            "trace_width": 0.15,  # routing wire width for this net
            "via_dia": 0.45,      # via diameter for this net
            "via_drill": 0.25,    # via drill diameter
            "uvia_dia": 0.3,      # microvia diameter
            "uvia_drill": 0.1,    # microvia drill diameter
            
            # all pads in the net, a list of all pads (each pad is a dict)
            "pads": [
                {
                    "pad_center_xy": [115.35, 40.75],  # center xy coordinates for the pad
                    "pad_vertices": [[115.1, 40.5],    # each pad is a rectangle, and this stores its four vertices coordinates (xy)
                                    [115.1, 41.0],
                                    [115.6, 40.5],
                                    [115.6, 41.0]],
                    "pad_size": [0.5, 0.5],  # x and y sizes of the pad, this should be consistent with pad_vertices
                    "pad_layer": "F.Cu",     # which layer the pad is at
                    "drill_hole": "False"    # if this pad is a drill hole
                }
            ]
        }
    },
    # all the wires/routing solution of the pcb, wires is a list of all paths, and aach path/wire isa straight line
    "wires": [
        {
            "start": [101.6, 38.1], # start xy coordinate of a path
            "end": [101.6, 39.16],  # end xy coordinate of a path
            "width" : 0.15,        # line width (mm)
            "layer": "F.Cu",       # layer where the line is located at
            "net": 1              # which net the wire is belong to
        }
    ],
    # this is the list of all the vias in the routing solution
    "vias": [
        {
            "postion": [111.58, 44.720002],  # xy coordinate of the center of the via
            "diameter": 0.45,                # diameter of the via
            "drill_diameter" : 0.25,         # drill diameter of the via
            "layers": ["F.Cu", "B.Cu"],      # the layers that the via is for
            "net": 2                         # which net the via is belong to
        }
    ]
}
```