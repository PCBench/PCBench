# Data Cleaning

## Dependencies
1. numpy

## Extract PCB information
To extract PCB information, please call `PCB` in `extract_kicad.py`. Here is an example code:
```
kicad_filename = "./benchmarks/real_world/1bitsy.kicad_pcb"
pcb = PCB(kicad_filename)
```

The extracted infomation are stored in `PCB` class, it includes following PCB inforamtion (look at [test.ipynb](https://github.com/ybiao-he/PCBench/blob/main/test.ipynb) about how to access each info):
1. layers: a list of layer names
2. boundary lines (now it only support straight lines, arcs need to be added later): a list of boundary lines
3. circuit range: a list of min_x, min_y, max_x, max_y
4. net info: a dict including: clearance, trace width, via diameter, vias drill diameter, microvia diameter, microvia drill diameter
5. net pads: a dict including: center xy coordinate, pad vertices xy coordinates, pad size, pad layer, if the pad is drill hole
6. wires: a list of wires
7. vias: a list of vias

## Clean up data
Run `python PCB_cleaner.py kicad_file_path`. It will output a `processed.kicad_pcb` file to the folder of `kicad__file_path`.

The current clean up includes:
1. delete incomplete wires
2. delete isolated vias
3. convert isolated pad to obstacles