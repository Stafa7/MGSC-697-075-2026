"""Small retail inventory replenishment simulator.

The environment is intentionally lightweight and deterministic under a seed.
It does not depend on Gymnasium because the assignment rewards clear MDP
framing over framework complexity.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from . import config


State = tuple[int, int, int, int, int]


@dataclass
class RetailInventoryEnv:
    """Finite-horizon single-SKU inventory environment."""

    scenario: str = "normal"
    seed: int = config.SEED
    episode_length: int = config.EPISODE_LENGTH
    rng: random.Random = field(init=False)
    day: int = field(init=False, default=0)
    inventory: int = field(init=False, default=config.INITIAL_INVENTORY)
    pipeline: list[tuple[int, int]] = field(init=False, default_factory=list)
    recent_demands: list[int] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if self.scenario not in config.SCENARIOS:
            raise ValueError(f"Unknown scenario: {self.scenario}")
        self.rng = random.Random(self.seed)

    def reset(self, seed: int | None = None) -> State:
        if seed is not None:
            self.seed = seed
        self.rng = random.Random(self.seed)
        self.day = 0
        self.inventory = config.INITIAL_INVENTORY
        self.pipeline = []
        self.recent_demands = [18, 18, 18]
        return self.state()

    def state(self) -> State:
        return (
            self._inventory_bin(self.inventory),
            self._pipeline_bin(sum(qty for _, qty in self.pipeline)),
            self._recent_demand_bin(sum(self.recent_demands[-3:]) / 3),
            self._day_type(),
            self._season_phase(),
        )

    def step(self, action: int) -> tuple[State, float, bool, dict[str, Any]]:
        if action not in config.ACTION_SPACE:
            raise ValueError(f"Action {action} is not in {config.ACTION_SPACE}")

        received = self._receive_due_orders()
        demand = self._sample_demand()
        sales = min(self.inventory, demand)
        lost_sales = max(0, demand - sales)
        self.inventory -= sales

        revenue = sales * config.SELL_PRICE
        purchase_cost = action * config.UNIT_COST
        fixed_order_cost = config.FIXED_ORDER_COST if action > 0 else 0.0
        holding_cost = self.inventory * config.HOLDING_COST
        stockout_cost = lost_sales * config.STOCKOUT_PENALTY

        if action > 0:
            self.pipeline.append((self._lead_time(), action))

        self.day += 1
        done = self.day >= self.episode_length
        terminal_loss = 0.0
        if done:
            terminal_loss = self.inventory * self._terminal_markdown_loss()

        reward = (
            revenue
            - purchase_cost
            - fixed_order_cost
            - holding_cost
            - stockout_cost
            - terminal_loss
        )

        self.recent_demands.append(demand)
        self._age_pipeline()

        info = {
            "day": self.day,
            "scenario": self.scenario,
            "action": action,
            "received": received,
            "demand": demand,
            "sales": sales,
            "lost_sales": lost_sales,
            "ending_inventory": self.inventory,
            "pipeline_inventory": sum(qty for _, qty in self.pipeline),
            "revenue": revenue,
            "purchase_cost": purchase_cost,
            "fixed_order_cost": fixed_order_cost,
            "holding_cost": holding_cost,
            "stockout_cost": stockout_cost,
            "terminal_loss": terminal_loss,
            "reward": reward,
            "service_level": sales / demand if demand else 1.0,
        }
        return self.state(), reward, done, info

    def _receive_due_orders(self) -> int:
        received = sum(qty for remaining, qty in self.pipeline if remaining <= 0)
        self.pipeline = [(remaining, qty) for remaining, qty in self.pipeline if remaining > 0]
        self.inventory = min(config.MAX_INVENTORY, self.inventory + received)
        return received

    def _age_pipeline(self) -> None:
        self.pipeline = [(remaining - 1, qty) for remaining, qty in self.pipeline]

    def _sample_demand(self) -> int:
        mean = 26 if self._day_type() == 1 else 18
        if self.scenario == "demand_spike" and 20 <= self.day <= 29:
            mean *= 1.7
        elif self.scenario == "demand_slump" and 20 <= self.day <= 34:
            mean *= 0.55
        demand = self.rng.gauss(mean, 4.5)
        return max(0, int(round(demand)))

    def _lead_time(self) -> int:
        if self.scenario == "supplier_delay" and 15 <= self.day <= 34:
            return 4
        return config.BASE_LEAD_TIME

    def _terminal_markdown_loss(self) -> float:
        if self.scenario == "end_season_pressure":
            return config.END_SEASON_TERMINAL_MARKDOWN_LOSS
        return config.TERMINAL_MARKDOWN_LOSS

    def _day_type(self) -> int:
        return 1 if self.day % 7 in (5, 6) else 0

    def _season_phase(self) -> int:
        if self.day < self.episode_length / 3:
            return 0
        if self.day < 2 * self.episode_length / 3:
            return 1
        return 2

    @staticmethod
    def _inventory_bin(value: int) -> int:
        if value <= 10:
            return 0
        if value <= 25:
            return 1
        if value <= 45:
            return 2
        if value <= 70:
            return 3
        return 4

    @staticmethod
    def _pipeline_bin(value: int) -> int:
        if value == 0:
            return 0
        if value <= 20:
            return 1
        if value <= 45:
            return 2
        return 3

    @staticmethod
    def _recent_demand_bin(value: float) -> int:
        if value <= 14:
            return 0
        if value <= 22:
            return 1
        if value <= 30:
            return 2
        return 3

