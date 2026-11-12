---
name: onboarding-web2app-funnel
description: Designs or reviews an app onboarding flow or a web-to-app funnel for subscription products, from ad click to paid trial, with concept options, screen-by-screen jobs, measurement plan and test order. Use when the user asks to "redesign onboarding", "web2app funnel", "quiz funnel", "web funnel for an app", "onboarding concepts", "reduce drop-off before paywall", "FunnelFox or Stripe checkout flow", or "what should the onboarding show before the paywall".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# Onboarding and web-to-app funnel design

Produces a small set of distinct onboarding concepts, each with a clear hypothesis, so a team tests ideas and not just visual variants.

## When to use

- Drop-off between install (or ad click) and paywall is high.
- The onboarding is a tour of features and does not sell the outcome.
- A move from app-first to a web funnel with payment before install is being considered.
- A designer or an AI design tool needs a brief with real constraints.

## Inputs

1. Product in one sentence and the aha moment: the first moment a user feels the product works.
2. Traffic sources and the promise of the ads that feed the funnel.
3. Current flow: screens, steps, where users leave (user's own funnel data).
4. Constraints: store rules, tracking events needed, payment stack, markets, languages, permissions needed.
5. What already ran as tests, and the result.

## Method

### Step 1. Map the current flow

List every screen with its job, the data collected, and the event fired. Mark screens with no job. Mark where the first value is shown and where the first payment ask appears.

### Step 2. Choose the strategic question

Pick one: should value come before the ask (demo-first), should the user invest effort first (quiz and personalisation), should the flow mirror the ad (story-first), should the user build something that the paywall then unlocks (profile or result-first). One question per concept set.

### Step 3. Generate concepts

Create 3 to 5 concepts, each distinct on mechanism, not on colour. For every concept write:

- Name and one-sentence hypothesis ("people who answer two questions value the plan more").
- Screen list with the job of each screen.
- The moment of peak and the handoff to the paywall.
- What the user does (taps, picks, uploads) and what the product shows back.
- Events to track.
- Risks (store review, honesty, load time).

### Step 4. Honesty and fit rules

- Show only what the product really delivers after payment. A demo that overpromises raises refunds.
- Personalisation screens must change something later, otherwise remove them.
- Progress indicators must not start at an artificially high level to trick users.
- Social proof must be real.

### Step 5. Measurement plan

Define the events and the primary metric (trial start or payment per ad click, not just completion rate), the guardrails (refunds, D1 and D7 retention, time to complete), and how concepts will be compared (split on the same traffic).

### Step 6. Test order

Test the strategic question first, with the roughest concepts that still show the mechanism. Polish only the concept that wins. Write what result would make you stop.

### Step 7. Web2app specifics (if relevant)

- Ad promise to first screen match.
- Server-side events and deduplication from the first step (see attribution-sanity-check).
- Checkout page: price, term, total, cancel, and support contact in view.
- Deep link and account handoff after payment, tested on a clean device.
- Email or login capture timing.

## Output format

1. Current flow map with problems.
2. The strategic question and why.
3. Concept cards (3 to 5).
4. Measurement plan.
5. Test order and stop rules.
6. A design brief per concept for a designer or an AI design tool.

## Guardrails

- Never state expected lifts. No data, no numbers.
- Do not copy a competitor's flow screen by screen. Use public examples only to understand patterns.
- Keep user data requests minimal and justified.

## Worked example

Brief for a subscription photo app (generic). Question: should the user see value before paying? Concepts: A, a two-question quiz that builds a personal plan; B, an interactive demo where each screen shows the product; C, ad-like stories ending at the paywall; D, a profile the user assembles with reactions arriving; E, a post action followed by a flow of reactions. Each concept has a hypothesis and a handoff to the paywall. Test order: run A, B and C first because they test three different mechanisms; D and E share one mechanism (social reaction) and run as a pair afterwards.
