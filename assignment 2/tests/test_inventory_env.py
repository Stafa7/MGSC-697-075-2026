from src import config
from src.inventory_env import RetailInventoryEnv
import pytest


def test_episode_runs_to_completion() -> None:
    env = RetailInventoryEnv(seed=config.SEED)
    state = env.reset()
    assert isinstance(state, tuple)

    done = False
    steps = 0
    while not done:
        state, reward, done, info = env.step(10)
        steps += 1
        assert isinstance(state, tuple)
        assert isinstance(reward, float)
        assert info["ending_inventory"] >= 0

    assert steps == config.EPISODE_LENGTH


def test_invalid_action_raises_value_error() -> None:
    env = RetailInventoryEnv(seed=config.SEED)
    env.reset()

    with pytest.raises(ValueError):
        env.step(7)


def test_fixed_seed_reproduces_episode_step() -> None:
    first = RetailInventoryEnv(seed=config.SEED)
    second = RetailInventoryEnv(seed=config.SEED)
    first.reset()
    second.reset()

    first_state, first_reward, first_done, first_info = first.step(10)
    second_state, second_reward, second_done, second_info = second.step(10)

    assert first_state == second_state
    assert first_reward == second_reward
    assert first_done == second_done
    assert first_info["demand"] == second_info["demand"]
    assert first_info["ending_inventory"] == second_info["ending_inventory"]


def test_supplier_delay_extends_lead_time_during_delay_window() -> None:
    env = RetailInventoryEnv(scenario="supplier_delay", seed=config.SEED)
    env.reset()

    env.day = 20

    assert env._lead_time() == 4


def test_terminal_markdown_loss_applies_on_final_day() -> None:
    env = RetailInventoryEnv(seed=config.SEED)
    env.reset()
    env.day = config.EPISODE_LENGTH - 1
    env.inventory = 10
    env._sample_demand = lambda: 0

    _, _, done, info = env.step(0)

    assert done
    assert info["terminal_loss"] == 10 * config.TERMINAL_MARKDOWN_LOSS
