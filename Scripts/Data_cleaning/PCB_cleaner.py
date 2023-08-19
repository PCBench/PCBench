import csv
from functools import reduce
from collections import defaultdict
import sys
sys.path.append('..')
from Data_extraction.thirdparty.kicad_parser.kicad_pcb import *

import os

PCB_folder = "new_PCBs"

def read_csv(file_name):
    with open(file_name, "r") as f:
        pcb_names = list(csv.reader(f, delimiter=","))

    pcb_names = reduce(lambda xs, ys: xs + ys, pcb_names)
    return pcb_names


def revise_module_fp_text(pcb):
    text_count = defaultdict(int)
    for m in pcb.module:
        text_count[m.fp_text[0][1]] += 1

    for m in pcb.module:
        if text_count[m.fp_text[0][1]] > 1 or m.fp_text[0][1] == '""' or m.fp_text[0][1] == '" "':
            tmp_text = m.fp_text[0][1]
            if tmp_text == '""':
                m.fp_text[0][1] =  f"Noname_{text_count[tmp_text]}"
            elif tmp_text == '" "':
                m.fp_text[0][1] =  f"None_{text_count[tmp_text]}"
            else:
                m.fp_text[0][1] =  str(tmp_text) + "_" + str(text_count[tmp_text])
            del m.fp_text[0][1][0]
            text_count[tmp_text] -= 1


def delete_segment_via(pcb, delete_nets):
    seg_idx = []
    via_idx = []
    for i in range(len(pcb.segment)):
        if pcb.segment[i].net in delete_nets:
            seg_idx.append(i)
    seg_idx.sort()
    for i in range(len(pcb.via)):
        if pcb.via[i].net in delete_nets:
            via_idx.append(i)
    via_idx.sort()

    bc = 0
    for i in seg_idx:
        del_i = i - bc
        if pcb.segment[del_i].net in delete_nets:
            del pcb.segment[del_i]
            bc += 1

    bc = 0

    for i in via_idx:
        del_i = i - bc
        if pcb.via[del_i].net in delete_nets:
            del pcb.via[del_i]
            bc += 1


def delete_fill_zone(pcb_names):
    fill_zone_folder = "Cleaning_PCBs"
    if not os.path.exists(fill_zone_folder):
        os.mkdir(fill_zone_folder)

    for name in pcb_names:
        pcb_file_path = f"../../{PCB_folder}/" + name + "/raw.kicad_pcb"
        new_pcb_name = name + ".kicad_pcb"
        pcb = KicadPCB.load(pcb_file_path)
        fill_zone_nets = set([])
        for zone in pcb.zone:
            fill_zone_nets.add(zone.net)
        del pcb.zone
        delete_segment_via(pcb, fill_zone_nets)
        revise_module_fp_text(pcb)
        pcb.export(os.path.join(fill_zone_folder, new_pcb_name))

if __name__ == "__main__":

    pcb_names = read_csv("clean_list.csv")
    delete_fill_zone(pcb_names)

