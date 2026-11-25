---
name: ad-copy-production
description: A pipeline for producing ad text at volume for app and subscription businesses: angles from research, a hook bank, primary text, headlines and descriptions per platform with character limits, variant generation on cheaper models with selection and editing on the strongest model, claim and policy checks (health, finance, before and after, personal attributes), naming, a test plan and a cost line. Use when the user asks for "write ad copy at scale", "ad copy variants", "hook bank", "Meta ad text", "TikTok ad scripts", "Google ad headlines", "ad copy pipeline", or "check ad copy for policy".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Ad copy production pipeline

Moves ad text from research to a tested, policy-checked batch. Cheap models draft many variants, the strongest model selects and edits a few.

## When to use

- A test needs 20 to 60 text variants and a writer cannot keep up.
- Copy sounds alike across ads because every ad uses one angle.
- Ads get rejected or limited for claims.
- The team wants a naming scheme and a plan, not a pile of text.

Do not use to invent proof. Every claim must be backed by the product or the user's data.

## Inputs to collect first

1. Product facts: what it does, price and trial terms, what it does not do.
2. Audience research: reviews, support questions, interview quotes, competitor ads (see market-to-creative-brief, competitor-watch-weekly).
3. Past results: top and bottom ads by cost per payer, with their text.
4. Platforms and formats: Meta, TikTok, Google App campaigns, Apple Search Ads, with brand voice rules.
5. Languages and markets.
6. Budget for the copy run, if models are paid per call.

## Method

### Step 1. Angles from research

List 5 to 10 angles, each as: audience, problem, promise, proof available. Mark every angle by proof strength. Drop angles you cannot support.

### Step 2. Hook bank

Create 5 to 10 hooks per angle in real customer wording: a question, a pain statement, a result in a number you can prove, a contrast, a story opener. Store them in one table: hook, angle, format, date, result. Reuse winners in new wording.

### Step 3. Platform copy and limits

Draft per platform. Character limits and truncation points change, so verify them in each platform's current ad specs before final edit.

- Meta: primary text (the first lines show before truncation, so put the hook there), headline, description.
- TikTok: ad text and a spoken or on-screen script for the first seconds.
- Google App campaigns: short text lines, each standing alone, since they are combined.
- Apple Search Ads and store pages: follow the metadata limits of the store.

Keep a table of limits with the verification date and re-check each quarter.

### Step 4. Generate cheap, edit strong

1. Give a cheaper model the angle, hook, product facts, banned claims and the format. Ask for many variants per call.
2. Remove duplicates and near duplicates by a simple similarity check.
3. Send the shortlist to the strongest model with the brief and past winners. Ask it to select, score against the brief and rewrite the best ones in a human voice.
4. A human reads the final set. Cut filler, generic phrases and anything that sounds like a template.

### Step 5. Claim and policy check

Check every line before launch against current platform ad policies, and verify the policy pages rather than trusting memory.

- Health: no promise of diagnosis, cure or guaranteed results. No implying the viewer has a condition.
- Finance: no guaranteed returns or income. Include required disclosures.
- Before and after: avoid unrealistic or implied transformations, and be careful with body imagery.
- Personal attributes: do not assert or imply the viewer's age, health, finances, race, religion or similar traits ("Are you struggling with debt?").
- Pricing and trials: state the real price, billing period and renewal.
Output a pass, fix or reject label per line with the reason.

### Step 6. Naming and test plan

- Name: platform, angle code, hook code, format, language, version, date. Example: meta_a03_h12_static_en_v2_2026-11.
- Test plan: which variable is tested, number of variants, budget per variant, spend gate and kill line from your CAC (see ua-kill-scale-rules, meta-creative-testing).
- After the test, write winners back into the hook bank.

### Step 7. Cost line

Record: number of calls, model per stage, tokens in and out if available, price per run, and cost per accepted variant. Compare to the cost of writer time. If the user has a spend limit for model calls, ask before exceeding it.

## Output format

1. Angle table and hook bank.
2. Copy table per platform with character counts.
3. Policy check table.
4. Naming list and test plan.
5. Cost line and accepted variant count.

## Guardrails

- No invented testimonials, numbers, awards or user quotes.
- No benchmarks in the copy or the plan unless from the user's data, labelled "example, tune it" otherwise.
- Do not target or describe viewers by sensitive personal attributes.
- Platform limits and policies change. Tell the user to verify against current platform docs.
- Keep the voice plain: no filler openings, no stacked superlatives.

## Worked example (illustrative numbers)

6 angles x 8 hooks = 48 hooks. A cheap model drafts 4 texts per hook, 192 drafts. Deduplication leaves about 120. The strong model shortlists 24 and rewrites them. The policy check rejects 3 (an implied health diagnosis) and fixes 5. 16 go to test, 4 per angle for the 4 best angles, at a spend gate of 2x target CAC (example). Illustrative cost: if the run costs 6 in model calls, cost per accepted variant is 6 / 16 = 0.38.

## Related skills

meta-creative-testing for the test design, market-to-creative-brief for briefs.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-ad-copy-production). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
