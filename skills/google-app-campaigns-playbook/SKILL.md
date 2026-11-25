---
name: google-app-campaigns-playbook
description: Plans and audits Google App campaigns (UAC) for subscription apps: choosing between install, in-app action and tROAS bidding, the event and volume each needs, asset groups and asset ratings, budget steps, learning period, Firebase or MMP conversion import, and iOS versus Android differences. Use when the user asks for "Google App campaign setup", "UAC", "Google UAC tROAS", "which event to optimise in Google App campaigns", "asset ratings low", "Google app install campaign not scaling", or "Firebase conversions for Google Ads".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Google App campaigns playbook (installs, in-app actions, tROAS)

Helps choose the right bid goal for the volume the app really has, then feeds the campaign clean events and enough creative.

## When to use

- A new Google App campaign is being planned and the optimisation event is undecided.
- Installs are cheap but few users start a trial or pay.
- An in-app action or tROAS campaign sits in learning and never leaves it.
- Asset ratings are low or one asset gets all the delivery.
- Android and iOS results differ and nobody knows why.

Do not use when the app sends no trusted conversion events. Fix measurement first (see payment-capi-tracking).

## Inputs to collect first

1. Target CAC per payer and payback window (see unit-economics-check).
2. Weekly counts per event for the last 4 to 8 weeks: installs, registration, trial start, payment, by platform.
3. How events reach Google: Firebase or Google Analytics link, MMP postbacks, or the Google Ads SDK. Which events are imported.
4. Revenue value passed with the payment event, currency, and whether refunds are removed.
5. Current campaign export: spend, installs, event counts, tROAS or CPA targets, budget changes with dates.
6. Asset inventory: text lines, images, videos by orientation, and their ratings if shown.

## Method

### Step 1. Pick the bid goal from volume

Move up only when volume supports it. For each candidate event, count weekly events per campaign:

- Installs: use to launch and to collect the first signals. Cheapest to feed, weakest link to money.
- In-app action (a deep event such as trial start): use when the event reaches the volume Google asks for in current documentation. Verify the minimum in the Google Ads help pages, since it changes.
- tROAS: use when a value-carrying payment event is steady and your revenue data is reliable. Needs the most volume and the longest wait.

Rule: choose the event closest to a payment that still gets enough events per week to leave learning. If no event reaches the volume, step down one level and plan to step up later.

### Step 2. Event hygiene

- Import only events that mean something: one trial or payment event, not five overlapping ones.
- Pass revenue with the payment event, in one currency or with a currency field. Check that test and refunded purchases are excluded.
- Compare Google reported events with backend counts weekly. A persistent gap means decisions are made on bad data.
- Match the conversion window and counting setting to how users actually convert. Verify current setting names in the platform.

### Step 3. Assets and ratings

The campaign assembles ads from your assets. Supply a range, not a set of near copies:

- Several text lines with different angles (benefit, proof, fear of missing out, price).
- Images and videos in every orientation offered. Include user-style video, not only product screens.
- Read the asset ratings as relative signals inside the campaign. Replace the lowest rated after the asset has had enough impressions, and keep a log of what replaced what.
- Do not judge an asset at low spend. Use a spend gate from your target CAC (example 2x, tune it).

### Step 4. Budget steps and learning

- Start with a daily budget that can buy a meaningful number of target events per week, using target CAC times the event count you need.
- Change budget in steps (example: 20 percent), then wait a full learning window before the next step. Do not edit targets and assets on the same day.
- During learning expect unstable cost. Judge after the window, using payers, not installs.
- Raise a target CPA or lower a tROAS target only in small steps, and log each change.

### Step 5. iOS versus Android

- Android: events usually arrive with more detail and faster, so deeper bid goals become possible sooner.
- iOS: attribution depends on Apple privacy rules and on conversion value setup, so signals are thinner and delayed. Verify current iOS measurement behaviour in Google and Apple documentation.
- Run platforms in separate campaigns so budgets and targets do not mix. Compare payers per spend, not installs per spend.

### Step 6. Weekly check

1. Reconcile Google, MMP and backend counts.
2. Review search, display, YouTube and other placements for waste if the report allows it.
3. Rotate the lowest assets and add one new angle.
4. Decide: hold, step budget, change goal, or pause. Write the reason.

## Output format

1. Goal decision: chosen bid type, event, why, and what volume would trigger a step up.
2. Event map: events imported, source, value, known gaps.
3. Asset plan: what to add, what to replace, test angle.
4. Budget schedule with dates and review points.
5. Open questions.

## Guardrails

- No invented benchmarks. Volumes, rates and thresholds come from the user's data, the current Google documentation, or are labelled "example, tune it".
- Field names, minimum volumes and bid options change. Tell the user to verify them against current platform docs.
- Do not recommend policy workarounds, fake events or inflated revenue values.
- State sample size behind every verdict. Under the gate, the verdict is "not enough data".

## Worked example (illustrative numbers)

Target CAC 50 (units). Android: 900 installs, 130 trial starts, 22 payments per week (examples). Payments are too few for tROAS, trial starts may be enough for an in-app action goal if current Google guidance allows that volume. Decision: optimise for trial start, import payment as a secondary event, and plan to move to tROAS when payments are steady at the volume Google documents. Budget: expected cost per trial about 50 / 0.17 = 8.5 if trial to paid is 17 percent (example), so a daily budget of 170 buys about 20 trials a day. Raise in 20 percent steps after each full learning window.

## Related skills

ua-budget-planner for channel mix, payment-capi-tracking for event delivery, meta-creative-testing for creative testing logic that transfers.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-google-app-campaigns-playbook). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
