import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from rl_environment import RLTradingEnv
from config import RL_CHECKPOINT_PATH
import os

ray.init(ignore_reinit_error=True)

def train():
    env_config = {"symbol": "BTC", "window_size": 20}

    config = (
        PPOConfig()
        .environment(RLTradingEnv, env_config=env_config)
        .rollouts(num_rollout_workers=2)
        .framework("torch")
        .training(
            lr=3e-4,
            train_batch_size=4000,
            gamma=0.99,
        )
        .resources(num_gpus=int(os.getenv("USE_GPU", 0)))
    )

    stopper = tune.stopper.MaximumIterationStopper(max_iter=100)

    tuner = tune.Tuner(
        "PPO",
        param_space=config.to_dict(),
        run_config=tune.RunConfig(stop=stopper, checkpoint_config=tune.CheckpointConfig(checkpoint_at_end=True)),
        tune_config=tune.TuneConfig(metric="episode_reward_mean", mode="max")
    )

    results = tuner.fit()
    best_checkpoint = results.get_best_result().checkpoint
    best_checkpoint.to_directory(RL_CHECKPOINT_PATH)
    print(f"Best model saved to {RL_CHECKPOINT_PATH}")

if __name__ == "__main__":
    os.makedirs("checkpoints/PPO", exist_ok=True)
    train()