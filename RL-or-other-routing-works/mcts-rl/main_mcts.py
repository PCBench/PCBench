import numpy as np
# import tensorflow as tf
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

    # env_shapes = dict()

    # if params.env.image_input:
    #     env_shapes['vis'] = env_mcts.state_shape
    # if params.env.vector_input:
    #     env_shapes['vec'] = env_mcts.state_shape

    # env_info = EnvInfo(params.env.env_name, 
    #                     params.env.is_discrete, 
    #                     params.env.image_input,
    #                     params.env.vector_input,
    #                     params.env.frame_stacking,
    #                     params.env.frames_stack_size, 
    #                     env_shapes,
    #                     env_mcts.n_actions)

    # network = network_builder(params.trainer.nn_architecure) \
    #     (hidden_sizes=params.policy.hidden_sizes, env_info=env_info)    # Build Neural Network with Forward Pass

    # model = CategoricalModel if env_info.is_discrete else GaussianModel
    # model = model(network=network, env_info=env_info)                   # Build Model for Discrete or Continuous Spaces

    # # if params.trainer.load_model:
    # print('Loading Model ...')
    # model.load_weights(os.path.join(model_path, "best"))           # Load model if load_model flag set to true

    # # for i in range(50):
    # #     test_policy(env_mcts, model, i)

    # paths = simulation.MCTS_search(env_mcts, model, board_ID=board_ID, rollout_times=1000)
    paths = simulation.MCTS_search(env_mcts, None, board_ID=board_path, rollout_times=10)
    # print(paths)