---
name: unit-economics-check
description: Checks CAC, LTV and payback for a subscription or app business, finds which input makes the numbers unreliable, and sets a safe CAC ceiling. Use when the user asks "is my CAC okay", "calculate LTV", "payback period", "can we afford to scale", "unit economics check", "ROAS target", or "what CAC can we pay". Works from the user's own data and never from industry averages.
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
---

# Unit economics check (CAC, LTV, payback)

Answers one question: can this business pay for the traffic it is buying, and how much per customer.

## When to use

- Before raising paid budget.
- When ROAS looks fine but cash is tight, or the reverse.
- When a founder quotes an LTV number nobody can explain.
- When a new offer, price or plan changes the maths.

## Inputs

1. Spend by channel and period, and the number of paying customers by the same cut (not installs, not trials).
2. Revenue per customer cohort over time: month 0, 1, 2, 3 and so on, net of refunds and store fees.
3. Gross margin items: store or payment fees, refunds, chargebacks, variable costs per user (for example AI generation cost per active user).
4. Subscription mix: plans, trial rules, renewal rates by plan if available.
5. Cash constraints: how long the business can wait for payback.

## Method

### Step 1. Define the customer

A customer is a paying user. Write the definition down. Make sure spend and customers use the same definition and the same period, with lag allowed for trials.

### Step 2. CAC

CAC = paid acquisition spend / new paying customers from that spend. Report three versions and say which is used for decisions:

- Platform CAC (platform-reported payments).
- Backend CAC (payments in your own data, attributed).
- Blended CAC (all spend / all new payers, including organic).

If platform and backend CAC differ a lot, route the user to attribution-sanity-check before trusting either.

### Step 3. Contribution per customer, not revenue

Per customer revenue minus fees, refunds and variable cost. Use net numbers. Call it contribution.

### Step 4. LTV from cohorts, not formulas

Build cumulative contribution per customer by cohort month. Rules:

- Use observed months as observed. Project beyond them only with a stated retention assumption, and show the result as a range (low, base, high).
- Never use a single formula such as ARPU / churn on fewer than a few renewal cycles of data. Say the data is too young.
- Separate plans with different renewal behaviour. A weekly plan and an annual plan cannot share one retention curve.

### Step 5. Payback

Payback = the month in which cumulative contribution per customer reaches CAC. Report in months, and as a cash need: spend per month times payback months is the cash tied up while growing.

### Step 6. Safe CAC ceiling

Ceiling = cumulative contribution per customer at the payback horizon the business can finance, divided by a safety factor the owner picks (state it). Show what happens at ceiling for three budgets so the owner sees the cash curve.

### Step 7. Sensitivity

Show how the ceiling moves when each driver changes by a stated step: first-renewal rate, refund rate, trial to paid, price, variable cost. Name the driver with the largest effect. That is where to work first.

## Output format

1. Definitions used (customer, period, attribution source).
2. Table: CAC (three versions), contribution per customer, cumulative contribution by month, payback month.
3. LTV range with the assumptions that produce each end.
4. Safe CAC ceiling and cash need.
5. Sensitivity list, ranked.
6. Data gaps and the next measurement to add.

## Guardrails

- Never insert a "typical" LTV, churn or CAC from outside the user's data. If data is missing, list what to collect.
- Mark every projected number as projected.
- Keep revenue gross and net separate. Do not mix store-reported revenue with payment-processor revenue without saying so.
- No advice on investment decisions beyond marketing economics.

## Worked example (illustrative numbers)

Example only: 1,000 spend, 20 new payers, CAC 50. Net contribution per payer: month 0 is 18, month 1 adds 9, month 2 adds 7, month 3 adds 6, cumulative 18, 27, 34, 40. Payback has not happened by month 3 (40 < 50), so payback is beyond observed data. Verdict: with a 3-month financing limit, this CAC is above the ceiling of about 40. Options: raise first-month contribution (offer or price), lower CAC (creative, funnel), or accept a longer payback with cash to match.
