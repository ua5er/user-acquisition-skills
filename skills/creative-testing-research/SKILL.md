---
name: creative-testing-research
description: Plans a creative testing cycle for paid social and researches competitor ads using only public ad libraries (Meta Ad Library, TikTok Creative Center, Google Ads Transparency Center). Use when the user asks for "creative testing plan", "competitor ad research", "what ads are competitors running", "creative briefs for Meta or TikTok", "hook testing", "ad library analysis", or "creative angles for a subscription app".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# Creative testing and competitor ad research

Two jobs in one loop: learn what the market already says (public data), then test your own angles in a way that produces a decision.

## When to use

- Creative output is steady but winners are rare.
- A new market, offer or competitor appeared.
- You need briefs for a creative team that tie to hypotheses.

## Inputs

1. Product, offer, price points, audience, markets.
2. Competitor list (names, app store links, domains) supplied by the user.
3. Your own creative results: spend, primary metric per creative, hook and hold metrics.
4. Production capacity per week.

## Method

### Step 1. Public ad research

Use only public sources a person can open without logging in to someone's account: Meta Ad Library, TikTok Creative Center and the ad library, Google Ads Transparency Center, public app store pages. Do not scrape behind logins, do not use leaked data, and respect each platform's terms.

For each competitor record: how many ads are active, formats, how long an ad has run (long runtime is a weak signal of profitability, not proof), hooks used in the first seconds, offers, landing page type, claims.

### Step 2. Cluster into angles

Group ads into angles (problem, outcome, social proof, demo, curiosity, comparison, trend format). Count presence per angle, then mark gaps: angles nobody uses, and angles everybody uses. A crowded angle needs a better execution, an empty angle needs a test.

### Step 3. Write hypotheses

One line each: "Angle X with hook Y will beat the control on cost per trial because Z". Keep the list short and ranked by expected value and ease.

### Step 4. Design the test

- One variable per test: hook, angle, format, offer line or end card.
- Same audience and placement, equal budget per creative, a fixed run window.
- Judge on the primary metric with the spend gate from ua-kill-scale-rules. Use hook rate and hold rate to explain, not to decide.
- Keep a control that stays live across tests.

### Step 5. Briefs

For each creative: angle, hook (first 3 seconds, script line), body beats, call to action, on-screen text, format spec per platform, what must not appear (claims you cannot back).

### Step 6. Cycle review

Record each test: hypothesis, result, spend, decision (scale, iterate, drop), and what was learned. Keep the log in one file so the team does not retest old ideas.

## Output format

1. Competitor table (public data only, with source links and capture date).
2. Angle map with gaps.
3. Ranked hypotheses.
4. Test plan for the next cycle.
5. Creative briefs.
6. Learning log template.

## Guardrails

- Public data only. State the source and date for each observation.
- Never claim a competitor's spend, revenue or results from an ad library. It shows what runs, not how it performs.
- Do not copy competitor creative. Use patterns, produce original work.
- Avoid misleading claims, fake testimonials and before and after images that overpromise.
- No invented benchmarks for hook rate or CTR.

## Worked example

A competitor list of four apps. Ad library shows most use a transformation hook. One uses a "ask 3 friends to rate" social hook. Gap: the social-reaction angle is rare. Hypothesis: a reaction-focused hook lowers cost per trial against the transformation control. Test: three hooks, same body, equal budget for the run window, verdict on cost per trial once the gate is passed.
