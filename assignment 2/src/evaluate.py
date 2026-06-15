"""Evaluate random, heuristic, and learned replenishment policies."""

from __future__ import annotations

import csv
import statistics

from . import config
from .agents import QLearningAgent, RandomPolicy, ReorderPointPolicy
from .simulation import run_episode, seeded_episode_seed


METRIC_FIELDS = [
    "profit",
    "service_level",
    "stockout_days",
    "lost_sales",
    "ending_inventory",
    "holding_cost",
    "stockout_cost",
    "terminal_loss",
]

HEURISTIC_CANDIDATES = (
    (25, 45),
    (30, 55),
    (35, 60),
    (40, 65),
    (45, 70),
)


def summarize(values: list[float]) -> tuple[float, float]:
    mean = statistics.fmean(values)
    std = statistics.stdev(values) if len(values) > 1 else 0.0
    return mean, std


def evaluate_heuristic_sensitivity() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for reorder_point, target_level in HEURISTIC_CANDIDATES:
        policy = ReorderPointPolicy(reorder_point=reorder_point, target_level=target_level)
        for scenario_index, scenario in enumerate(config.SCENARIOS):
            profits: list[float] = []
            service_levels: list[float] = []
            stockout_days: list[float] = []
            for episode in range(config.EVAL_EPISODES):
                seed = seeded_episode_seed(config.SEED, scenario_index, episode)
                metrics, _ = run_episode(policy, scenario=scenario, seed=seed, train=False)
                profits.append(metrics["profit"])
                service_levels.append(metrics["service_level"])
                stockout_days.append(metrics["stockout_days"])

            profit_mean, profit_std = summarize(profits)
            service_mean, service_std = summarize(service_levels)
            stockout_mean, stockout_std = summarize(stockout_days)
            rows.append(
                {
                    "scenario": scenario,
                    "reorder_point": reorder_point,
                    "target_level": target_level,
                    "profit_mean": round(profit_mean, 4),
                    "profit_std": round(profit_std, 4),
                    "service_level_mean": round(service_mean, 4),
                    "service_level_std": round(service_std, 4),
                    "stockout_days_mean": round(stockout_mean, 4),
                    "stockout_days_std": round(stockout_std, 4),
                }
            )
    return rows


def main() -> None:
    config.ensure_output_dirs()
    q_path = config.RESULTS_DIR / "q_table.pkl"
    if not q_path.exists():
        raise FileNotFoundError("Run `python -m src.train` before evaluation.")

    policies = [
        RandomPolicy(seed=config.SEED),
        ReorderPointPolicy(),
        QLearningAgent.load(q_path),
    ]

    metrics_rows: list[dict[str, object]] = []
    episode_log_rows: list[dict[str, object]] = []

    for scenario_index, scenario in enumerate(config.SCENARIOS):
        for policy in policies:
            collected: dict[str, list[float]] = {field: [] for field in METRIC_FIELDS}
            for episode in range(config.EVAL_EPISODES):
                seed = seeded_episode_seed(config.SEED, scenario_index, episode)
                metrics, logs = run_episode(policy, scenario=scenario, seed=seed, train=False)
                for field in METRIC_FIELDS:
                    collected[field].append(metrics[field])
                if episode == 0:
                    for row in logs:
                        episode_log_rows.append({"policy": policy.name, **row})

            summary: dict[str, object] = {"scenario": scenario, "policy": policy.name}
            for field in METRIC_FIELDS:
                mean, std = summarize(collected[field])
                summary[f"{field}_mean"] = round(mean, 4)
                summary[f"{field}_std"] = round(std, 4)
            metrics_rows.append(summary)

    metrics_path = config.RESULTS_DIR / "metrics.csv"
    with metrics_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(metrics_rows[0].keys()))
        writer.writeheader()
        writer.writerows(metrics_rows)

    logs_path = config.RESULTS_DIR / "episode_logs.csv"
    with logs_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(episode_log_rows[0].keys()))
        writer.writeheader()
        writer.writerows(episode_log_rows)

    sensitivity_rows = evaluate_heuristic_sensitivity()
    sensitivity_path = config.RESULTS_DIR / "heuristic_sensitivity.csv"
    with sensitivity_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(sensitivity_rows[0].keys()))
        writer.writeheader()
        writer.writerows(sensitivity_rows)

    print(f"Saved evaluation metrics to {metrics_path}")
    print(f"Saved representative episode logs to {logs_path}")
    print(f"Saved heuristic sensitivity results to {sensitivity_path}")


if __name__ == "__main__":
    main()
