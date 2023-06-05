# Data Cleaning

## Prerequisites
+ KiCAD 5
+ FreeRouting>=1.7
+ Python 3

## PCB cleaning
1. Create `clean_list.csv`. List names of PCBs to be cleaned in `PCBs` folder in the `.csv` file named `clean_list.csv`, where each row contains one PCB name.  An example `clean_list.csv` is provided in this folder.
2. Run `PCB_cleaner.py` to delete fill zones and adjust `fp_text` names in `.kicad_pcb` file.
	```
	python PCB_clean.py
	```
	This will generate a folder named `Cleaning_PCBs` containing all PCBs after deleting fill zones. In the folder, each PCB has a name `pcb_name.kicad_pcb` where `pcb_name` is the named listed in `clean_list.csv`.
3. Use [FreeRouting](https://github.com/freerouting/freerouting) to route nets that are originally connected by fill zones. To do this, first open a `pcb_name.kicad_pcb` file in folder `Cleaning_PCBs` using KiCAD 5 and export it as `pcb_name.dsn` file. Then run FreeRouting by
	```
	java -jar freerouting-1.7.0.jar -de ./Cleaning_PCBs/pcb_name.dsn -do ./Cleaning_PCBs/pcb_name.ses
	```  
	After routing of FreeRouting, open `pcb_name.kicad_pcb` file in folder `Cleaning_PCBs` and import the `pcb_name.ses` and save `pcb_name.kicad_pcb`
4. Update dataset in `PCBs` folder by runing
	```
	python update_dataset.py
	```
	This will move all the `.kicad_pcb` files in `Clean_PCBs` folder to the corresponding PCB folder in `PCBs` folder of the root. Note that after runing this update script, the `Cleaning_PCBs` will be deleted.