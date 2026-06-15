"""Shared training and evaluation helpers."""

from __future__ import annotations

from typing import Any

from . import config
from .agents import QLearningAgent, ReorderPointPolicy
from .inventory_env import RetailInventoryEnv


def policy_action(policy: Any, env: RetailInventoryEnv, state: tuple[int, ...], train: bool = False) -> int:
    if isinstance(policy, ReorderPointPolicy):
        inventory_position = env.inventory + sum(qty for _, qty in env.pipeline)
        return policy.act(state, inventory_position=inventory_position)
    if isinstance(policy, QLearningAgent):
        return policy.act(state, explore=train)
    return policy.act(state)


def run_episode(
    policy: Any,
    scenario: str,
    seed: int,
    train: bool = False,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    env = RetailInventoryEnv(scenario=scenario, seed=seed)
    state = env.reset(seed)
    done = False
    rows: list[dict[str, Any]] = []

    while not done:
        action = policy_action(policy, env, state, train=train)
        next_state, reward, done, info = env.step(action)
        if train and isinstance(policy, QLearningAgent):
            policy.update(state, action, reward, next_state, done)
        rows.append(info)
        state = next_state

    total_demand = sum(row["demand"] for row in rows)
    total_sales = sum(row["sales"] for row in rows)
    metrics = {
        "profit": sum(row["reward"] for row in rows),
        "service_level": total_sales / total_demand if total_demand else 1.0,
        "stockout_days": sum(1 for row in rows if row["lost_sales"] > 0),
        "lost_sales": sum(row["lost_sales"] for row in rows),
        "ending_inventory": rows[-1]["ending_inventory"],
        "holding_cost": sum(row["holding_cost"] for row in rows),
        "stockout_cost": sum(row["stockout_cost"] for row in rows),
        "terminal_loss": sum(row["terminal_loss"] for row in rows),
    }
    return metrics, rows


def seeded_episode_seed(base_seed: int, scenario_index: int, episode_index: int) -> int:
    return base_seed + scenario_index * 10_000 + episode_index

