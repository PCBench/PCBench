from collections import defaultdict
import sys
from Scripts.Data_extraction.thirdparty.kicad_parser.kicad_pcb import *
import os


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

def preprocess_single_PCBs(pcb_name, output_folder):

    pcb_file_path = os.path.join("../../PCBs/", pcb_name, "processed.kicad_pcb")
    new_pcb_name = pcb_name + ".kicad_pcb"
    pcb = KicadPCB.load(pcb_file_path)

    del pcb.zone
    del pcb.segment
    del pcb.via
    revise_module_fp_text(pcb)
    pcb.export(os.path.join(output_folder, new_pcb_name))

def preprocess_all_PCBs(output_folder):

    for pcb_name in os.listdir("../../PCBs/"):
        if os.path.isdir(os.path.join("../../PCBs/", pcb_name)):
            preprocess_single_PCBs(pcb_name, output_folder)

if __name__ == "__main__":

    unrouted_folder = "unrouted"
    if not os.path.exists(unrouted_folder):
        os.mkdir(unrouted_folder)

    if len(sys.argv) > 1:
        pcb_name = sys.argv[1]
    else:
        preprocess_all_PCBs(unrouted_folder)





