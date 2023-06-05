import os
import shutil


if __name__ == "__main__":

    clean_pcb_folder = './Cleaning_PCBs'
    for pcb in os.listdir(clean_pcb_folder):
        if ".kicad_pcb" in pcb:
            pcb_name = ".".join(pcb.split(".")[:-1])
            source = clean_pcb_folder + "/" + pcb
            target = '../../PCBs/' + pcb_name + '/processed.kicad_pcb'
            shutil.copy(source, target)
    shutil.rmtree(clean_pcb_folder)
