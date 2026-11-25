---
name: static-ad-production
description: Production pipeline for static ad creatives on Meta, TikTok and other placements: an English brief built only from a product facts file, concepts and hooks from the strongest model, layouts in HTML or Figma by a cheaper builder model, image drafts on a cheap image model then the approved pick on the hero model, copy as live text layers, export to 1:1, 4:5 and 9:16 with safe zones, contact sheet review, a quick persona panel, a QA gate, naming and a cost line per batch. Use when the user asks for "static ad pipeline", "produce image ads at scale", "ad creative workflow with AI", "generate banner variations", "ad sizes and safe zones", "creative QA checklist", "batch of Meta image ads", or "cost per creative batch".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Static ad production pipeline

A repeatable way to turn product facts into a batch of tested-ready static ads, with each model doing only the job it is good and cheap at.

## When to use

- A creative sprint needs 10 to 40 static ads in a few days.
- Ads come out inconsistent, claims drift, or text inside images is garbled.
- The cost of image generation is unclear and keeps growing.

## Inputs to collect first

1. A product facts file: what the product does, real features, prices, trial terms, proof you can show, legal lines. Everything claimed in ads must come from here.
2. Audience and the market snapshot or research notes, if you have them (see competitor-creative-parser and market-to-creative-brief).
3. Brand assets: logo, fonts, colours, app screenshots.
4. Target placements and the platform policies that apply.
5. Budget for generation per batch, and the review owner.

## Method

### Step 1. Write the brief from facts only

English, short. Fields: goal, audience, one promise, proof, offer, call to action, banned claims. Every line cites a row of the facts file. If a claim has no source, drop it.

### Step 2. Concepts and hooks (strongest model)

- Ask for distinct concepts, not variations of one: different angle, different first-glance message.
- Per concept: hook line, headline, subline, visual idea, why it should stop a thumb.
- Keep 6 to 12 concepts. Cut near-duplicates before building.

### Step 3. Layouts (cheaper builder model)

- Build each layout as HTML or in Figma with real text layers, a grid, a safe-zone guide and brand tokens.
- Copy stays live text. Never bake copy into generated images: it garbles, cannot be edited and breaks localisation.
- One template per concept, parameterised, so sizes and languages are exports, not redraws.

### Step 4. Images (cheap draft, hero final)

- Draft the visual on a cheap image model. Review the drafts quickly and pick.
- Render only the approved pick on the hero model. Maximum 3 takes per image.
- If it is still off, make one edit with a reference image instead of regenerating from scratch.
- Do not use product shots or screens that misrepresent the app. Real screenshots come from files.
- Quote the cost before any paid generation (see Step 9).

### Step 5. Export sizes and safe zones

- 1:1 and 4:5 for feeds, 9:16 for stories and reels.
- Keep key text and the product inside the platform safe zones, away from UI overlays at the top and bottom of 9:16. Check the current platform spec before each batch.
- Export from the live layout, so every size has the same copy.

### Step 6. Contact sheet review

Put all ads on one sheet at thumbnail size. Check what reads at a glance, what repeats, what looks off. A person picks, rejects and notes fixes.

### Step 7. Persona glance panel

Show the survivors to a small set of described buyer profiles (see creative-preflight-panel) and note which message each reads. It is a filter, not a live test.

### Step 8. QA gate

- Claims: each one traced to the facts file.
- Specs: size, file weight, format, text share limits where the platform has them.
- Contrast and legibility at phone size.
- Policy: personal attributes, before and after rules, health and money claims, trademark use.
- Typos and price, trial and currency correctness.

### Step 9. Name and cost

- Naming: `concept_angle_format_size_version`, one scheme for the whole account.
- Cost line per batch: concepts, drafts, hero renders, edits, units, cost per unit and the total. Compare with the quote.

Per-ad record to keep in a sheet:

- Ad name, concept, angle and hook line.
- Source fact row for every claim.
- Models and takes used for the image, with the cost.
- Sizes exported and the QA result.
- Launch date, test cell and the result when it arrives.

## Output format

1. Brief with fact references.
2. Concept table.
3. Layout files and exports by size.
4. Contact sheet and review notes.
5. QA checklist result with pass or fail per ad.
6. Naming list and the cost line.

Model roles at a glance: strongest model for concepts and hooks, cheaper builder model for layouts and variants, cheap image model for drafts, hero image model only for approved picks. Check current prices before each batch, since they change.

## Guardrails

- Claims come only from the facts file. Do not invent features, results, reviews or prices.
- No fake testimonials, fake UI or fabricated numbers.
- Follow platform ad policies. Do not generate real people's likenesses without rights.
- Ask for a cost quote before paid generation, and stop at the approved cap.
- A person approves every ad before it goes live.

## Worked example (illustrative numbers)

Example batch: 8 concepts, 4 survive the contact sheet. Drafts: 8 images at a low price per image (example 0.02 each) = 0.16. Hero renders: 4 images, up to 3 takes each, 12 at most at 0.20 (example) = 2.40. Edits: 2 at 0.20 = 0.40. Quote 3.00, actual 2.96. Each of the 4 concepts exports to 3 sizes, giving 12 files. QA fails 1 ad because the headline promised a result not in the facts file. It is fixed and passes on the second check.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-static-ad-production). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
