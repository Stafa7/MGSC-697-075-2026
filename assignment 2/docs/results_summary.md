# Results Summary

Run the project commands from the Assignment 2 root folder:

```bash
python -m src.train
python -m src.evaluate
python -m src.plots
```

The current run evaluates three main policies: random ordering, a reorder-point heuristic, and tabular Q-learning. Each policy is evaluated over 250 seeded episodes in five scenarios. The reorder-point heuristic is the relevant business baseline because it resembles a simple replenishment rule a retailer could actually operate.

## Main Policy Comparison

The learned Q-learning policy beats the random baseline in most settings, but it does not beat the reorder-point heuristic. The table reports mean episode profit, standard deviation, and the profit gap between the heuristic and Q-learning.

| Scenario | Reorder profit, mean +/- std | Q-learning profit, mean +/- std | Heuristic profit gap | Reorder service | Q-learning service |
|---|---:|---:|---:|---:|---:|
| Normal demand | 3976.35 +/- 171.32 | 3734.07 +/- 358.14 | 242.28 | 0.7505 | 0.7422 |
| Demand spike | 3881.67 +/- 170.37 | 2990.31 +/- 349.61 | 891.36 | 0.6985 | 0.6351 |
| Demand slump | 3754.98 +/- 180.09 | 3360.22 +/- 399.02 | 394.76 | 0.7850 | 0.7604 |
| Supplier delay | 3039.37 +/- 155.02 | 2869.95 +/- 304.50 | 169.42 | 0.6584 | 0.6577 |
| End-season pressure | 3965.08 +/- 165.42 | 3690.37 +/- 326.00 | 274.71 | 0.7495 | 0.7387 |

Q-learning also has higher profit variability than the heuristic in every scenario. That matters operationally: even if the average performance were close, the learned policy is less stable.

## Behavior Interpretation

The learned policy appears to understock relative to the heuristic. In normal demand, Q-learning has lower holding cost than the reorder-point policy, but the savings do not compensate for stockout exposure:

| Policy | Holding cost | Stockout cost | Terminal loss | Stockout days |
|---|---:|---:|---:|---:|
| Random | 95.81 | 1224.77 | 23.18 | 34.66 |
| Reorder-point | 148.40 | 904.40 | 26.91 | 24.33 |
| Q-learning | 77.49 | 934.21 | 18.10 | 31.48 |

This is the key tradeoff. Q-learning carries less inventory and has lower terminal loss, but it stocks out more often than the heuristic. The result is lower profit and worse operational reliability. The demand-spike episode makes this failure mode visible: the learned policy fulfills only about 63.5% of demand and loses about 891 profit per episode versus the heuristic.

## Heuristic Sensitivity

The selected reorder-point baseline uses reorder point 35 and target level 60. A sensitivity check in `results/heuristic_sensitivity.csv` compares several nearby heuristic settings. Averaged across all five scenarios, the more aggressive `(45, 70)` setting has the highest mean profit and service level:

| Reorder point | Target level | Avg. profit | Avg. service level | Avg. stockout days |
|---:|---:|---:|---:|---:|
| 45 | 70 | 4533.52 | 0.8163 | 18.50 |
| 40 | 65 | 4110.45 | 0.7700 | 21.76 |
| 35 | 60 | 3723.49 | 0.7284 | 24.90 |
| 30 | 55 | 1467.95 | 0.4960 | 37.56 |
| 25 | 45 | 1420.74 | 0.4946 | 38.51 |

This strengthens the business conclusion. The learned policy does not merely lose to one arbitrary heuristic; it loses to the selected heuristic, and simple tuning of that heuristic can produce even stronger business performance.

## Generated Artifacts

- `results/metrics.csv`: aggregate policy performance by scenario.
- `results/heuristic_sensitivity.csv`: reorder-point parameter sensitivity.
- `results/episode_logs.csv`: representative daily episode logs.
- `figures/reward_curve.png`: training reward curve.
- `figures/baseline_comparison.png`: normal-demand policy comparison.
- `figures/all_scenario_policy_comparison.png`: profit and service across all scenarios.
- `figures/cost_breakdown.png`: normal-demand holding, stockout, and terminal costs.
- `figures/inventory_policy_heatmap.png`: learned policy behavior.
- `figures/edge_episode_behavior.png`: demand-spike trajectory.

## Recommendation

The learned Q-learning policy should not be deployed. It should also not replace the heuristic in shadow mode yet, because it does not meet the minimum standard of outperforming a realistic business rule across normal and edge scenarios. The operating recommendation is to keep a reorder-point heuristic and only reconsider a learned policy after it improves profit, service level, stockout behavior, and edge-case robustness against tuned heuristic baselines.
