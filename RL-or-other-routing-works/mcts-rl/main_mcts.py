from stable_baselines3.ppo.policies import MlpPolicy
# from config import EnvParams
import sys
from MCTS_CREnv import MCTS_CREnv
import simulation

if __name__ == "__main__":

    # params = EnvParams
    # load_model = params.load_model
    # board_path = params.pcb_path

    board_path = sys.argv[1]
    load_model = sys.argv[2]
    resolution = float(sys.argv[3])

    resolution = [resolution, resolution]
    # np.random.seed(params.env.seed)

    env_mcts = MCTS_CREnv(pcb_path=board_path, resolution=resolution)
    env_mcts.reset()

    policy = MlpPolicy.load(load_model, device='cpu')

    paths = simulation.MCTS_search(env_mcts, policy, board_ID=board_path, rollout_times=10)
    print(paths)