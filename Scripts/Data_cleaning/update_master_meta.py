import os
import json

def update_master_meta(root_folder: str):

    master_meta = {}
    global_info = {
            "Num. Unique pcb designs": 0, # number of dirs in PCBs/
            "Num. Unique repos": 0,       # distinct_count(source)
            "Kicad source files": 0, # count(isKicad(raw))
            "Eagle source files": 0, # count(not isKicad(raw))
            "From Adafruit": 0,      # count(org == "https://github.com/adafruit")
            "From Sparkfun": 0,      # count(org == "https://github.com/sparkfun")
            "From Kitspace": 0,       # count(org == "https://kitspace.org")
            "Unique Repos": ["https://github.com/owner_or_org/repo",...]
        }
    master_meta["Global Info"] = global_info
    pcb_folder = os.path.join(root_folder, "PCBs")
    unique_repos = set([])
    count_kitspace = 0
    count_kicad = 0
    for pcb_name in os.listdir(pcb_folder):
        meta_path = os.path.join(pcb_folder, pcb_name, "metadata.json")
        with open(meta_path) as f:
            meta = json.load(f)
        unique_repos.add(meta["source"])
        if "kitspace" in pcb_name:
            count_kitspace += 1
        if "kicad_pcb" in meta["raw"]:
            count_kicad += 1
        master_meta[pcb_name] = meta

    master_meta["Global Info"]["Num. Unique pcb designs"] = len(os.listdir(pcb_folder))
    master_meta["Global Info"]["Num. Unique repos"] = len(unique_repos)
    master_meta["Global Info"]["Kicad source files"] = count_kicad
    master_meta["Global Info"]["From Kitspace"] = count_kitspace
    master_meta["Global Info"]["Unique Repos"] = list(unique_repos)

    with open(os.path.join(root_folder, "master_metadata.json"), "w", encoding='utf-8') as f:
        metaf = json.dumps(master_meta, indent=2)
        f.write(metaf)

if __name__ == "__main__":
    update_master_meta("../../PCBs/")