---
name: tiktok-app-campaigns-playbook
description: Sets up and runs TikTok app and web campaigns for subscription apps: optimisation event choice, Smart+ versus manual setup, creative volume and refresh cadence, Spark Ads, Events API and MMP setup check, bidding (cost cap versus lowest cost), scaling steps and fatigue signals. Use when the user asks for "TikTok ads setup for app", "TikTok Smart+", "TikTok cost cap", "TikTok creative refresh", "Spark Ads", "TikTok Events API check", "TikTok campaign not scaling", or "TikTok ad fatigue".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# TikTok app and web campaigns playbook

A repeatable setup and weekly routine for TikTok where creative volume, event quality and bid control decide the result.

## When to use

- Launching TikTok for an app, or for a web2app funnel that ends in a store install or a web payment.
- Spend is flat or CPA climbs after a good first week.
- The team debates Smart+ against manual setup.
- Creatives die fast and nobody has a refresh plan.
- You need a check that events reach TikTok correctly.

Do not use for pure brand reach goals. This skill assumes a payment or trial signal.

## Inputs to collect first

1. Target CAC per payer and payback window (see unit-economics-check).
2. Funnel type: app install, web2app with a web payment, or web lead.
3. Event path: MMP postbacks, Events API from your server, pixel, or app SDK. Which events and how often.
4. Weekly event counts for the last 4 weeks: clicks, installs or landing views, trials, payments.
5. Creative inventory: formats, hooks used, run dates, spend per creative.
6. Current campaign export with budgets, bid types and changes.

## Method

### Step 1. Choose the optimisation event

- Choose the event closest to payment that still produces enough weekly events per ad group to leave learning. Verify the current learning threshold in TikTok documentation.
- If payments are too few, optimise for trial start or registration and judge the payment result separately, then move down the funnel when volume allows.
- Do not optimise for installs only and call the result a business outcome.

### Step 2. Smart+ or manual

- Smart+ automates targeting, placement and creative combination. It suits accounts with clean events and a steady supply of creatives. Manual control suits tests where you want to isolate one variable.
- Run a small controlled comparison: same budget split, same creative pool, same window. Decide on cost per payer, with the sample size shown.
- Whichever mode you choose, keep one test per campaign so you can read the result.

### Step 3. Events API and MMP setup check

1. Confirm each event fires once per real action (no duplicates, no test events in production).
2. Confirm deduplication between pixel or SDK and server events using a shared event identifier. Verify current field names in TikTok docs.
3. Pass value and currency with payment events, and remove refunded or cancelled purchases from the feed where the platform allows.
4. Compare TikTok reported events with MMP and backend counts weekly. Define an acceptable gap with the client, then act when it is exceeded.
5. Check event match quality or the equivalent diagnostics in the platform and fix the lowest field first.

### Step 4. Creative volume and cadence

- Treat creative as the main lever. Plan a number of new concepts per week that the team can really produce.
- Each concept varies the hook, not only the cut: first three seconds, opening line, on-screen text.
- Keep a hook bank: hook, angle, format, spend, result. Reuse winning angles in a new execution before inventing new ones.
- Refresh on signals, not on a calendar alone (Step 7), and keep the next batch queued before the current winner fades.

### Step 5. Spark Ads

- Use Spark Ads to run organic or creator posts as ads, which keeps comments and social proof on the post.
- Get written authorisation from creators for ad use, with a time window, and store it. Verify current authorisation steps in the platform.
- Moderate comments. A negative comment thread on a winner can cut results.

### Step 6. Bidding and scaling

- Lowest cost: simplest, good for finding what works, less predictable in cost.
- Cost cap: holds cost near a target but can underspend if the cap is too tight. Set it from your target cost per optimisation event (target CAC times the event to payer rate), not from a guess.
- Scale in steps (example: 20 percent), wait a full learning window, then step again. For bigger jumps duplicate the winner. Stop when marginal CAC passes target (see ua-kill-scale-rules).

### Step 7. Fatigue signals

Watch together, over several days: hook rate or three second view rate falling, CTR falling, frequency rising, CPM flat or up, cost per event rising. One signal alone is noise. When three agree, replace the creative and keep the ad group.

## Output format

1. Setup sheet: campaign type, event, mode, bid type, budget, test plan.
2. Event check table: event, source, dedup status, gap against backend.
3. Creative calendar: concepts per week, owner, hook tested.
4. Weekly action list with sample sizes, and scaling steps with dates.

## Guardrails

- No invented benchmarks. Use user data or label "example, tune it".
- Field names, learning thresholds and bid options change. Tell the user to verify against current TikTok documentation.
- Judge on payers when payer data exists, and say which source was used.
- No fake events, no misleading claims, no unauthorised use of creator or music content. Health, finance and before and after claims need the check in ad-copy-production.

## Worked example (illustrative numbers)

Target CAC 45 (units). Trial to paid 20 percent (example), so target cost per trial is 9. Set a cost cap near 9, start at a budget that buys about 15 to 20 trials a day, and run Smart+ against manual with equal budgets for 7 days. Result: manual 40 trials, 7 payers, spend 380, so 54 per payer. Smart+ 52 trials, 9 payers, spend 380, so 42 per payer. The gap is on small samples, so keep both, extend one more week, and add four new hooks before judging.

## Related skills

ua-budget-planner, meta-creative-testing for the testing logic, market-to-creative-brief for briefs, competitor-watch-weekly for ideas.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-tiktok-app-campaigns-playbook). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
