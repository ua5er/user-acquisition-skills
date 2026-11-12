---
name: ai-marketing-system-audit
description: Audits a company's marketing system as a loop (acquire, convert, measure, automate, intelligence, decide), finds the weakest links and proposes where AI agents and automation can help without risk. Use when the user asks for an "AI marketing audit", "marketing system audit", "where can we automate marketing", "growth audit", "AI growth consultant checklist", "map our marketing stack", or "what should we build first in marketing automation".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# AI marketing system audit

Maps how a business finds, converts and learns from customers, then ranks gaps by money at stake. The idea: the numbers that spend the money should also decide the next dollar, so each link of the loop must feed the next.

## The loop

1. Acquire: channels, budgets, creative production, partners.
2. Convert: landing pages, web funnels, onboarding, paywall, checkout.
3. Measure: tracking, attribution, BI, unit economics, data quality.
4. Automate: pacing rules, alerts, reporting, testing frameworks, kill and scale logic.
5. Intelligence: competitor monitoring on public data, market and pricing watch.
6. Decide: weekly cadence, owners, decision log, budget allocation.

## When to use

- A new engagement starts and you need a fast, fair picture.
- A team wants to "use AI" in marketing and does not know where it is safe.
- Spend is growing and reporting or tracking is behind.

## Inputs

1. Business model, price points, current monthly spend, team size.
2. Access or exports for: ad accounts, analytics, MMP, payment data, funnel tools, BI.
3. Org chart for marketing decisions and the current meeting rhythm.
4. Past tests and their results, if recorded.

## Method

### Step 1. Inventory

List tools, data sources and people per link of the loop. For each: what it does, who owns it, how often it is used, how it connects to the next link (manual, export, API).

### Step 2. Score each link on four checks

For each link answer yes, partly or no, with evidence:

- Exists and is owned.
- Trusted: numbers reconcile with money.
- Connected: output feeds the next link without manual copying.
- Acted on: decisions follow from it on a schedule.

### Step 3. Find gaps and chains

A gap in measure poisons the links after it. Order findings by dependency, not only by size: fix tracking before automation, automation before agents.

### Step 4. Where AI helps, and where not

Good candidates: reading dashboards and drafting summaries, anomaly flags, generating creative briefs from tested angles, classifying ad library data, writing queries and scripts, QA of tracking. Weak candidates: anything where a wrong action spends money without a human check, or where input data is not trusted yet. For each proposed use state: input, output, human check, failure cost.

### Step 5. Roadmap

Three horizons: first two weeks (measurement and quick wins), first 90 days (automation and funnel), after that (intelligence and agents). Each item has owner, effort, dependency, and the metric that proves it worked.

### Step 6. Operating cadence

Define the weekly loop: data check, report, decisions, test queue, review of last decisions.

## Output format

1. Loop map with tools and owners.
2. Score table (link by check) with evidence.
3. Gap list ordered by dependency and money at stake.
4. AI and automation candidates with human checks.
5. Roadmap and weekly cadence.
6. What the audit could not verify.

## Guardrails

- Evidence first: every score cites something seen or supplied.
- No claimed results or lifts. Roadmap items name metrics, not promised outcomes.
- Automation that changes budgets needs limits and a human approval path.
- Public data only for competitor intelligence.
- Respect client confidentiality: no client names in outputs meant to be shared.

## Worked example (illustrative)

A subscription app buys on two channels. Acquire exists. Convert has a paywall nobody has tested. Measure shows platform payments higher than backend by an unexplained gap. Automate is a spreadsheet updated by hand. Intelligence is none. Decide is ad hoc. Order of work: reconcile attribution first, then the weekly report script, then a test queue for the paywall, then kill and scale rules, then competitor monitoring.
