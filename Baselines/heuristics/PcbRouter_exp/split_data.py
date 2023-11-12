import os
import shutil

unrouted_folder = "./unrouted"
split_folder_prefix = "split_unrouted"
num_pcb_per_folder = 119

for name in os.listdir(unrouted_folder):
	if name[-3:] == "pro":
		os.remove(os.path.join(unrouted_folder, name))

kicad_file_names = [name for name in os.listdir(unrouted_folder) if name[-10:]==".kicad_pcb"]
print(f"found {len(kicad_file_names)} kicad_pcb files....")
num_folders = len(kicad_file_names) // num_pcb_per_folder

for i in range(num_folders):
	folder_name = split_folder_prefix + "_" + str(i)
	if not os.path.exists(folder_name):
		os.mkdir(folder_name)

for i, file_name in enumerate(kicad_file_names):
	folder_idx = i // num_pcb_per_folder
	folder_idx = folder_idx - 1 if folder_idx >= num_folders else folder_idx

	original_loc = os.path.join(unrouted_folder, file_name)
	target_loc = os.path.join(split_folder_prefix + "_" + str(folder_idx), file_name)
	shutil.copyfile(original_loc, target_loc)