# Benchmarking the SOTA

We benchmark three PCB routers using our dataset: [RL-MCTS router](https://ieeexplore.ieee.org/document/9768074), [FreeRouting](https://github.com/freerouting/freerouting), and [PcbRouter](https://github.com/The-OpenROAD-Project/PcbRouter). The first one is a ML-based approach, and the other two are heuristic approaches. The detailed results of these approaches can be found [here](https://docs.google.com/spreadsheets/d/1P1y3hfvNfsB1HC0W9c6N1bXTP7QoEg7tjmHyZq8PSmM/edit#gid=0).

## ML-based approach: RL-MCTS
### Prerequisites
+ [Gymnasium](https://gymnasium.farama.org/)
+ [Stable-Baselines3 > 2.0](https://stable-baselines3.readthedocs.io/en/master/guide/install.html)
+ [tqdm](https://github.com/tqdm/tqdm)
+ [Rich](https://rich.readthedocs.io/en/stable/introduction.html)
+ [PyTorch](https://pytorch.org/)
+ [Scipy](https://scipy.org/)
+ [KiCad](https://www.kicad.org/): Current support for .kicad_pcb format derived from KiCad v5.

### Run
#### Train RL policy:
```
cd Baselines/RL/
python agent.py
```
All the configurations about training can be set in the .json file [params.json](https://github.com/PCBench/PCBench/blob/main/Baselines/RL/params.json).
#### Routing by MCTS:
```
cd Baselines/mcts/
python main_mcts.py path_to_board_json path_to_rl_policy grid_resolution
```
Please revise arguments of the second line to its corresponding values. The `grid_resolution` is 0.5 in this experiment.
For other settings of this approaches, please contact authors of the [paper](https://ieeexplore.ieee.org/document/9768074).

## Heuristic approaches
For heuristic approaches, we provide a script, [clean.py](https://github.com/PCBench/PCBench/blob/main/Baselines/heuristics/clean.py) to remove teh existing wires on the PCB to be routed if there is any. You can run it by following command:
```
cd Baselines/heuristics/
python clean.py pcb_name
```
`pcb_name` is the name of PCB to be routed in the folder `PCBs`. The cleaned PCB will be stored in a generated folder named `unrouted` under the folder  `Baselines/heuristics/`.

### FreeRouting
Please refer to this [repo](https://github.com/freerouting/freerouting).

### PcbRouter
This is the work of paper: [A Unified Printed Circuit Board Routing Algorithm With Complicated Constraints and Differential Pairs](https://dl.acm.org/doi/10.1145/3394885.3431568).

Please refer to this [repo](https://github.com/The-OpenROAD-Project/PcbRouter) to use thier method.