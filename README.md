# PCBench: A Dataset for Printed Circuit Board Routing
PCBench is a dataset for PCB routing task, it includes a dataset consisting of 164 printed circuit boards (PCB), a data augmentation script  to expand the dataset for supervised learning (SL) tasks, and a reinforcement learning (RL) environment.
  
 
## Dataset
### Folder Structure
All the PCB designs in our dataset are stored in the folder `PCBs`, where each PCB design is stored in a subfolder named `{author/org}_{PCB_name}_{design_version(optional)}`. Below is the folder structure of the dataset.
```
├── PCBs
│   ├── master_metadata.json
│   ├── subfolder1
│   │   ├── raw.kicad_pcb
│   │   ├── processed.kicad_pcb
│   │   ├── final.json
│   │   ├── metadata.json
│   ├── subfolder2
│   │   ├── raw.kicad_pcb
│   │   ├── processed.kicad_pcb
│   │   ├── final.json
│   │   ├── metadata.json
│   ├── ...
```
The `raw.kicad_pcb` is the raw PCB design file, `process.kicad_pcb` is the file after cleaning up, `final.json` stores only  routing-related information used for ML tasks. `metadata.json` stores the meta information for each single PCB design. `master_meta.json` contains metadata of all PCBs and global-level information.

### Meta Data
The meta data information can be found [here](https://pcbench.slab.com/posts/json-for-board-metadata-wqa2wdrc).

### PCB Routing Description Language (PCB-RDL)
We propose a JSON specification (`final.json` for each PCB design) called the PCB Routing Description  Language (PCB-RDL) that expresses a PCB routing problem and its solutions intuitively using basic concepts in order to facilitate research into automated PCB routing using ML. The details of PCB-RDL can be found [here](https://pcbench.slab.com/posts/pcb-routing-description-language-pcb-rdl-merz04kq).

![Test Image 4](https://github.com/PCBench/PCBench/blob/main/Images/PCB_example.png)

## Data Augmentation
### Run
The augmentation data can be generated with the script [`Scripts/Data_augmentation/augmentation.py`](https://github.com/PCBench/PCBench/blob/main/Scripts/Data_augmentation/augmentation.py).  To generate 3 samples by randomly extracting 50% nets from the PCB `1Bitsy_1bitsy`, please run the following command
```
cd Scripts/Data_augmentation/
python augmentation.py --num_samples 3 --net_ratio 0.5 --pcb_name 1Bitsy_1bitsy
```
### Output
All the generated PCBs will be stored in the folder named `augmented_data` under  `Scripts/Data_augmentation/`. In `augmented_data`, all the generated samples will be stored in a subfolder with the name of selected PCB. Each generated sample has the name `sample_index.json`. For example, the above command will generate the following file under `Scripts/Data_augmentation/`
```
├── augmented_data
│   ├── 1Bitsy_1bitsy
│   │   ├── 1.json
│   │   ├── 2.json
│   │   ├── 3.json
```

## RL environment

### Installation
The RL environment requires Python >= 3.7. You can simply install the environment with the following commands:
```
git clone https://github.com/PCBench/PCBench.git
cd PCBench
python setup.py install
```
After installation, open a Python console and type
```
from RLEnv.EnvLayer.PCBRoutingEnv import PCBRoutingEnv
```
If no error occurs, you have successfully installed the PCB routing environment.

### API Usage
The following content shows an example of API usage of PCBRoutingEnv. 
```
from RLEnv.EnvLayer.PCBRoutingEnv import PCBRoutingEnv
import random

resolution = [0.5, 0.5]
pcb_folder = '../PCBs/'
pcb_names = ["1Bitsy_1bitsy"]
iters = 30
env = PCBRoutingEnv(resolution=resolution, pcb_folder=pcb_folder, pcb_names=pcb_names)
obs, info = env.reset()
for _ in range(iters):
    act = random.randint(0,5)
    obs, rew, terminal, _, info = env.step(act)
    if terminal:
        env.reset()
```
You can find more examples of customizing functions of reward and state observation from [RLEnv/examples.ipynb](https://github.com/PCBench/PCBench/blob/main/RLEnv/examples.ipynb).