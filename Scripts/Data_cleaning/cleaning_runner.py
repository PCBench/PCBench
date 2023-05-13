import os
import subprocess
from typing import List

import pandas as pd
from glob2 import glob
from tqdm import tqdm

DEBUG = True

if __name__ == "__main__":
    # Fetch all KiCad files
    files: List[str] = glob("../../PCBs/**/raw.kicad_pcb")
    if DEBUG:
        print(f"Discovered {len(files)} files:", [file.replace('../../PCBs/', '').replace('/raw.kicad_pcb', '') for file in files])

    
    # Lists to save successful and not successful files
    success_files: List[str] = list()
    error_files: List[str] = list()
    
    # Search files, and run loader 
    for file in tqdm(files):
        # Attempt to run the cleaner on all files
        error_log_Path = file.replace('raw.kicad_pcb', "error.log")
        processed_path = file.replace('raw.kicad_pcb', 'processed.kicad_pcb')
        if os.path.exists(error_log_Path):
            os.remove(error_log_Path)
        if os.path.exists(processed_path):
            print(f"removing file: {processed_path}")
            os.remove(processed_path)
        try:
            # os.chdir(file.replace("/raw.kicad_pcb", ''))
            result = subprocess.check_output(["python", "PCB_cleaner.py", file], stderr=subprocess.STDOUT) 
        # If running the cleaner on the file results in an error, report it
        except subprocess.CalledProcessError as e:
            error_files.append(file.replace('../../PCBs/', '').replace('/raw.kicad_pcb', ''))
            
            f = open(error_log_Path, "w")
            f.write(str(e.output, "UTF-8"))
            f.close()
            print(error_files)
        # If running the cleaner on the file is successful, report it
        else:
            success_files.append(file.replace('../../PCBs/', '').replace('/raw.kicad_pcb', ''))
        # os.chdir("../../Scripts/Data_cleaning")

    # Log the successful files and the non-successful ones
    print("Successful files: ", success_files)
    print("Error files:", error_files)
