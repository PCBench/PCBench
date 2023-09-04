# Data Cleaning

## Prerequisites
+ KiCAD 5
+ FreeRouting=1.7
+ Python 3

## PCB cleaning
1. Put all PCBs need to be cleaned in the folder `new_PCBs` and check if they are valid. If they are not valid, then drop it (no need to clean and we will not use it). The criteria of judging if a PCB is valid are:
* Please open each PCB using KiCAD 5, and if KiCAD 5 can not open it, then the PCB is NOT valid. (It can be from KiCAD 6 or 7, let's view it as invalid for now.)
* If a PCB does not contain any nets, then the PCB is NOT valid.
* If a PCB does not contain boundaries (on edge.cut layer), then the PCB is NOT valid.
* If a PCB is not routed (does not contain any wires), then the PCB is NOT valid.
* If a PCB is exacly same with another one or is the part of a PCB panel, then the PCB is NOT valid. (This is to delete duplicate PCBs).

2. Create `clean_list.csv`. List names of PCBs to be cleaned in `new_PCBs` folder in the `.csv` file named `clean_list.csv`, where each row contains one PCB name.  An example `clean_list.csv` is provided in this folder.
3. Run `PCB_cleaner.py` to delete fill zones and adjust `fp_text` names in `.kicad_pcb` file.
	```
	python PCB_clean.py
	```
	This will generate a folder named `Cleaning_PCBs` containing all PCBs after deleting fill zones. In the folder, each PCB has a name `pcb_name.kicad_pcb` where `pcb_name` is the named listed in `clean_list.csv`.
4. Use [FreeRouting](https://github.com/freerouting/freerouting) to route nets that are originally connected by fill zones. To do this, first open a `pcb_name.kicad_pcb` file in folder `Cleaning_PCBs` using KiCAD 5 and export it as `pcb_name.dsn` file. Then run FreeRouting by
	```
	java -jar freerouting-1.7.0.jar -de ./Cleaning_PCBs/pcb_name.dsn -do ./Cleaning_PCBs/pcb_name.ses
	```  
	After routing of FreeRouting, open `pcb_name.kicad_pcb` file in folder `Cleaning_PCBs` and import the `pcb_name.ses` and save `pcb_name.kicad_pcb`

	If FreeRouting fails to route a PCB, we need to manually route them and if there are too much nets need to be manually routed, please record the PCB names.
5. Update dataset in `new_PCBs` folder by runing
	```
	python update_dataset.py
	```
	This will move all the `.kicad_pcb` files in `Clean_PCBs` folder to the corresponding PCB folder in `new_PCBs` folder of the root. Note that after runing this update script, the `Cleaning_PCBs` will be deleted.