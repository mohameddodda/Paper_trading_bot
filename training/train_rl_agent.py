# Copyright 2026 Mohamed Dodda
#
# Licensed under the Apache License, Version 2.0 (the \"License\");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an \"AS IS\" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python3
\"\"\"train_rl_agent.py - RL Agent Training with PPO
==================================================

Trains PPO agent on RLTradingEnv for paper trading.
Saves policy to checkpoints/rl_ppo_policy.zip

Requires: pip install stable-baselines3[extra] gymnasium
\"\"\"

import os
import sys
import logging
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SYMBOLS
from training.rl_environment import RLTradingEnv
from pathlib import Path

# Paths
MODEL_PATH = Path(__file__).parent.parent / \"checkpoints\" / \"rl_ppo_policy.zip\"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def train_rl_agent(symbol=SYMBOLS[0] if SYMBOLS else \"BTC_USDT\", total_timesteps=50000):
    \"\"\"Train PPO agent on RLTradingEnv.\"\"\"

    # Create vectorized env
    env = make_vec_env(lambda: RLTradingEnv(symbol=symbol), n_envs=4)

    # Callbacks
    eval_env = RLTradingEnv(symbol=symbol)
    eval_callback = EvalCallback(eval_env, best_model_save_path=str(MODEL_PATH.parent),
                                 log_path=str(MODEL_PATH.parent / \"evaluations/\"), 
                                 eval_freq=1000,
                                 deterministic=True, render=False)

    # Train PPO
    model = PPO(\"MlpPolicy\", env, verbose=1, tensorboard_log=str(MODEL_PATH.parent / \"tb_logs/\"), 
                learning_rate=3e-4, n_steps=2048, batch_size=64)
    
    model.learn(total_timesteps=total_timesteps, callback=eval_callback, progress_bar=True)

    # Final save
    model.save(str(MODEL_PATH))
    log.info(f\"✅ PPO policy saved to {MODEL_PATH}\")

    # Test episode
    obs, _ = eval_env.reset()
    done = False
    total_reward = 0
    while not done:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, _, info = eval_env.step(action)
        total_reward += reward
        eval_env.render()
    
    log.info(f\"Test episode reward: {total_reward:.4f}\")
    env.close()
    eval_env.close()

if __name__ == \"__main__\":
    print(\"🚀 Training RL Agent (PPO) for Paper Trading...\")
    train_rl_agent()
