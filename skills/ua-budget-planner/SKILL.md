---
name: ua-budget-planner
description: Builds a monthly or quarterly paid user acquisition budget and channel mix for app and subscription businesses across Meta, TikTok, Apple Search Ads, Google App campaigns and web2app, from target CAC, payback window, cash limits and current channel data. Includes a test reserve, a forecast of payers and payback, and a scenario table. Use when the user asks for "UA budget plan", "channel mix", "how much should we spend on Meta vs TikTok", "quarterly marketing budget", "budget allocation", "how much can we spend per month", "payback forecast", or "scenario plan for ad spend".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# UA budget planner (monthly and quarterly channel mix)

Turns "we have some money for ads" into a plan with a total, a split by channel, a test reserve, a forecast and three scenarios. Every number traces back to the user's own data.

## When to use

- A new month or quarter starts and spend is set by habit or by last month's split.
- The business wants to add a channel (for example Apple Search Ads or web2app) and needs to know how much to risk.
- Cash is limited and someone must say how much spend the payback window allows.
- A manager or investor asks for a forecast of payers and payback.

Do not use without any payment data. If there is no cohort revenue yet, plan a test budget only and say so.

## Inputs to collect first

1. Target CAC and the payback window the business can finance (from the unit-economics-check skill if available).
2. Cash limits: maximum cash tied up in unpaid acquisition at any time, and any monthly spend cap.
3. Per channel, last 8 to 12 weeks: spend, installs or leads, trials, payments, revenue, by week. Include web2app and app store paths separately.
4. Conversion lag: how many days from click to trial, and from trial to first payment.
5. Capacity limits: creative output per week, how much each channel can absorb before CAC rises (from past scale attempts).
6. Seasonality or known events in the period.

If the CAC ceiling or payback window is unknown, stop and compute it first. Never take it from "the industry".

## Method

### Step 1. Set the total envelope

Compute the largest spend that cash allows: cash limit divided by the cash that one unit of spend ties up over the payback window. Write the formula with the user's numbers. The plan total is the lower of this envelope and any cap set by the business.

### Step 2. Reserve the test budget

Hold back a share for tests (example: 10 to 20 percent, tune it) before splitting the rest. Tests cover new creatives, a new channel, a new audience or a new funnel. Reserve is spent only on pre-written tests, each with a question and a stop rule.

### Step 3. Rate each channel on evidence

For every channel build one row: spend, payers, CAC on payments, payback so far, marginal CAC on the last increase, confidence. Confidence is high only with enough payments to judge (state the count). A channel with few payments is "unproven" and gets test budget only, not core budget.

### Step 4. Split the core budget

- Fund channels in order of payback speed, from proven and under the CAC ceiling, until each reaches its absorption limit from Step 3 data.
- Cap any one channel at a share the business could survive losing (set it with the client).
- Do not push a channel past the point where marginal CAC crosses target.
- Web2app and app store paths are separate lines: their CAC, fees and payback differ.

### Step 5. Forecast payers and payback

For each channel: planned spend divided by expected CAC gives payers. Show a low, base and high case by moving CAC and conversion lag within the range seen in the data, not by guessing. Place payments on a timeline using the real lag, so the plan shows cash out first and cash in later. State the week when cumulative cash turns positive.

### Step 6. Scenario table

Build at least three scenarios: base, conservative (CAC 20 percent worse, example, tune it) and aggressive (extra spend in the best channel until marginal CAC hits target). For each: total spend, payers, blended CAC, peak cash at risk, payback week.

### Step 7. Review rules

Write when the plan is revisited: weekly pacing check, a monthly re-split, and the trigger for an emergency cut (for example blended CAC above the ceiling for a full payback cycle, example). Link to ua-kill-scale-rules for ad level rules.

### Step 8. Check the plan against reality each week

- Write down which assumption hurts most if wrong (usually conversion lag or marginal CAC) and how you will notice early.
- Keep a one-page owner view: total, split, expected payers, worst-case cash at risk.
- Compare actual spend, payers and CAC with the plan every week and write the gap in one line.
- If a channel is behind plan for two weeks, find the cause (creative supply, tracking, audience size) before moving budget.
- If a channel is ahead of plan, raise its budget in steps and recheck marginal CAC, not blended CAC.
- Move unused test reserve into the next test, not into core spend, unless a test already proved a result.
- Record every change to the plan with the date and the reason, so the next quarter starts from facts.

## Output format

1. Envelope: formula, inputs, result.
2. Channel table: channel, evidence, core budget, test budget, expected CAC, expected payers.
3. Forecast: weekly spend, payers and cumulative cash, low, base and high.
4. Scenario table.
5. Test list with the question and stop rule for each test.
6. Review calendar and cut triggers.
7. Open questions (data gaps that widen the range).

Tips for the channel table:

- Put web2app next to app install channels so fees and payback differences are visible.
- Show Apple Search Ads and Google App campaigns with their own intent level: search demand is capped, so mark the ceiling.
- Show Meta and TikTok with creative supply as the limit: more budget needs more creatives.
- Mark any channel where payments come late with the lag in days.

## Guardrails

- Never invent benchmarks. Every threshold comes from the user's data or is labelled "example, tune it".
- Forecasts are ranges. Do not present one number as certain.
- Use payments from the backend where available, not only platform-reported conversions. Say which source was used.
- Do not allocate core budget to a channel with too few payments to judge. Put it in the test reserve.
- Do not suggest bypassing platform policies or inflating events.

## Worked example (illustrative numbers)

Example: cash limit 30,000 tied up at once, payback window 30 days, target CAC 40. Spend of 30,000 per month would tie up roughly the whole amount until payback, so the envelope is about 30,000 (example). Reserve 15 percent, example: 4,500 for tests, 25,500 core. Meta shows 120 payers at CAC 38 over 8 weeks and a stable marginal CAC, so it takes 60 percent of core. Apple Search Ads shows CAC 35 but only 25 payers, so it is capped near 20 percent until more payments arrive. TikTok has 9 payers: unproven, so test reserve only. Base forecast: 25,500 / 38 gives about 670 payers (illustrative).

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-ua-budget-planner). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
