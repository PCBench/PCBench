from stable_baselines3.ppo.policies import MlpPolicy
from config import EnvParams

from MCTS_CREnv import MCTS_CREnv
import simulation

if __name__ == "__main__":

    params = EnvParams
    load_model = params.load_model
    board_path = params.pcb_path

    # np.random.seed(params.env.seed)

    env_mcts = MCTS_CREnv(pcb_path=board_path, resolution=params.grid_resolution)
    env_mcts.reset()

    policy = MlpPolicy.load(load_model, device='cpu')

    paths = simulation.MCTS_search(env_mcts, policy, board_ID=board_path, rollout_times=100)
    # paths = simulation.MCTS_search(env_mcts, None, board_ID=board_path, rollout_times=100)
    # print(paths)