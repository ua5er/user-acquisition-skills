---
name: meta-ads-learning-audit
description: Audit a Meta (Facebook/Instagram) ad account that is stuck in "Learning limited", gets too few optimization events, or burned budget on failed tests, and write a post-mortem of past campaigns. Works from Ads Manager exports, screenshots or a browser session; an API token is optional. Use when the user asks "why are my Facebook ads not working", "learning limited fix", "facebook ads audit", "not enough optimization events", "why did these campaigns fail", "CPM too high", or wants a previous-campaigns analysis for a client or manager.
---

# Meta Ads learning audit and campaign post-mortem

The goal is one clear answer: **why the account does not produce enough conversions for Meta to learn, and what to change first.** Most "bad creatives" problems are really event-volume problems. Prove or disprove that before judging creatives.

## 1. Collect the data (pick what is available)

Ask once for whichever source is easiest, in this order:
1. Ads Manager export (CSV/XLSX) at **ad set** and **ad** level, date range "Maximum" plus "Last 30 days". Columns: campaign, ad set, ad, delivery, budget, spend, impressions, CPM, link clicks, CTR, results, cost per result, purchases, purchase value, ROAS, learning status, attribution setting, start date.
2. Screenshots of the same tables.
3. A logged-in browser session (Claude in Chrome, antidetect profile) or a Meta Ads MCP connector. Read only. Never publish drafts you did not create; the account may hold the owner's unpublished edits.
4. Events Manager: events received per day for the optimization event and the steps before it (PageView, Lead, InitiateCheckout, Purchase), plus Event Match Quality.

Also ask for: the funnel URL, the business model (one-off purchase or subscription with trial), and the target CPA if one exists.

## 2. Run the checks

### A. Event volume vs learning threshold (always first)
- Meta needs about **50 optimization events per ad set per 7 days** to exit learning. Translate it to the account: `events_per_day_needed = 50 / 7 ≈ 7`.
- For each active ad set: `events_per_week = purchases_last_7d`. Below 50 means it will not stabilize, whatever the creative.
- Minimum budget to learn: `daily_budget_min = target_CPA × 50 / 7`. Compare it to the real budget. Show the gap as one number ("you spend $120/day, learning needs ~$271/day at $38 CPA").
- Pixel total vs ad set share: if the pixel sees 14 purchases/day from all traffic but the main ad set gets 3, the account is not data-poor, the structure is splitting signal.

### B. Fragmentation
- Count ad sets that spent money in the last 14 days. Many ad sets with $50 to 150/day each and 0 to 2 purchases = signal split across too many learners.
- For each failed test ad set compute **spend needed to learn** (`target_CPA × 50`) vs **actual spend**. A test that got 1/5 of what it needed did not fail; it never ran.

### C. CPM and auction
- Compare CPM of small test ad sets to the main campaign. Small, narrow or fresh ad sets usually pay 1.5 to 2.5× more per 1,000 impressions. Report the multiple.
- Check placements and OS exclusions: ad-set level placement/OS exclusions are being deprecated in favour of account-level controls. Flag ad sets that still rely on them.

### D. Funnel and tracking
- Count screens or steps between ad click and the optimization event. If Meta only sees PageView until the final purchase, recommend intermediate events (QuizStart, QuizComplete, Lead, InitiateCheckout) via Pixel + CAPI.
- Event Match Quality below ~6: recommend passing email/phone hashes and fbp/fbc through CAPI.
- Attribution setting consistency across campaigns (7-day click + 1-day view vs others). Mixed settings make results incomparable.

### E. Creatives (only after A to D)
- Rank ads by purchases first, then CPA, then ROAS, across all time. Flag rejected ads, duplicates ("- Copy"), and ads with spend but 0 purchases.
- Note quality, engagement and conversion rankings if present.

### F. Account hygiene
- Setup errors on live ads (missing Instagram identity, rejected creatives).
- Automated rules that pause or restart campaigns on a schedule: list them and which campaigns they hit. These silently break learning.
- Unpublished drafts sitting on live ads.

## 3. Write the output

Produce two things:

**1. Diagnosis (5 to 8 bullets, plain language).** Each bullet: finding → number → consequence. Example: "5 test ad sets spent $256 to 318 each and got 0 to 2 purchases. Each needed ~$1,550 to learn. They were stopped at 1/5 of that, so they answered nothing."

**2. Previous campaigns table** (for a client or manager):

| Ad set | Daily budget | Spend | Purchases | CPA | CPM | Spend needed to learn | Verdict |
|---|---|---|---|---|---|---|---|

Then a short "what changes in the next launch" table: problem → fix.

If the user wants a shareable page, build it as an HTML artifact with the table, a bar per ad set (actual spend vs spend needed), and 3 to 4 findings. Keep numbers sourced: state the date range and currency.

## Rules
- Do not blame creatives while event volume is below threshold. Say so explicitly.
- Never fabricate numbers. If a metric is missing, write "not in export".
- Never change anything in the account during an audit.
- Keep the tone factual: the reader is often the person who launched the failed campaigns.
