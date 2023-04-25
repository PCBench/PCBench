import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.ppo.policies import MlpPolicy
from config import EnvParams

# from nn_architecures import network_builder
# from models import CategoricalModel, GaussianModel
import os
import sys
from MCTS_CREnv import MCTS_CREnv
import simulation

if __name__ == "__main__":

    # physical_devices = tf.config.list_physical_devices('GPU')
    # tf.config.experimental.set_memory_growth(physical_devices[0], True)

    board_path = sys.argv[1]

    params = EnvParams
    load_model = params.load_model

    # np.random.seed(params.env.seed)

    env_mcts = MCTS_CREnv(pcb_path=board_path, resolution=params.grid_resolution)
    env_mcts.reset()

    policy = MlpPolicy.load(load_model)

    # paths = simulation.MCTS_search(env_mcts, model, board_ID=board_ID, rollout_times=1000)
    paths = simulation.MCTS_search(env_mcts, None, board_ID=board_path, rollout_times=10)
    # print(paths)