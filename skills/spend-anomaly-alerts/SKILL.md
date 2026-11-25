---
name: spend-anomaly-alerts
description: Designs a daily monitor for paid ad accounts that catches pacing problems, CPA, CPM and CTR spikes, spend with zero conversions and tracking drops (platform events against backend payments), with thresholds learned from the account's own history, a fixed alert message format and a human approval queue where a script proposes an action and a person approves it before it applies. Use when the user asks for "ad spend alerts", "anomaly detection for ad accounts", "monitor Meta and TikTok daily", "alert when CPA spikes", "budget overspend alert", "tracking broke alert", "approval queue for ad changes", or "automated rules vs script".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Spend anomaly alerts and approval queue

A daily check that tells a person what changed in the ad accounts, why it matters and what to do, and never changes money by itself without approval.

## When to use

- Someone checks accounts by hand and sometimes finds a problem days late.
- Spend jumped, conversions stopped or tracking broke and nobody saw it.
- You want automation but want a person to keep control of budgets.

## Inputs to collect first

1. Accounts and channels (Meta, TikTok, Google, Apple Search Ads) and how to read them: export, official API or reporting connector.
2. Daily history, at least 4 to 8 weeks: spend, impressions, clicks, conversions, CPM, CTR, CPA by campaign and ad set.
3. Planned spend per account or campaign (from the budget plan).
4. Backend payments by day and by source, to compare with platform events.
5. Target CAC and who owns each account.
6. Where alerts go (email, chat) and who approves actions.

## Method

### Step 1. Choose the checks

| Check | Question | Needs |
|---|---|---|
| Pacing | Is spend far above or below plan for the day or month to date? | Plan, spend |
| CPA spike | Is cost per primary event far above its normal level? | History |
| CPM spike | Did delivery get expensive without a creative change? | History |
| CTR drop | Did click rate fall sharply (fatigue, broken ad, disapproval)? | History |
| Zero conversions | Did spend pass a gate with no primary events? | Spend gate |
| Tracking drop | Did platform events fall while backend payments did not? | Backend data |
| Delivery stop | Did an active ad or set stop spending, or get rejected? | Status |

### Step 2. Learn thresholds from history

For each metric and level compute the median and spread over the last weeks, with the same weekday where seasonality is strong. Flag a day when:

- percent off median passes a line you set (for example 40 percent, example, tune it), or
- the z-score passes a line (for example 3, example, tune it), computed on a robust spread such as the median absolute deviation.

Require a minimum sample: no alert on a metric with fewer events or spend than the gate (state it). Review thresholds monthly against alerts that proved useless or missed.

### Step 3. Split by where the check runs

- Platform rules fit simple, fast and local limits: daily spend caps, pause at spend with zero results, notify when CPA passes a line. They are quick to set and need no code, but see only that platform's own data.
- A script on API exports or reports fits anything that crosses systems: tracking drop against backend payments, z-score or median-based baselines, blended CAC across channels, history-aware pacing. Use official APIs and read-only scopes first.

### Step 4. Write the alert message

Fixed format, short:

1. Severity (info, warning, critical) and account.
2. What: metric, value, normal range, sample size.
3. Likely cause (one or two ideas, labelled as hypotheses).
4. Proposed action with the exact entity and the exact change.
5. Approve and reject links, and what happens if nobody answers (default: nothing changes).

### Step 5. Approval queue

- The script writes a proposed action to a queue: entity, current value, new value, reason, expiry time.
- A person approves or rejects. Only approved items are applied, by a separate step with write access, and the result is logged.
- Allow only a small action set (pause an ad, lower a budget by a capped step). No raising budgets and no creating campaigns from alerts.
- Tracking drops and anything unclear go to a person with no automatic action: stop judging ads until measurement is fixed.

### Step 6. Operate it

Run once a day after platform reporting settles, and a lighter spend-only check intraday. Keep an alert log, mark each alert as useful, noise or missed, and tune thresholds from that log.

Alert hygiene:

- Group alerts into one daily digest, with critical items sent at once.
- Never send the same alert twice for the same cause. Re-alert only if it gets worse.
- Add a mute option with an expiry, so a planned change does not spam the channel.
- Show the last 7 days next to the value, so a reader sees the trend at a glance.
- Write the account owner on each alert so someone owns the answer.

## Output format

1. Check list with metric, level, threshold and the reason for each value.
2. Alert message template with an example.
3. Queue schema and the apply step.
4. Split: which checks are platform rules, which are script.
5. Tuning plan from the alert log.

Queue states to keep: proposed, approved, rejected, expired, applied, failed. Log who approved and when.

## Guardrails

- Never invent benchmarks. Thresholds come from the account's history or are labelled "example, tune it".
- Never let a script change spend without a recorded human approval. Read-only by default.
- Use official APIs and reporting within platform terms. Keep tokens in a secret store.
- State sample sizes. Small samples give "not enough data", not alerts.
- Platform data and backend data can differ by lag. Compare complete days only.

## Worked example (illustrative numbers)

Campaign median CPA over 6 weeks: 42, with a robust spread of 6 (example). Today it is 71, a z-score near 4.8, above the example line of 3, and 69 percent over the median. Spend today passed the gate. Alert: warning, "CPA 71 vs normal 42, 14 payments last 3 days". Hypotheses: fatigue on the top ad, or a tracking gap. Backend payments are flat, so tracking is fine. Proposed action: lower the daily budget of ad set A by 20 percent. A person approves, the script applies it and logs it.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-spend-anomaly-alerts). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
