---
name: paywall-audit
description: Audits and redesigns a subscription app paywall or web checkout for clarity, price display, trust and testability, and outputs a ranked change list plus a test queue. Use when the user asks to "audit my paywall", "improve paywall conversion", "review pricing screen", "trial offer layout", "plan picker", "paywall A/B test plan", "web checkout price display", or "why do people not start trials". Adapted in part from two MIT-licensed skills, credited below.
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  adapted-from: "coreyhaines31/marketingskills paywalls (MIT, Corey Haines); appeeky/aso-skills paywall-optimization (MIT, Erencan)"
---

# Paywall audit

Adapted from `paywalls` in coreyhaines31/marketingskills (MIT, copyright Corey Haines) and `paywall-optimization` in appeeky/aso-skills (MIT, copyright Erencan). Their licence texts are reproduced in THIRD_PARTY_NOTICES.md. What is kept: the idea of scoring a paywall element by element and the principle of showing value before the ask. What is changed: the method below is rebuilt around evidence from the user's own funnel, a price-display and disclosure check, a stack of decision rules and a test queue. No benchmark tables from the source skills are carried over.

## When to use

- Trial start or paid conversion is below the business target.
- A redesign is planned and nobody knows what to keep.
- A web checkout or first-month offer is being added to an app funnel.
- Before an A/B test, to choose what to test first.

## Inputs

1. Screenshots or a prototype of every paywall state: first view, plan selected, checkout sheet, restore and error states.
2. Plan structure, prices, trial rules, renewal terms, regions.
3. Funnel numbers from the user's own data: paywall views, plan selections, checkout starts, trial starts, paid conversions, refunds. Last 30 days or the available window.
4. Where the paywall sits: after onboarding, after a value moment, on a feature gate.
5. What the traffic source promised (the ad or store page that brought the user).

## Method

### Step 1. Find the weakest funnel step

Compute step conversion from the user's own numbers and rank steps by the gap to the user's own previous period or target. Work on the weakest step only. If no funnel data exists, say so, run the audit anyway, and mark every finding as "unmeasured hypothesis".

### Step 2. Message match

Does the paywall continue the promise of the ad or the last onboarding screen? If the ad sold one outcome and the paywall sells features, fix the headline first.

### Step 3. Element audit

For each element give a verdict (fix, test, keep) and one reason:

1. Headline: states an outcome the user already wants.
2. Proof above the plans: real rating, count, or named result. Placeholder proof is a blocker. Use only numbers the business can substantiate.
3. Plans: what is selected by default and why, how plans differ, number of plans.
4. Price display: the full price and billing period stay visible next to the selected plan. A per-day or per-week price can be shown as a second line, never as the only price.
5. Trial terms: what happens at the end, the date of first charge, the price after.
6. CTA: one action, says what happens, matches the selected plan.
7. Trust: cancel instructions, restore purchases, terms and privacy reachable on the first screen.
8. Checkout sheet: order summary, discount line, total, secure payment cue.
9. Motion: entrance and press feedback support comprehension, use transform and opacity only, respect reduced motion.
10. Accessibility: contrast of small text, tap targets, labels for buttons.

### Step 4. Disclosure and fairness check

Before suggesting tactics, check the screen would pass a plain reading: a user can tell what they will be charged, when, and how to cancel. Platform rules (App Store review guidelines, Google Play policy, consumer law in the target regions) apply. Countdown timers and "limited" labels must reflect a real offer rule. If the offer does not truly expire, do not recommend a timer. Flag any dark pattern and recommend its removal.

### Step 5. Ranked change list

Score each finding by expected effect (high, medium, low, with the reasoning), effort, and risk. Put copy and disclosure fixes first, price-structure tests second, layout and motion polish last.

### Step 6. Test queue

Test one element at a time unless traffic allows a factorial design. For each test: hypothesis, primary metric (the one closest to money), guardrail metrics (refunds, D7 retention), minimum sample from the user's own baseline using a standard power calculation, and stop rule. Never declare a winner on platform-reported clicks alone.

## Output format

1. Funnel diagnosis (which step, evidence or "unmeasured").
2. Element table with verdicts.
3. Disclosure and fairness findings.
4. Ranked change list.
5. Test queue (first three tests in detail).
6. Redesign brief if requested: layout order, copy lines, states to design.

## Guardrails

- Never invent conversion benchmarks or "typical" lifts. Use the user's data or label as unknown.
- Placeholders such as [RATING] must be replaced with real numbers before shipping. Say so.
- Do not propose hidden fees, pre-checked add-ons, fake urgency or confusing cancel paths.
- Name designs and prices as examples when they come from a mock-up.

## Worked example

A mock-up for a subscription photo app, three plans (illustrative prices: a 1-day trial at 0.99 then 9.99 per week, a 1-week trial at 4.99 then 19.99 per month, one year at 49.99). Findings: rating line held a placeholder (blocker), per-day price shown larger than the billing price (risk), "Save 79%" computed against 12 monthly payments of 19.99 (acceptable if the comparison is stated), CTA did not name the price. Fixes: real proof, billing line equal in size to per-day line, CTA text includes the price of the selected plan, explicit date of first charge under the button. First test: default plan.
