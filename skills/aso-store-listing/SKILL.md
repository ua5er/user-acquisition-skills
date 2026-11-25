---
name: aso-store-listing
description: Plans App Store and Google Play listing work for subscription apps: keyword research and field allocation (title, subtitle, keyword field, short and long description), screenshot and preview video order, custom product pages and store listing experiments, ratings prompts, localisation priority by revenue, and measurement of conversion from page view to install. Use when the user asks for "ASO", "app store optimization", "app store keywords", "screenshots order", "Google Play listing", "store listing experiment", "custom product page", "localise app listing", or "improve app store conversion".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# ASO and store listing playbook for subscription apps

Treats the store page as a funnel step with a measurable conversion rate, and the metadata as a limited budget of characters.

## When to use

- A new listing is being written or an old one has not changed in a year.
- Installs from search are flat while paid traffic lands on the same page.
- Screenshots were designed once and never tested.
- The team wants to add languages and must choose which first.
- You need a test plan for custom product pages or store listing experiments.

Do not promise ranking results. ASO changes influence, they do not guarantee.

## Inputs to collect first

1. Revenue and installs by storefront for the last 3 to 6 months.
2. Store analytics export: impressions, product page views, installs, by source, by country if available.
3. Current metadata in every language, and character limits shown in the console.
4. Keyword data: your ASO tool's terms with popularity and difficulty as shown by that tool, plus Apple Search Ads search term reports.
5. Top competitors' listings, as seen in the stores.
6. Rating, review count and recent review themes.

## Method

### Step 1. Keyword research

1. Collect candidates from competitor listings, your search term reports, review text and the language users actually use.
2. Score each by relevance first, then by volume and difficulty as reported by your tool. Treat tool numbers as relative, not absolute.
3. Group by intent: core feature, problem, audience, brand and competitor. Drop terms that do not describe the app, because irrelevant installs lower conversion.
4. Check that paid search terms with real payers are present in the metadata too.

### Step 2. Field allocation

Verify current character limits and rules in each store's documentation.

- App Store: title and subtitle are indexed with the most weight, the keyword field is hidden and limited. Do not repeat a word across fields, since repeats waste space. Do not use competitor names or unproven claims.
- Google Play: title, short description and long description are indexed. Write the long description for people first, with key terms placed naturally, without stuffing.
- Put the highest relevance term in the title, supporting terms in the next fields, and keep wording readable.

### Step 3. Screenshots and preview video

- Order by what a new visitor needs: the main outcome first, proof or social signal, two or three core features, price or trial clarity last.
- The first two screenshots carry most of the decision. Make the first one readable at thumbnail size.
- One message per screenshot, short headline, real product screen. Keep style consistent across the set.
- Preview video: open with the outcome within the first seconds. Many users never press play, so do not hide the key message there.
- Use the same angles that win in paid creative (see market-to-creative-brief).

### Step 4. Custom product pages and experiments

- Custom product pages: one page per intent or channel, linked from ads and referral links. See apple-search-ads-playbook.
- Store listing experiments on Google Play and product page optimisation on the App Store: test one change per experiment, run to the platform's confidence readout and a full weekly cycle, and record the result even when it loses. Verify current tools and limits in the store consoles.

### Step 5. Ratings prompts

- Ask for a rating after a clear success moment, not at launch or after an error.
- Use the system prompt API, respect its frequency limits, and never gate it by sentiment where store policy forbids that. Verify the current policy.
- Reply to reviews, especially recurring complaints, and feed themes back to product.

### Step 6. Localisation priority

Rank storefronts by revenue and by installs, then by gap: high revenue with a poor localised listing comes first. Localise keywords by research in each language, not by literal translation. Localise screenshots text. Re-check the plan every quarter.

### Step 7. Measurement

- Core metric: conversion from product page view to install, per source and country, over at least a full week.
- Also track impressions to page view, and install to trial to payer rate by source, so a page that raises installs but lowers payers is caught.
- Log every change with the date, because store reports lag and effects overlap.

## Output format

1. Keyword table with group, relevance, tool metrics and target field.
2. Metadata draft per field with character counts.
3. Screenshot order and headline list, with one test idea.
4. Experiment plan: hypothesis, variant, metric, minimum duration.
5. Localisation queue by priority and the reason.

## Guardrails

- No invented benchmarks for conversion or volume. Use the user's analytics or "example, tune it".
- Limits and policies change. Tell the user to verify against current App Store and Google Play documentation.
- No misleading screenshots, fake awards or rating manipulation.
- A test with too few page views gets the verdict "not enough data".

## Worked example (illustrative numbers)

Product page views 20,000, installs 3,400 in a week, so conversion is 17 percent (example). Variant B opens with the outcome screenshot, gets 4,100 installs on 20,000 views, so 20.5 percent. Check the readout for confidence, then look at payers per 1,000 views: if it also rises, ship B. If installs rise but payers per view fall, keep A and rework the message.

## Related skills

market-to-creative-brief for angles, apple-search-ads-playbook for keyword data from paid search.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-aso-store-listing). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
