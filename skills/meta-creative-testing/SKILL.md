---
name: meta-creative-testing
description: Design creative testing for Meta Ads in the Andromeda era: choose which existing ads to relaunch based on real performance, decide between one broad ad set, ABO with a fixed budget per creative, or Meta's Creative Testing tool, set winner and kill criteria, and write briefs for designers and UGC creators. Use for "meta ads creative testing framework", "how to test ad creatives after andromeda", "ABO vs CBO for creative testing", "how to pick winning ad creatives", "static vs video ads", "UGC ad brief", "creative requirements for the design team".
---

# Meta creative testing framework

Goal: find the winning creative with the smallest budget, and keep a steady flow of new ones. Structure decisions come second; most accounts lose more money on too few creatives and too few events than on the "wrong" test structure.

## 1. Pick creatives from history
1. Export ads with date range "Maximum": ad name, delivery, spend, purchases, CPA, ROAS, CTR, quality ranking, creative thumbnail.
2. Rank by purchases, then CPA, then ROAS. Keep ads with a meaningful sample (≥ 5 purchases) or a CPA well under target on a small sample.
3. Drop: rejected ads (cannot be duplicated, re-upload an edited version instead), "- Copy" duplicates of an ad already picked, ads with spend ≥ 2× target CPA and 0 purchases, same visual already covered.
4. Write a one-line reason for every included and every excluded creative. Stakeholders ask for both.

Output table: creative | purchases | CPA | ROAS | in/out | reason.

## 2. Choose the test structure
| Option | When it fits | Cost of an answer |
|---|---|---|
| **One broad ad set (CBO), all creatives + auto-rules** (default) | Account below ~100 purchases/week; mixed static and video; budget-limited | Lowest: weak ads stop at ~2× target CPA |
| **ABO, fixed budget per creative** | High volume (each test ad set can reach ~50 events/week) or a hard requirement to compare concepts evenly | High: N creatives × (≥ 3 to 4× target CPA) before any verdict |
| **Meta Creative Testing tool** (2 to 5 ads inside an existing ad set, equal split, then back to normal delivery) | Need a fair read on 2 to 5 specific new ads without a new ad set | Medium: the test budget is spent evenly regardless of early signal |

Explain the default with this logic (use the account's numbers):
- With a fixed budget, a weak creative spends its full budget even when it is clearly losing on day 1, and a strong one is capped and starves.
- 11 creatives at $150 each = $1,650 for one answer. Previous fixed-budget tests that got $250 to 320 each and 0 to 2 purchases answered nothing.
- In one ad set, Meta shifts spend to creatives with early signals; the stop rule caps the loss on a bad creative at ~2× target CPA.
- Each creative is a separate ad with a clear name, so per-creative metrics stay visible.
- Testing tools are also built to increase test spend. The advertiser's goal is the cheapest winner.

Mixing static and video in one ad set is fine: one format taking most of the spend is itself the answer.

## 3. Winner and kill criteria
- **Kill:** spend ≥ 2× target CPA and 0 purchases; or spend > 4× target CPA and < 3 purchases.
- **Winner:** ≥ 5 purchases at CPA ≤ target over ≥ 3 days, while still getting spend share.
- **Keep watching:** everything else. Do not judge on CTR alone.
- **Fatigue:** frequency > 3 with CTR falling and CPA rising over 5 to 7 days.
- Restart rule for late attribution: a paused ad that later shows 2+ purchases in 3 days at CPA under target goes back on.

## 4. Creative pipeline
- New batch every week, 3 to 6 creatives, into the same ad set. Concepts, not small variations: different angle, persona, hook, format.
- Mix: proven winner iterations (new hook on the same idea), new angles, UGC video, static with a strong headline.
- Name every ad: `PROJECT | TEST | Format | Concept | src: file_or_original`.

## 5. Brief template for designers and UGC creators
```
Product / offer:
Audience and their main pain (one sentence):
Angle (why now, what changes for them):
Hook (first 1 to 3 seconds / headline):
Proof (number, review, demo):
CTA:
Format: 9:16 video 15 to 30s / 1:1 and 4:5 static / both
Must avoid: income promises, before/after claims, platform policy risks for the vertical
Reference ads (links from Ad Library or account winners):
Deliverables and deadline:
```
Generate 3 to 5 filled briefs from the winners' patterns and the funnel's selling points. For UGC, add a shot list and a script with the hook in the first line.

## 6. Reporting
Weekly table: creative | spend | purchases | CPA | ROAS | status (winner / watch / killed / fatigued) | next action. One paragraph on what the batch taught us and what the next batch tests.

## Rules
- Never declare a winner below 5 purchases unless the client accepts the risk in writing.
- Do not change creatives and budget on the same day; batch changes weekly.
- Keep claims in ad copy policy-safe for the vertical (employment, health, finance).
