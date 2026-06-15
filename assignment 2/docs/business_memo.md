# Business Memo

**To:** Retail Operations Leadership  
**From:** Analytics Team  
**Subject:** Recommendation on learned inventory replenishment policy

## Decision

Do not deploy the learned Q-learning replenishment policy. Keep the reorder-point heuristic as the operating policy for this SKU.

The learned policy improves over a random ordering baseline, but it does not beat the realistic business benchmark. Across normal demand and stress scenarios, the reorder-point heuristic produces higher mean profit and more reliable service levels. The learned policy is especially weak during demand spikes, where poor replenishment decisions create materially more lost sales.

## Business Context

The replenishment problem is a daily inventory decision for one retail SKU over a 60-day selling season. Ordering too little creates stockouts, lost sales, and poor customer experience. Ordering too much ties up working capital and increases holding and end-of-season markdown costs. A useful automated policy must therefore improve profit without creating unacceptable service-level risk.

The business question for this assignment is whether a learned sequential decision policy should replace a simple reorder-point heuristic. Based on the current evidence, the answer is no.

## Method

The project evaluates three replenishment policies in a small inventory simulator:

- A random policy, used only as a sanity-check baseline.
- A reorder-point heuristic, which orders up to a target level when inventory position falls below a threshold.
- A tabular Q-learning policy, trained on the normal-demand simulator.

Each policy is evaluated over 250 seeded episodes in five scenarios: normal demand, demand spike, demand slump, supplier delay, and end-of-season pressure. The main metrics are mean episode profit, service level, stockout days, lost sales, ending inventory, holding cost, stockout cost, and terminal markdown loss.

## Evidence

The reorder-point heuristic is the strongest policy by mean profit in every evaluated scenario.

| Scenario | Reorder-point profit | Q-learning profit | Q-learning service level |
|---|---:|---:|---:|
| Normal demand | 3976.35 | 3734.07 | 0.7422 |
| Demand spike | 3881.67 | 2990.31 | 0.6351 |
| Demand slump | 3754.98 | 3360.22 | 0.7604 |
| Supplier delay | 3039.37 | 2869.95 | 0.6577 |
| End-season pressure | 3965.08 | 3690.37 | 0.7387 |

The normal-demand result is already enough to reject replacement: Q-learning earns about 242 less profit per episode than the reorder-point policy. The demand-spike scenario is more concerning. Under temporary high demand, Q-learning earns about 891 less profit than the heuristic and fulfills only about 63.5% of demand. This is the setting where a replenishment policy should protect availability, but the learned policy instead exposes the business to more stockouts.

The learned policy does appear to carry less inventory and incur lower holding and terminal markdown costs in several scenarios. That is not a sufficient win. The savings come with higher stockout exposure, lower service levels, and weaker edge-case behavior. For retail operations, a policy that saves inventory cost by missing too much demand is not ready for live automation.

A sensitivity check on the reorder-point heuristic further strengthens this conclusion. Nearby heuristic settings, especially a more aggressive reorder point and target level, can improve both profit and service level beyond the simple baseline used in the main comparison. The learned policy therefore does not only fail against one business rule; it fails against a class of simple, interpretable replenishment rules.

## Risks

The current learned policy creates several operational risks:

- **Reward hacking:** The policy may learn to protect simulated profit by under-ordering and accepting too many stockouts.
- **Service-level risk:** Profit can look acceptable while customer experience deteriorates through repeated stockouts.
- **Simulator overfitting:** The policy was trained in a simplified simulator, so its behavior may not transfer to real demand patterns, promotions, supplier disruptions, or seasonality.
- **Supplier delay exposure:** The policy does not show enough robustness when lead times increase.
- **Governance risk:** Automated ordering without guardrails could create repeated availability failures before managers notice the pattern.

## Recommendation and Next Steps

The learned Q-learning policy should be rejected for deployment. It should also not replace the heuristic in shadow mode yet, because it does not meet the basic standard of outperforming the current business rule across normal and edge scenarios.

The retailer should keep the reorder-point heuristic as the operating baseline and use the current experiment as a diagnostic tool. A future learned policy should only be reconsidered after it improves mean profit while maintaining service level and stockout behavior at least as strong as the heuristic.

Before any future shadow or live use, the policy should include clear governance controls: maximum order caps, minimum service-level guardrails, stockout alerts, monitoring for abnormal inventory positions, and human approval for unusual order recommendations. The reward design should also be revisited so that stockout penalties and service-level requirements better reflect the business cost of lost sales and poor customer experience.
