"""Generate assignment figures from saved training and evaluation outputs."""

from __future__ import annotations

import os

from . import config

MPLCONFIGDIR = config.ROOT_DIR / ".cache" / "matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from .agents import QLearningAgent


def save_reward_curve() -> None:
    rewards = pd.read_csv(config.RESULTS_DIR / "training_rewards.csv")
    rewards["rolling_reward"] = rewards["reward"].rolling(100, min_periods=1).mean()
    plt.figure(figsize=(9, 5))
    sns.lineplot(data=rewards, x="episode", y="reward", alpha=0.25, linewidth=0.7, label="Episode reward")
    sns.lineplot(data=rewards, x="episode", y="rolling_reward", linewidth=2, label="100-episode average")
    plt.title("Q-learning Training Reward")
    plt.xlabel("Training episode")
    plt.ylabel("Episode profit")
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "reward_curve.png", dpi=160)
    plt.close()


def save_baseline_comparison() -> None:
    metrics = pd.read_csv(config.RESULTS_DIR / "metrics.csv")
    normal = metrics[metrics["scenario"] == "normal"].copy()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    sns.barplot(data=normal, x="policy", y="profit_mean", ax=axes[0])
    axes[0].set_title("Mean Profit, Normal Demand")
    axes[0].set_xlabel("Policy")
    axes[0].set_ylabel("Profit")

    sns.barplot(data=normal, x="policy", y="service_level_mean", ax=axes[1])
    axes[1].set_title("Service Level, Normal Demand")
    axes[1].set_xlabel("Policy")
    axes[1].set_ylabel("Fulfilled demand share")
    axes[1].set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "baseline_comparison.png", dpi=160)
    plt.close()


def save_all_scenario_comparison() -> None:
    metrics = pd.read_csv(config.RESULTS_DIR / "metrics.csv")
    metrics["scenario"] = metrics["scenario"].str.replace("_", " ").str.title()

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    sns.barplot(data=metrics, x="scenario", y="profit_mean", hue="policy", ax=axes[0])
    axes[0].set_title("Mean Profit by Scenario")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Profit")
    axes[0].legend(title="Policy")

    sns.barplot(data=metrics, x="scenario", y="service_level_mean", hue="policy", ax=axes[1])
    axes[1].set_title("Service Level by Scenario")
    axes[1].set_xlabel("Scenario")
    axes[1].set_ylabel("Fulfilled demand share")
    axes[1].set_ylim(0, 1)
    axes[1].legend(title="Policy")

    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "all_scenario_policy_comparison.png", dpi=160)
    plt.close()


def save_cost_breakdown() -> None:
    metrics = pd.read_csv(config.RESULTS_DIR / "metrics.csv")
    normal = metrics[metrics["scenario"] == "normal"].copy()
    cost_columns = {
        "holding_cost_mean": "Holding cost",
        "stockout_cost_mean": "Stockout cost",
        "terminal_loss_mean": "Terminal markdown loss",
    }
    costs = normal[["policy", *cost_columns.keys()]].rename(columns=cost_columns)
    costs = costs.melt(id_vars="policy", var_name="Cost component", value_name="Mean cost")

    plt.figure(figsize=(9, 5))
    sns.barplot(data=costs, x="policy", y="Mean cost", hue="Cost component")
    plt.title("Normal-Demand Cost Breakdown")
    plt.xlabel("Policy")
    plt.ylabel("Mean episode cost")
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "cost_breakdown.png", dpi=160)
    plt.close()


def save_policy_heatmap() -> None:
    agent = QLearningAgent.load(config.RESULTS_DIR / "q_table.pkl")
    rows = []
    for inventory_bin in range(5):
        for demand_bin in range(4):
            state = (inventory_bin, 1, demand_bin, 0, 1)
            action = agent.act(state, explore=False)
            rows.append(
                {
                    "Inventory bin": inventory_bin,
                    "Recent demand bin": demand_bin,
                    "Preferred order": action,
                }
            )
    frame = pd.DataFrame(rows)
    pivot = frame.pivot(index="Recent demand bin", columns="Inventory bin", values="Preferred order")
    plt.figure(figsize=(7, 4.5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="viridis", cbar_kws={"label": "Order quantity"})
    plt.title("Learned Policy Behavior")
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "inventory_policy_heatmap.png", dpi=160)
    plt.close()


def save_edge_episode_behavior() -> None:
    logs = pd.read_csv(config.RESULTS_DIR / "episode_logs.csv")
    edge = logs[(logs["scenario"] == "demand_spike") & (logs["policy"] == "q_learning")].copy()
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=edge, x="day", y="demand", label="Demand")
    sns.lineplot(data=edge, x="day", y="ending_inventory", label="Ending inventory")
    sns.lineplot(data=edge, x="day", y="action", label="Order quantity")
    sns.lineplot(data=edge, x="day", y="lost_sales", label="Lost sales")
    plt.title("Q-learning Behavior During Demand Spike")
    plt.xlabel("Day")
    plt.tight_layout()
    plt.savefig(config.FIGURES_DIR / "edge_episode_behavior.png", dpi=160)
    plt.close()


def main() -> None:
    config.ensure_output_dirs()
    save_reward_curve()
    save_baseline_comparison()
    save_all_scenario_comparison()
    save_cost_breakdown()
    save_policy_heatmap()
    save_edge_episode_behavior()
    print(f"Saved figures to {config.FIGURES_DIR}")


if __name__ == "__main__":
    main()
