# Assignment 2: Sequential Decision Agent for Retail Replenishment

## 1. Project Overview

This project builds a small retail inventory replenishment simulator and trains a sequential decision agent to manage daily order quantities for one SKU. The main goal is to compare a learned **tabular Q-learning** policy against simple baselines and decide whether the learned policy is ready for deployment, shadow testing, or rejection.

The project is intentionally lightweight. It is designed to run on CPU from a fresh clone using a local virtual environment.

## 2. Assignment Requirements Covered

- **Problem framing**: state, action, reward, transition, and horizon are documented below.
- **Baseline**: random policy and reorder-point heuristic.
- **Learning agent**: tabular Q-learning.
- **Evaluation against baseline**: normal demand plus edge scenarios.
- **Plots**: reward curve, baseline comparisons, all-scenario comparison, cost breakdown, policy heatmap, and edge-episode behavior.
- **Failure analysis**: reward hacking, unsafe stockouts, overstocking, simulator overfitting, and governance.
- **Business memo**: final deployment recommendation in [docs/business_memo.md](docs/business_memo.md).

## 3. Repository Structure

This repository folder is self-contained for Assignment 2. It does not depend on Assignment 1, even if both assignments live under the same course folder.

```text
.
|-- README.md
|-- requirements.txt
|-- docs/
|   |-- assignment_2_instructions.md
|   |-- assignment_2_plan.md
|   |-- business_memo.md
|   `-- results_summary.md
|-- src/
|   |-- config.py
|   |-- inventory_env.py
|   |-- agents.py
|   |-- simulation.py
|   |-- train.py
|   |-- evaluate.py
|   `-- plots.py
|-- tests/
|   `-- test_inventory_env.py
|-- results/
|   |-- training_rewards.csv
|   |-- metrics.csv
|   |-- heuristic_sensitivity.csv
|   |-- episode_logs.csv
|   `-- q_table.pkl
`-- figures/
    |-- reward_curve.png
    |-- baseline_comparison.png
    |-- all_scenario_policy_comparison.png
    |-- cost_breakdown.png
    |-- inventory_policy_heatmap.png
    `-- edge_episode_behavior.png
```

`results/` and `figures/` are generated outputs. They are ignored by Git so the source tree stays clean, but the full set of artifacts can be regenerated with the commands in the run section. If submitting as a ZIP, these generated folders may be included after running the project commands.

## 4. Environment Setup

Use a virtual environment local to this Assignment 2 folder only:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The environment folder is named `.venv/` and is ignored by Git. Do not commit it.

Python 3.11 or newer is expected. This repo was verified locally with Python 3.12.11.

## 5. How to Run

Run these commands from the Assignment 2 root folder:

```bash
python -m src.train
python -m src.evaluate
python -m src.plots
```

Optional test command:

```bash
python -m pytest
```

## 6. Reproducibility Notes

- Random seeds are fixed in [src/config.py](src/config.py).
- Trained artifacts are saved in `results/`, including `q_table.pkl`.
- Evaluation metrics are saved to `results/metrics.csv`.
- Reorder-point sensitivity results are saved to `results/heuristic_sensitivity.csv`.
- Representative daily episode logs are saved to `results/episode_logs.csv`.
- Generated plots are saved in `figures/`.
- Training is expected to run on CPU in under 10-15 minutes on a normal laptop.
- **No GPU is required.**
- **CUDA/MPS/Metal acceleration is intentionally not used because the selected Q-learning implementation is tabular and lightweight.**

## 7. MDP Design

The domain is retail inventory replenishment for one SKU over a 60-day selling season.

**State**

The state is a compact tuple:

```text
(
  inventory_bin,
  pipeline_bin,
  recent_demand_bin,
  day_type,
  season_phase
)
```

- `inventory_bin`: bucketed on-hand inventory.
- `pipeline_bin`: bucketed outstanding orders not yet delivered.
- `recent_demand_bin`: bucketed trailing average demand.
- `day_type`: weekday or weekend/high-traffic day.
- `season_phase`: early, middle, or late episode.

**Action**

The agent chooses a daily order quantity:

```text
{0, 5, 10, 15, 20, 30}
```

**Reward**

Daily reward approximates operating profit:

```text
sales_revenue
- purchase_cost
- fixed_order_cost
- holding_cost
- stockout_penalty
- terminal_markdown_loss
```

This reward encourages profit while penalizing stockouts, excess inventory, and end-of-season leftovers.

**Transition**

Each simulated day:

1. Due supplier orders arrive.
2. The policy chooses an order quantity.
3. Demand is sampled based on day type and scenario.
4. Sales, lost sales, inventory, costs, and reward are calculated.
5. New orders enter the delivery pipeline.
6. The day advances.

**Horizon**

Each episode lasts 60 simulated days.

## 8. Agents

The project evaluates three policies:

- **Random baseline**: randomly samples allowed order quantities.
- **Reorder-point heuristic**: orders up to a target level when inventory position drops below a threshold.
- **Tabular Q-learning agent**: learns state-action values with epsilon-greedy exploration.

The reorder-point heuristic is the primary business baseline because it resembles a practical replenishment rule.

## 9. Evaluation

Each policy is evaluated across the same seeded scenarios:

- **Normal demand**: demand matches the training distribution.
- **Demand spike**: a temporary increase in demand tests stockout recovery.
- **Demand slump**: a temporary decrease in demand tests overstock risk.
- **Supplier delay**: longer lead times test pipeline robustness.
- **End-of-season pressure**: higher terminal markdown cost tests late-season ordering discipline.

Primary metrics:

- Mean episode profit.
- Service level.
- Stockout days.
- Lost sales.
- Ending inventory.
- Holding cost.
- Stockout cost.
- Terminal markdown loss.

## 10. Results and Plots

After running the project, inspect:

- `results/metrics.csv` for aggregate results.
- `results/heuristic_sensitivity.csv` for reorder-point parameter checks.
- `results/episode_logs.csv` for representative daily behavior.
- `figures/reward_curve.png` for learning progress.
- `figures/baseline_comparison.png` for normal-demand policy comparison.
- `figures/all_scenario_policy_comparison.png` for profit and service level across all scenarios.
- `figures/cost_breakdown.png` for normal-demand holding, stockout, and terminal costs.
- `figures/inventory_policy_heatmap.png` for learned order behavior.
- `figures/edge_episode_behavior.png` for demand-spike behavior.

Summarize the final interpretation in [docs/results_summary.md](docs/results_summary.md).

Current generated results show that the reorder-point heuristic is the strongest policy by mean profit across all evaluated scenarios:

| Scenario | Reorder-point profit | Q-learning profit | Profit gap | Q-learning service level |
|---|---:|---:|---:|---:|
| Normal demand | 3976.35 | 3734.07 | 242.28 | 0.7422 |
| Demand spike | 3881.67 | 2990.31 | 891.36 | 0.6351 |
| Demand slump | 3754.98 | 3360.22 | 394.76 | 0.7604 |
| Supplier delay | 3039.37 | 2869.95 | 169.42 | 0.6577 |
| End-season pressure | 3965.08 | 3690.37 | 274.71 | 0.7387 |

The learned policy beats the random baseline in most settings, but it does not beat the operationally relevant reorder-point heuristic. Its main pattern is lower inventory carrying cost with higher stockout exposure. In normal demand, Q-learning has lower holding cost than the heuristic, but it also has more stockout days and lower profit. During the demand-spike scenario, the policy fulfills only about 63.5% of demand, which is not acceptable for deployment.

The heuristic sensitivity output checks several reorder-point and target-level settings. The selected reorder-point baseline is intentionally simple, but the sensitivity check helps show that the comparison is against a reasonable business rule rather than an arbitrary weak baseline.

## 11. Failure Analysis and Governance

Important risks:

- **Reward hacking**: if stockout penalties are too low, the agent may understock to avoid holding costs.
- **Unsafe stockout behavior**: high profit can still be unacceptable if service level drops too far.
- **Overstocking**: the agent may over-order to avoid stockouts, creating waste and markdown losses.
- **Simulator overfitting**: the learned policy may exploit assumptions that do not hold in production.
- **Supplier instability**: real lead times may be less reliable than simulated lead times.
- **Baseline sensitivity**: a learned policy should beat more than one plausible heuristic setting before deployment is considered.

Recommended safeguards:

- Shadow mode before live deployment.
- Maximum order caps.
- Service-level monitoring.
- Alerts for repeated stockouts or abnormal inventory.
- Human approval for unusual orders.
- Periodic recalibration against recent demand and supplier performance.

## 12. Business Recommendation

The current recommendation is **reject deployment of the learned Q-learning policy** and keep the reorder-point heuristic as the operating baseline. The learned policy beats the random baseline in most settings, but it does not beat the realistic heuristic benchmark and performs poorly during the demand-spike edge case. A future learned policy should only move to shadow mode after it improves profit while maintaining service level, stockout behavior, and inventory risk at least as well as the heuristic across normal and edge scenarios.
