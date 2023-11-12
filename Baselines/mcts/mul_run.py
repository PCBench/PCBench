import os
import sys

if __name__ == '__main__':

	model_folder = sys.argv[1]
	for model_file in os.listdir(model_folder):
		if model_file[:6] != "policy":
			continue
		pcb_name = model_file[7:]
		model_file_path = os.path.join(model_folder, model_file)
		pcb_json_file_path = os.path.join(os.path.join("../../PCBs", pcb_name), "final.json")
		log_path = os.path.join(model_folder, pcb_name + ".log")
		if pcb_name + ".log" not in os.listdir(model_folder):
			pcb_json_file_path = pcb_json_file_path.replace(" ", "\ ")
			model_file_path = model_file_path.replace(" ", "\ ")
			log_path = log_path.replace(" ", "\ ")
			os.system(f"python3 main_mcts.py {pcb_json_file_path} {model_file_path} 0.5 | tee {log_path}")
			break