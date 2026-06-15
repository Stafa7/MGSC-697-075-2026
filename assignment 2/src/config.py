"""Shared configuration for the Assignment 2 inventory simulator."""

from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "results"
FIGURES_DIR = ROOT_DIR / "figures"

SEED = 6972
EPISODE_LENGTH = 60
TRAINING_EPISODES = 5000
EVAL_EPISODES = 250

ACTION_SPACE = (0, 5, 10, 15, 20, 30)
MAX_INVENTORY = 100
INITIAL_INVENTORY = 25
BASE_LEAD_TIME = 2

SELL_PRICE = 12.0
UNIT_COST = 6.0
FIXED_ORDER_COST = 10.0
HOLDING_COST = 0.35
STOCKOUT_PENALTY = 3.0
TERMINAL_MARKDOWN_LOSS = 4.0
END_SEASON_TERMINAL_MARKDOWN_LOSS = 7.0

Q_ALPHA = 0.10
Q_GAMMA = 0.95
EPSILON_START = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995

SCENARIOS = (
    "normal",
    "demand_spike",
    "demand_slump",
    "supplier_delay",
    "end_season_pressure",
)


def ensure_output_dirs() -> None:
    """Create generated-output folders if they do not already exist."""
    RESULTS_DIR.mkdir(exist_ok=True)
    FIGURES_DIR.mkdir(exist_ok=True)

