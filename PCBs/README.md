# Dataset of PCB designs
This folder stores all the PCB design (each design is stored in a folder, please refer to this [doc](https://pcbench.slab.com/public/posts/file-hierarchy-imdkde4b) for details of folder name and structure) including the raw files (kicad and eagle files) that we scrape directly from different sources, the cleaned files and stored in kicak format, and final JSON files that we use to store routing informations that can be used for ML tasks. [This repo](https://github.com/SergioGasquez/awesome-electronic-engineering#kicad) list learning resources for PCB or electronic designs. 

## find and upload PCB designs

To upload the circuit to this folder, please
1. upload the found circuit from different sources and store it in a folder (refer to this [doc](https://pcbench.slab.com/public/posts/file-hierarchy-imdkde4b) for details). Please refer this [doc](https://docs.google.com/document/d/10nzUBFvauhISvmaXDbtiUpjhvJx0_DutUYc8_EI8eA8/edit) about where to find the circuit.
2. go to `/PCBench/Scripts/Data_cleaning` and run `python PCB_cleaner.py kicad_file_path`. It will output a `processed.kicad_pcb` file to the folder where the raw file is stored. Note that the clean-up script currently only works for kicad files. For eagle files, just ignore this and following steps for now.
3. open the cleaned-up `processed.kicad_pcb` file and check if the clean up is correct. Please refer to this [issue](https://github.com/ybiao-he/PCBench/issues/1) about criterias of correctness.

Note that 
1. if the souce file is from KiCAD version 5, please put `.kicad_pcb` file in the folder, and if the source file is from KiCAD version 6, please put `.kicad_pcb` and `.pro` file in the folder. 
2. if you meet any issues when uploading PCB designs or run our scripts for cleaning up the data, please report the issue to [github issues of this repo](https://github.com/ybiao-he/PCBench/issues).
