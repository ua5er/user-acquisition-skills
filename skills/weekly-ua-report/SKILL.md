---
name: weekly-ua-report
description: Builds a weekly paid acquisition report for an app or subscription business from exported data, with decisions, not just charts. Use when the user asks for a "weekly UA report", "weekly performance report", "marketing report for the founder", "what happened this week in paid", "Monday growth review", "report on CAC, ROAS and payback", or "automate the weekly report".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# Weekly UA report

A one-page report a founder reads in five minutes and acts on. Built from exports the user supplies.

## When to use

- Every week, at the same time, from the same sources.
- When a report exists but nobody makes decisions from it.
- When reporting takes hours by hand and should become a script.

## Inputs

1. Spend and platform metrics by channel, campaign and creative for the week and the previous periods.
2. Backend payments for the same cut (new payers, revenue, refunds).
3. Targets: CAC ceiling, payback target, monthly budget.
4. Last week's report and the decisions made then.
5. Notes on changes: launches, offers, tracking changes, holidays.

## Method

### Step 1. Check the data before the story

Run three checks and show them at the top: spend matches billing within the stated tolerance, backend payments loaded to the last day, and no tracking change broke comparability (see attribution-sanity-check). If a check fails, mark affected numbers as unreliable.

### Step 2. Headline block

Spend, new payers, CAC (backend), revenue, payback status against target, budget used versus plan. Each with the change versus last week and versus the trailing four-week average. Write the direction in words first, then the number.

### Step 3. What moved and why

For the largest changes, break down by driver: volume (spend), price of traffic (CPM, CPC), traffic quality (click to trial, trial to paid), creative mix. One sentence per driver, with evidence. Mark anything you cannot explain as unexplained.

### Step 4. Winners and losers

Top and bottom creatives and ad sets by the primary metric, only those past the spend gate. For the rest write "not enough data".

### Step 5. Decisions

A short list: what we scale, what we stop, what we test, what we fix (tracking, funnel). Each with owner and date. Check the previous week's decisions and report what happened.

### Step 6. Risks and next week

Budget pacing, fatigue watch list, platform changes, open data gaps.

## Output format

Markdown, one page: data checks, headline table, three to five bullets on what moved, winners and losers table, decisions table, risks. Add an appendix with the raw tables.

## Guardrails

- Never fill gaps with estimates presented as facts. Label estimates.
- Every number has a source (platform, MMP, backend). Do not mix without saying so.
- No celebratory language. State what happened and what to do.
- Do not name individuals or clients in reports meant for sharing outside the team.

## Worked example (illustrative)

Headline: spend up, backend CAC up, payers flat. What moved: CPM up in one placement, click to trial down on the newest landing page. Decision: pause the placement, roll back the landing page, test a revised hook next. Last week's decision to raise budget on the best ad set is reviewed: marginal CAC rose above the ceiling, so scaling stops.
