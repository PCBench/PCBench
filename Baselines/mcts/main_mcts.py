from stable_baselines3.ppo.policies import MlpPolicy
import sys
from MCTS_CREnv import MCTS_CREnv
import simulation
import json
import time

import resource
  
def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))

if __name__ == "__main__":

    limit_memory(32212254720)

    t1 = time.time()

    board_path = sys.argv[1]
    load_model = sys.argv[2]
    resolution = float(sys.argv[3])

    resolution = [resolution, resolution]
    # np.random.seed(params.env.seed)

    env_mcts = MCTS_CREnv(pcb_path=board_path, resolution=resolution)
    env_mcts.reset()

    policy = MlpPolicy.load(load_model, device='cpu')

    paths = simulation.MCTS_search(env_mcts, policy, board_ID=board_path, rollout_times=100)

    print(f"running time is: {time.time() - t1}")
    pcb_name = board_path.split("/")[-2]
    with open(f"path_{pcb_name}.json", "w") as outfile:
        json.dump(paths, outfile)