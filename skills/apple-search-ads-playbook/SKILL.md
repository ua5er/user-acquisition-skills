---
name: apple-search-ads-playbook
description: Builds and runs an Apple Search Ads account for subscription apps: campaign structure (brand, category, competitor, discovery), keyword match types and negatives, Search Match, bids by CPT and cost per payer, custom product pages, attribution through the AdServices API and an MMP, and a weekly optimisation loop. Use when the user asks for "Apple Search Ads setup", "ASA structure", "ASA keywords", "search match", "CPT bids", "ASA campaign audit", "custom product pages for ads", or "why is ASA cost per install rising".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Apple Search Ads playbook for subscription apps

Gives an App Store search campaign a structure that separates intent, so each bid can be judged against cost per payer and not against cost per install.

## When to use

- Launching Apple Search Ads for a subscription app, or taking over an account nobody can explain.
- Cost per tap or cost per install is rising and nobody knows which keywords cause it.
- Brand, competitor and generic terms sit in one campaign and one budget.
- You need a weekly routine a person or a script can follow.

Do not use for apps with no payment event or no way to link a tap to a payer. Fix measurement first (see payment-capi-tracking and attribution-sanity-check).

## Inputs to collect first

1. Target CAC per payer and the payback window (see unit-economics-check).
2. Countries and storefronts, and the revenue split between them.
3. Current account export: campaign, ad group, keyword, match type, impressions, taps, installs, spend, by week.
4. Attribution setup: AdServices API token handling, MMP in use, which events reach Apple reporting and which reach your backend.
5. Subscription funnel rates from install to trial and trial to paid, by source if known.
6. Existing custom product pages and the app's top search terms from your ASO tool.

If the funnel rates are unknown, report cost per install only as a diagnostic and say the bid decisions are provisional.

## Method

### Step 1. Structure by intent

Use separate campaigns, each with its own budget and its own judging rule:

- Brand: your app name and close variants. Exact match. Low cost, defends the listing. Judge by share of brand searches won, not by growth.
- Category: generic terms that describe what the app does. Exact match first, broad match to find variants.
- Competitor: named rivals and their products. Expect lower conversion and higher cost per payer. Cap the budget and judge strictly.
- Discovery: Search Match on, plus broad match, with brand and known keywords added as negatives. Its job is to find new terms, not to scale.

Split by storefront when payment value differs a lot. Keep one theme per ad group so a keyword's result is readable.

### Step 2. Match types and negatives

- Exact match for terms with proven payers. Broad match only in discovery, where it feeds the keyword list.
- Promote a discovered term to exact when it reaches a payer count you set (example: three payers, tune it), then add it as a negative in discovery so budgets do not overlap.
- Add the same exact keyword as a negative across campaigns so one search triggers one ad group.
- Add negatives for irrelevant intent (free, jobs, unrelated apps) found in the search term report. Review the report weekly.

### Step 3. Search Match

Search Match matches searches Apple infers from your listing and metadata. Keep it on in discovery only, switch it off elsewhere, and read its search terms before trusting it. Verify the current behaviour in the Apple Search Ads documentation.

### Step 4. Bids from cost per payer

Work backwards from money:

1. Target cost per payer, from Step 1 of the inputs.
2. Install to payer rate for the keyword group (from your data).
3. Maximum cost per install = target cost per payer times that rate.
4. Maximum CPT bid = maximum cost per install times the tap to install rate.

Start below that maximum and raise only while cost per payer holds. Bid limits and bid types change, so verify against the current platform documentation.

### Step 5. Custom product pages

Map each campaign or ad group to a product page that matches the search intent: a competitor audience sees the comparison angle, a category audience sees the core benefit. Change one page element per test and compare tap to install and install to trial. Check page requirements in current Apple documentation.

### Step 6. Attribution

- Use the AdServices framework to attribute installs from search ads, and send the attribution token to your MMP or backend. Verify the current integration steps in Apple documentation.
- Join Apple's keyword level data to your own trial and payment events by campaign and keyword identifiers.
- Reconcile weekly: Apple reported installs against MMP installs against backend payers. A large gap means stop judging and fix the pipeline.

### Step 7. Weekly loop

1. Pull the search term and keyword report.
2. Add negatives, promote winners to exact, pause keywords that passed the spend gate (a multiple of target CAC, example 2x to 3x, tune it) with no payer.
3. Adjust bids in small steps (example: 10 to 20 percent) and log each change.
4. Check budget pacing and impression share on brand.
5. Record one learning and one test for next week.

## Output format

1. Account structure table: campaign, goal, match type, budget, judging metric.
2. Bid worksheet: keyword group, rates used, maximum CPT, starting bid.
3. Weekly action list: negatives, promotions, pauses, bid changes, each with its sample size.
4. Attribution reconciliation table and open data gaps.

## Guardrails

- Never state a benchmark for CPT, conversion rate or payer rate. Use the user's data or label a number "example, tune it".
- Platform field names, bid types, limits and API steps change. Tell the user to verify them against current Apple documentation before applying.
- Judge on payers, not installs, whenever payer data exists. State the sample size behind each verdict.
- Do not use a competitor's trademark in ad text or page copy where the platform policy forbids it.
- Keep audience claims honest: do not target or describe users by sensitive personal attributes.

## Worked example (illustrative numbers)

Target cost per payer: 60 (currency units). Category exact keyword group: install to payer rate 6 percent, tap to install rate 55 percent (examples). Maximum cost per install = 60 x 0.06 = 3.6. Maximum CPT = 3.6 x 0.55 = 1.98. Start the bid at 1.5 and raise in 15 percent steps while cost per payer stays under 60. A competitor keyword with spend 150, zero payers and 4 installs passes a 2.5x gate (150): pause it, keep it as a retest with a comparison product page.

## Related skills

ua-budget-planner for channel mix, payment-capi-tracking for event delivery, aso-store-listing for product page work, ua-kill-scale-rules for pause rules.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-apple-search-ads-playbook). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
