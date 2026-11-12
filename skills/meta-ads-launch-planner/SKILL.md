---
name: meta-ads-launch-planner
description: Plan and set up a Meta (Facebook/Instagram) sales campaign launch that exits the learning phase without wasting budget. Calculates the budget from target CPA × 50 events/week, picks the structure (CBO, one broad ad set), writes day-by-day decision rules, creates automated stop/restart rules, a scaling schedule and a relaunch playbook, and turns it into a launch plan document for a client or manager. Use for "meta ads launch plan", "how much budget to exit learning phase", "how to scale facebook ads without resetting learning", "facebook automated rules", "CBO vs ABO", "advantage+ sales campaign setup", or when a stakeholder asks for stop conditions and a clear action plan.
---

# Meta Ads launch and scaling planner

Output: a launch plan the team can follow without a meeting, and (if access is given) the campaign built in Ads Manager, switched **off** so the owner launches it.

## 1. Inputs
Ask once, in one message:
- Target or historical CPA, and currency.
- Optimization event (Purchase, StartTrial, Lead) and daily events the pixel sees from all traffic.
- Total budget the client accepts for the test period.
- Proven creatives from history (or run `meta-ads-learning-audit` first) and new creatives to test.
- Constraints: special ad category, countries, exclusions (recent purchasers), who approves the launch.

## 2. Budget math (show the numbers)
```
learning_budget_per_day = target_CPA × 50 / 7
day1_budget             = learning_budget_per_day / 2   (when the client wants a cautious start)
checkpoint_events       = 5 purchases after day 1 (or after ~2× target CPA × 5 spent)
max_exposure            = spend until the first real stop decision
```
Example: CPA $38 → $271/day to learn → round to ~10 purchases/day = $380. Cautious start: $190 on day 1, $380 from day 2 if 5+ purchases. Worst case before stopping: ~$380 over 2 days.

Use `scripts/budget.py` (below) to print the table for several CPA scenarios. Always show the CPA sensitivity: purchases/day at CPA ±30%.

## 3. Structure (default, explain trade-offs only if asked)
- **One campaign, CBO, one broad ad set** (country, 18 to 65+, all genders, Advantage+ audience), static and video together. All purchases build up in one place; with ~70 purchases/week one ad set clears 50, two would sit at ~35 each.
- Exclude purchasers of the last 180 days (custom audience) for subscription products.
- 6 to 12 creatives: proven winners by purchases and CPA + a new batch. One ad per creative, clear names: `PROJECT | TOPn | Format | Concept | src: original_ad`.
- Placements automatic. Ad-set level placement/OS exclusions are being deprecated; use account controls if needed.
- Special ad category: check the client's vertical (employment, housing, credit) before launch; it changes targeting limits.

## 4. Automated rules (create all three)
| Rule | Scope | Condition | Action |
|---|---|---|---|
| STOP no-buy | Active ads in this campaign | Lifetime spend ≥ 2× target CPA and purchases = 0 | Turn off ad |
| STOP expensive | Active ads in this campaign | Lifetime spend > ~4× target CPA and purchases < 3 | Turn off ad |
| START late buyer | Selected ads (paused ones) | Last 3 days: purchases ≥ 2 and spend < 2× target CPA | Turn on ad |

Notes from practice:
- Inside CBO, Meta blocks cost-per-result conditions for on/off rules on ads. Use spend + purchase counts.
- "Active ads in campaign" scope picks up new ads automatically. The START rule must target selected ads (paused ads are not "active"), so re-apply it whenever ads are added or replaced; rules keep IDs of deleted ads.
- Check the account for other rules that pause campaigns on a schedule. They break learning.

## 5. Day-by-day plan (put it in the doc as a table)
| When | Budget / spent so far | Check and action |
|---|---|---|
| Day 0 | $0 | Old campaign off at launch, test purchase hits the pixel, rules and exclusions on |
| Day 1 | ½ learning budget | Midday: 0 purchases at ~½ day budget → check tracking. End: 5+ → full budget from day 2; 1 to 4 → one more day |
| Day 2 | Full (or ½) | Still <5 purchases after ~2 days of ½ budget → stop, old campaign back on, fix funnel |
| Days 3 to 4 | Full | No edits. Rules handle weak ads. Day 4: ≥7/day → plan scaling |
| Days 5 to 7 | +20 to 30% every 2 to 3 days | Only while CPA ≤ target. CPA > 1.3× target for 3 days → roll back |
| Week 2+ | Step by step | 50+/week, new creative batch weekly, all changes on one day |

## 6. Relaunch playbook (include it, stakeholders always ask)
| Problem | Signal | Action |
|---|---|---|
| Tracking broken | 0 purchases in Ads Manager, sales in backend | Pause, fix pixel/CAPI, test purchase, restart same campaign |
| Weak start | < 5 purchases at the checkpoint | Stop, previous campaign back on, audit funnel, relaunch with top-3 ads |
| Rules switched off most ads | < 3 active ads | Add next creative batch to the same ad set |
| Ad rejected | Status Rejected | Edit and upload as a new ad, appeal in parallel |
| CPA up after scaling | CPA > 1.3× target 3 days | Roll back to last good budget, wait 3 days |
| Creative fatigue | Frequency > 3, CTR down, CPA up | New creatives in the same ad set |
| Campaign stuck | CPA 2× target 5+ days after fixes | Duplicate with best 3 to 5 ads, old one off |

Principle: one bad day never justifies rebuilding the campaign.

## 7. Building in Ads Manager (if access is given)
- Work through the UI or a Meta Ads MCP connector. Duplicate proven ads into the new ad set with "Existing campaign → Existing ad set"; "Original campaign" duplicates into the source ad set.
- If an Instagram identity error appears on copies, switch to "Use Facebook Page".
- Publish only the drafts you created. "Review and publish (N)" may include the owner's own drafts: check the count before and after.
- Leave the campaign off. The owner switches it on.

## 8. Documents for stakeholders
Build one HTML page (artifact or file) with: current situation KPIs, structure diagram, creatives table (purchases, CPA, ROAS, why in / why out), budget-vs-CPA chart, day-by-day table, rules table, relaunch table, and a short "why not X" section for the alternative the stakeholder proposed. Offer a language switcher if the team is multilingual. Keep the plan and the account identical: after any change in one, update the other.

For pushback, answer with numbers from the account, not opinions, and keep it short: what we do, why, what number would change our mind.

## scripts/budget.py
```python
import sys
cpa = float(sys.argv[1]) if len(sys.argv) > 1 else 38
for k in (0.7, 0.85, 1.0, 1.15, 1.3):
    c = cpa * k
    learn = c * 50 / 7
    print(f"CPA {c:6.2f} | learn/day {learn:7.0f} | @190: {190/c:4.1f}/day | @380: {380/c:4.1f}/day")
```
