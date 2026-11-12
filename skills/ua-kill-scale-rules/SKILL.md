---
name: ua-kill-scale-rules
description: Writes kill, scale and budget pacing rules for paid user acquisition on Meta and TikTok for subscription and app businesses, then applies them to a campaign export. Use when the user asks for "kill rules", "scale rules", "when to turn off an ad set", "budget pacing", "how fast to raise budget", "Meta ads automation rules", "TikTok campaign rules", or "which creatives to pause". Works from the user's own CAC target and data.
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# UA kill and scale rules (Meta, TikTok)

Turns a vague "pause what does not work" into written rules that a person or a script can apply the same way every week.

## When to use

- A buyer judges ads by feel, or by a different metric each day.
- Spend is growing and nobody can say when a budget increase is safe.
- A weekly review takes hours because there are no agreed thresholds.
- You want rules ready to paste into platform automation or a script.

Do not use for brand awareness campaigns with no payment signal. Rules below assume you can tie spend to a payment or a trial event.

## Inputs to collect first

1. Business model: subscription, trial plus paid, one-off purchase, web funnel or app install.
2. Target CAC and the payback window the business can finance (from the unit-economics-check skill if available).
3. The event the platform optimises for, and the event that actually pays (these are often different).
4. A campaign or ad set export: spend, impressions, clicks, installs or leads, trials, payments, revenue, by day and by creative.
5. Current daily budget per campaign and the account's spend limit.

If the target CAC is unknown, stop and compute it first. Never pick a CAC target "from the industry".

## Method

### Step 1. Fix the judging metric

Pick one primary metric, the closest one to money you can read with enough volume: cost per payment, else cost per trial start, else cost per qualified install. Keep a secondary metric for diagnosis only (hook rate, CTR, CPM, install to trial rate). Rules use the primary metric. Diagnosis metrics explain why, they do not decide.

### Step 2. Set the spend gate before judging

An ad cannot be killed on too little data. Define the gate as a multiple of target CAC:

- Do not judge before spend reaches a stated multiple of target CAC (start with 2x to 3x, an example you tune to your volume) and a minimum number of clicks you set from your own click to event rate.
- Below the gate: leave it alone, unless a hard stop applies (Step 3).

### Step 3. Write the kill rules

Write each rule as: condition, window, action. Use this set as a starting template and fill values from your data:

| Rule | Condition | Action |
|---|---|---|
| Hard stop | Spend passed the hard cap (for example 4x target CAC, illustrative) with zero primary events | Pause ad |
| Soft kill | Spend passed the gate and cost per primary event is above the kill line for the full window | Pause ad, log the reason |
| Fatigue | Frequency rising and CTR or hook rate falling for several days while CPM is flat | Replace creative, keep the ad set |
| Quality | Click to event rate far below the account median, with normal CTR | Check landing page or store page and tracking before blaming the ad |
| Tracking | Platform events fall while backend payments do not | Stop all judging, fix measurement first (see attribution-sanity-check) |

State the kill line explicitly, for example "1.3x target CAC over the last 3 days" as an example. Tune it from your history: look at the ads you kept that later paid back, and the ads you killed that you now wish you had kept.

### Step 4. Write the scale rules

- Scale only an ad set that beat target CAC over a window long enough to cover the learning period and a weekday cycle.
- Raise budget in steps (a typical cautious step is 20 percent, an example), wait a full window, and re-check. Large jumps reset delivery on Meta and often raise CAC.
- Prefer duplicating a winner into a new ad set for a bigger jump instead of editing the original.
- Scale the creative, not only the budget: when a winner fatigues, the next creative must already be in the queue.
- Stop scaling when marginal CAC (extra spend divided by extra payments) crosses target, even if blended CAC still looks fine.

### Step 5. Budget pacing

- Compute planned daily spend from monthly budget and days left, every morning.
- Flag under-delivery (below 80 percent of plan for two days) and over-delivery.
- Reserve a share of budget for tests (state it, for example 10 to 20 percent as an example) so scaling does not starve learning.
- Never let a single campaign exceed a share of total spend that the business could not survive losing. Set that share with the client.

### Step 6. Apply to the export

Run every ad and ad set through the rules in order. Output a table with: entity, spend, primary metric, rule fired, action, confidence (high if above the gate by a wide margin, low if close to the line).

## Output format

1. Rule sheet: metrics, gate, kill rules, scale rules, pacing rules, each with its value and the reason for that value.
2. Action table for the supplied export.
3. Open questions (data gaps that make some rows low confidence).
4. Automation notes: which rules can be platform rules and which need a script.

## Guardrails

- Never invent benchmarks. Every threshold is either computed from the user's data, derived from their target CAC, or labelled "example, tune it".
- Never recommend actions on platform-reported conversions alone when the user can see payments. Say which source was used.
- Do not suggest bypassing platform policies, spoofing events or buying engagement.
- State the sample size behind every verdict. If spend is under the gate, the verdict is "not enough data".
- Rules support judgment, they do not replace it. Flag edge cases for a human.

## Worked example (illustrative numbers)

Target CAC: 40 (currency units). Gate: 2x = 80 spend. One ad has spend 95, 0 payments, 3 trials. Hard stop is 4x = 160, not reached. Soft kill needs cost per payment above the kill line, but there are no payments, so cost per trial is the fallback: 95 / 3 = 31.7. If the trial to paid rate for this offer is known to be about one in three (example), expected cost per payment is about 95, above the kill line of 52 (1.3x). Verdict: soft kill, medium confidence, because three trials is a small sample. Action: pause, keep the creative idea for one retest with a changed hook.
