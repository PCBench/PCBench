import os
import shutil
import json

import sys
sys.path.append('..')
from Data_extraction.thirdparty.kicad_parser.kicad_pcb import *


def extract_layer(pcb: KicadPCB, max_layer_index: int):
    
    layers = list()
    layer_indices = []
    for k in pcb.layers:
        if int(k) < max_layer_index:
            layer_indices.append(int(k))
            layers.append(pcb.layers[k][0])
    
    return [x for _, x in sorted(zip(layer_indices, layers))]


def update_meta_data(pcb_name: str):
    source = os.path.join("../../PCBs", pcb_name, "raw.kicad_pcb")
    pcb = KicadPCB.load(source)
    meta_path = os.path.join("../../PCBs", pcb_name, "metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)

    max_layer_index = 16 if pcb.version == 3 else 32
    layers = extract_layer(pcb=pcb, max_layer_index=max_layer_index)
    meta["layers"] = len(layers)
    meta["CAD version"] = "KiCad " + str(pcb.version)

    with open(meta_path, "w", encoding='utf-8') as f:
        metaf = json.dumps(meta, indent=2)
        f.write(metaf)


if __name__ == "__main__":

    clean_pcb_folder = 'Cleaning_PCBs'
    for pcb in os.listdir(clean_pcb_folder):
        if ".kicad_pcb" in pcb:
            pcb_name = ".".join(pcb.split(".")[:-1])
            source = os.path.join(clean_pcb_folder, pcb)
            target = os.path.join('../../PCBs', pcb_name, 'processed.kicad_pcb')
            shutil.copy(source, target)
            update_meta_data(pcb_name)
    shutil.rmtree(clean_pcb_folder)
