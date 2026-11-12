---
name: attribution-sanity-check
description: Audits whether paid acquisition numbers can be trusted, comparing ad platform, MMP, SKAN and backend payment data for mobile apps and web funnels. Use when the user says "attribution looks wrong", "Meta says X but Stripe says Y", "SKAN check", "AppsFlyer vs Adjust discrepancy", "Conversions API setup", "tracking audit", "why do installs not match", or "can I trust ROAS". Produces a reconciliation table and a fix list.
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# Attribution sanity check

Finds out which number to believe before money is moved on it.

## When to use

- Platform ROAS and backend revenue disagree.
- After an iOS, SDK, funnel or checkout change.
- Before building dashboards or automation on top of attribution data.
- When moving from app-install buying to a web funnel with server-side events.

## Inputs

1. Four views of the same period if they exist: ad platform report, MMP report (AppsFlyer, Adjust, AppMetrica or similar), SKAN postbacks or the MMP's SKAN view, and backend payments (Stripe, RevenueCat, Adapty, store reports).
2. The event map: which events fire where, with names, and which one the platform optimises for.
3. Funnel type: app install, web to app, or web only.
4. Recent changes: SDK versions, pixel or Conversions API changes, checkout changes, consent flow changes.

## Method

### Step 1. Anchor on the backend

Backend payments are the source of truth for money. Everything else is a model of it. Write the backend totals first: payers, revenue, refunds.

### Step 2. Reconcile, layer by layer

Build one table with a row per layer and columns: count, revenue, difference to backend, difference explained, difference unexplained.

1. Platform vs backend (payments).
2. MMP vs backend.
3. SKAN vs MMP for iOS install campaigns (expect gaps, conversion value and privacy thresholds hide some data).
4. Pixel vs Conversions API vs backend for web funnels (look for double counting and missing deduplication keys).

### Step 3. Check the usual suspects

- Event deduplication: same event sent by browser and server without a shared event id.
- Event timing: purchase fired at checkout start, not at success.
- Currency, tax and refund handling differing between sources.
- Trial vs paid: platform counts trial start as a purchase.
- Attribution window mismatch between sources.
- Consent and ATT: share of users with no identifier, and what the platform models for them.
- Test traffic and internal users in production data.
- Time zone cut-offs.

### Step 4. Decide the decision metric

Choose which source drives which decision and write it down: for example budget moves use backend payments joined by campaign, creative testing may use platform signals earlier in the funnel. Record the known bias of each source (direction if known, otherwise "unknown").

### Step 5. Fix list

Rank fixes by money at risk. Each item: what is wrong, evidence, fix, owner, how to verify after.

## Output format

1. Reconciliation table with unexplained gaps highlighted.
2. Findings ranked by impact, each with evidence.
3. The decision-metric map.
4. Fix list with verification steps.
5. What cannot be known from the supplied data.

## Guardrails

- Never claim a gap "is normal" with a percentage from memory. Quote the user's own history, or say that no baseline exists and propose how to build one.
- Do not recommend workarounds that evade platform privacy rules, consent choices or ATT.
- Separate verified facts (in the data) from hypotheses (inferred).
- If only one source is supplied, say what cannot be checked.

## Worked example (illustrative)

A platform report shows 120 purchases, backend shows 70 payers. Check 1: platform counts trial starts as purchases, backend payers exclude trials in progress. After aligning definitions the platform shows 85 against 70. Check 2: browser and server events share no event id, so some purchases count twice. After adding deduplication the platform count falls to 74. Remaining gap of 4 is within what modelled conversions could explain, flagged as "unverified". Decision metric: backend payers by campaign.
