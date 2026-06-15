"""Train the tabular Q-learning inventory replenishment agent."""

from __future__ import annotations

import csv
import time

from . import config
from .agents import QLearningAgent
from .simulation import run_episode


def main() -> None:
    config.ensure_output_dirs()
    start = time.perf_counter()
    agent = QLearningAgent(seed=config.SEED)
    reward_path = config.RESULTS_DIR / "training_rewards.csv"

    with reward_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["episode", "reward", "epsilon"])
        writer.writeheader()
        for episode in range(1, config.TRAINING_EPISODES + 1):
            metrics, _ = run_episode(
                agent,
                scenario="normal",
                seed=config.SEED + episode,
                train=True,
            )
            agent.decay_epsilon()
            writer.writerow(
                {
                    "episode": episode,
                    "reward": round(metrics["profit"], 4),
                    "epsilon": round(agent.epsilon, 6),
                }
            )

    q_path = config.RESULTS_DIR / "q_table.pkl"
    agent.save(q_path)
    elapsed = time.perf_counter() - start
    print(f"Saved Q-table to {q_path}")
    print(f"Saved training rewards to {reward_path}")
    print(f"Training completed in {elapsed:.2f} seconds on CPU.")


if __name__ == "__main__":
    main()

