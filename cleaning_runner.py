import os
import subprocess
from typing import List

import pandas as pd
from glob2 import glob
from tqdm import tqdm

DEBUG = True

if __name__ == "__main__":
    # Fetch all KiCad files
    files: List[str] = glob("PCBs/**/raw.kicad_pcb")
    print(files)
    if DEBUG:
        print(f"Discovered {len(files)} files:", [file.replace('PCBs/', '').strip('/raw.kicad_pcb') for file in files])

    
    # Lists to save successful and not successful files
    success_files: List[str] = list()
    error_files: List[str] = list()
    
    # Search files, and run loader 
    for file in tqdm(files):
        # Attempt to run the cleaner on all files
        try:
            os.chdir(file.replace("/raw.kicad_pcb", ''))
            result = subprocess.check_output(["python", "../../Scripts/Data_cleaning/PCB_cleaner.py", "raw.kicad_pcb"], stderr=subprocess.STDOUT) 
        # If running the cleaner on the file results in an error, report it
        except subprocess.CalledProcessError as e:
            error_files.append(file.strip('PCBs/').strip('/raw.kicad_pcb'))
            if os.path.exists("error.log"):
                os.remove("error.log")
            f = open("error.log", "x")
            f.write(str(e.output, "UTF-8"))
            f.close()
            print(error_files)
        # If running the cleaner on the file is successful, report it
        else:
            success_files.append(file.strip('PCBs/').strip('/raw.kicad_pcb'))
        os.chdir("../..")

    # Log the successful files and the non-successful ones
    print("Successful files: ", success_files)
    print("Error files:", error_files)
