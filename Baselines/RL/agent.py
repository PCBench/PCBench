from stable_baselines3 import PPO, A2C
import os
from RLEnv.EnvLayer.PCBRoutingEnv import PCBRoutingEnv
from params import Params
from stable_baselines3.common.logger import configure

class Agent:
    def __init__(self, env=None, pcb_names=None) -> None:
        self.params = Params()
        if self.params.rl.load_model_name is not None:
            self.load_model_name = os.path.dirname(os.path.abspath(__file__)) + "/models/" + self.params.rl.load_model_name
        else:
            self.load_model_name = None
        self.pcb_names = pcb_names
        self._build_env(env)
        self._build_model()

    def _build_env(self, env=None) -> None:
        if self.pcb_names is None:
            self.pcb_names = self.params.env.pcb_names
        else:
            self.pcb_names = [self.pcb_names]
        if self.params.env.env_name == "basic_pos":
            self.env = PCBRoutingEnv(
                resolution=self.params.env.resolution, 
                pcb_folder=self.params.env.benchmark_folder,
                pcb_names=self.pcb_names
            )
        elif self.params.env.env_name == "rl-mcts":
            from rl_env import rl_env
            self.env = rl_env(
                resolution=self.params.env.resolution, 
                pcb_folder=self.params.env.benchmark_folder,
                pcb_names=self.pcb_names
            )
        else:
            self.env = env
        
        self.env.reset()

    def _build_model(self) -> None:

        policy_kwargs = dict(activation_fn=self.params.rl.activation_function,
                     net_arch=dict(pi=self.params.rl.actor_net_structure, vf=self.params.rl.critic_net_structure))
        
        if self.params.rl.rl_model_name == "a2c":
            if self.load_model_name is not None:
                self.model = A2C.load(self.load_model_name, env=self.env)
            else:
                self.model = A2C(
                    policy=self.params.rl.policy_network, 
                    env=self.env, 
                    policy_kwargs=policy_kwargs, 
                    verbose=1)
        else:
            # default model is PPO
            if self.load_model_name is not None:
                self.model = PPO.load(self.load_model_name, env=self.env)
            else:
                self.model = PPO(
                    policy=self.params.rl.policy_network, 
                    env=self.env,
                    learning_rate=self.params.rl.lr,
                    n_steps=self.params.rl.n_steps,
                    batch_size=self.params.rl.batch_size,
                    n_epochs=self.params.rl.n_epochs,
                    gamma=self.params.rl.gamma,
                    gae_lambda=self.params.rl.gae_lambda,
                    ent_coef=self.params.rl.ent_coef,
                    vf_coef=self.params.rl.vf_coef,
                    policy_kwargs=policy_kwargs, 
                    verbose=1,
                    device=self.params.rl.device
                )

        logger_path = os.path.dirname(os.path.abspath(__file__)) + "/logs/" + self.env.pcb_name + "/"
        if not os.path.exists(logger_path):
            os.mkdir(logger_path)
        # set up logger
        new_logger = configure(logger_path, ["stdout", "csv", "tensorboard"])
        self.model.set_logger(new_logger)
    
    def learn(self) -> None:
        self.model.learn(total_timesteps=self.params.rl.total_timesteps, progress_bar=True)
        if self.params.rl.save_model_name is not None:
            self.save()

    def save(self) -> None:
        models_folder = os.path.dirname(os.path.abspath(__file__)) + "/models/"
        if not os.path.exists(models_folder):
            os.mkdir(models_folder)
        self.model.save(models_folder + self.params.rl.save_model_name + self.env.pcb_name)
        self.model.policy.save(models_folder + "policy_" + self.env.pcb_name)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pcb_name = sys.argv[1].split('/')[-1]
    else:
        pcb_name = None
    if not os.path.exists("logs"):
        os.mkdir("logs")
    agent = Agent(pcb_names=pcb_name)
    agent.learn()