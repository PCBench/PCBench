import os
import json
from typing import Any, Dict, List
from torch import nn


class EnvParams:

    resolution: float = 0.5
    benchmark_folder: str = None
    pcb_names: str = None
    termination_rule: str="r"  # "r" for terminating when all nets are routed, 'v' for terminating when there is a DRV  
    DRV_penalty_coef: float=10

    def __init__(self, env_params: Dict[str, Any]) -> None:
        self.resolution = env_params["resolution"]
        self.benchmark_folder = env_params["benchmark_folder"]
        self.pcb_names = env_params["pcb_names"]
        self.termination_rule = env_params["termination_rule"]
        self.DRV_penalty_coef = env_params["design_rule_violate_penalty_coef"]


class RLParams:
    rl_model_name: str = "ppo"
    total_timesteps: int = 2e5
    n_epochs: int = 10 # number of epochs of updating ac networks
    lr: float = 0.001
    n_steps: int = 3000, # number of steps to update policy
    batch_size: int = 64,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
    ent_coef: float = 0.1,
    vf_coef: float = 0.5,
    device: str = "gpu",
    policy_network: str = None  # currently, we use existig model in stablebaselines, "MlpPloicy"
    actor_net_structure: List = [64, 64]  # policy network
    critic_net_structure: List = [64, 64]   # value network
    activation_function: nn.Module = nn.ReLU
    
    def __init__(self, RL_params: Dict[str, Any]) -> None:
        self.rl_model_name = RL_params["rl_model_name"]
        self.policy_network = RL_params["policy_network"]
        self.actor_net_structure = RL_params["actor_net_structure"]
        self.critic_net_structure = RL_params["critic_net_structure"]

        if RL_params["activation_function"] == "Sigmoid":
            self.activation_function = nn.Sigmoid
        elif RL_params["activation_function"] == "Tanh":
            self.activation_function = nn.Tanh
        else:
            self.activation_function = nn.ReLU
        
        self.total_timesteps = RL_params["total_timesteps"]
        self.lr = RL_params["learning_rate"]
        self.n_epochs = RL_params["n_epochs"]
        self.n_steps = RL_params["n_steps"]
        self.batch_size = RL_params["batch_size"]
        self.gamma = RL_params["gamma"]
        self.gae_lambda = RL_params["gae_lambda"]
        self.ent_coef = RL_params["ent_coef"]
        self.vf_coef = RL_params["vf_coef"]
        self.device = RL_params["device"]


class Params:
    """
    @brief Parameter class
    """
    def __init__(self):
        """
        @brief initialization
        """
        filename = os.path.join(os.path.dirname(__file__), 'params.json')
        if os.path.isfile(filename):
            params_dict = {}
            with open(filename, "r") as f:
                params_dict = json.load(f)
            
            self.env = EnvParams(params_dict["env"])
            self.rl = RLParams(params_dict["rl"])

        else:
            self.env = EnvParams()
            self.rl = RLParams()
