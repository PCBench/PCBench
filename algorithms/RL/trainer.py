from stable_baselines3 import PPO, A2C
from RLEnv.PCBEnvPos import PCBEnvPos
from Algorithms.RL.params import Params

class Trainer:
    def __init__(self) -> None:
        self.params = Params()
        self.env = PCBEnvPos(
            resolution=self.params.env.resolution, 
            pcb_folder=self.params.env.benchmark_folder,
            pcb_names=self.params.env.pcb_names
        )

        self._build()
    
    def _build(self) -> None:

        policy_kwargs = dict(activation_fn=self.params.rl.activation_function,
                     net_arch=dict(pi=self.params.rl.actor_net_structure, vf=self.params.rl.critic_net_structure))
        
        if self.params.rl.rl_model_name == "a2c":
            self.model = A2C(
                policy=self.params.rl.policy_network, 
                env=self.env, 
                policy_kwargs=policy_kwargs, 
                verbose=1)
        else:
            # default model is PPO
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
    
    def learn(self) -> None:
        self.model.learn(total_timesteps=self.params.rl.total_timesteps, progress_bar=True)

if __name__ == "__main__":
    trainer = Trainer()
    trainer.learn()