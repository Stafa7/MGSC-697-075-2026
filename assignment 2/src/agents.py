"""Baseline and Q-learning agents."""

from __future__ import annotations

import pickle
import random
from collections import defaultdict
from pathlib import Path

from . import config
from .inventory_env import State


class RandomPolicy:
    name = "random"

    def __init__(self, seed: int = config.SEED) -> None:
        self.rng = random.Random(seed)

    def act(self, state: State) -> int:
        return self.rng.choice(config.ACTION_SPACE)


class ReorderPointPolicy:
    name = "reorder_point"

    def __init__(self, reorder_point: int = 35, target_level: int = 60) -> None:
        self.reorder_point = reorder_point
        self.target_level = target_level

    def act_from_inventory_position(self, inventory_position: int) -> int:
        if inventory_position >= self.reorder_point:
            return 0
        needed = max(0, self.target_level - inventory_position)
        return min(config.ACTION_SPACE, key=lambda action: abs(action - needed))

    def act(self, state: State, inventory_position: int | None = None) -> int:
        if inventory_position is None:
            inventory_position = 0
        return self.act_from_inventory_position(inventory_position)


class QLearningAgent:
    name = "q_learning"

    def __init__(
        self,
        alpha: float = config.Q_ALPHA,
        gamma: float = config.Q_GAMMA,
        epsilon: float = config.EPSILON_START,
        seed: int = config.SEED,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = random.Random(seed)
        self.q: defaultdict[State, dict[int, float]] = defaultdict(
            lambda: {action: 0.0 for action in config.ACTION_SPACE}
        )

    def act(self, state: State, explore: bool = True) -> int:
        if explore and self.rng.random() < self.epsilon:
            return self.rng.choice(config.ACTION_SPACE)
        values = self.q[state]
        best_value = max(values.values())
        best_actions = [action for action, value in values.items() if value == best_value]
        return min(best_actions)

    def update(self, state: State, action: int, reward: float, next_state: State, done: bool) -> None:
        next_best = 0.0 if done else max(self.q[next_state].values())
        target = reward + self.gamma * next_best
        self.q[state][action] += self.alpha * (target - self.q[state][action])

    def decay_epsilon(self) -> None:
        self.epsilon = max(config.EPSILON_MIN, self.epsilon * config.EPSILON_DECAY)

    def save(self, path: Path) -> None:
        with path.open("wb") as file:
            pickle.dump(dict(self.q), file)

    @classmethod
    def load(cls, path: Path) -> "QLearningAgent":
        agent = cls(epsilon=0.0)
        with path.open("rb") as file:
            raw_q = pickle.load(file)
        agent.q.update(raw_q)
        return agent

