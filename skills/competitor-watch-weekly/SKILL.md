---
name: competitor-watch-weekly
description: Runs a scheduled weekly watch of competitors in public ad libraries (Meta Ad Library, TikTok Creative Center) and on App Store and Google Play pages (screenshots, titles, prices, paywall, ratings), keeps store snapshots, diffs them week over week and writes a weekly brief with new angles, ads that survived two or more weeks, price and paywall changes and what to test. Use when the user asks for "weekly competitor monitoring", "track competitor ads", "competitor app store changes", "what changed at competitors this week", "ad library watch", "competitor paywall changes", "weekly competitor brief", or "which competitor ads are still running".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Competitor watch (weekly)

A light, repeatable routine: capture the same public pages every week, compare with last week, and write a one-page brief that ends in test ideas. For a one-off deep snapshot of a market, use competitor-creative-parser instead. This skill is the cheap loop that runs between those deep dives.

## When to use

- You want to know what competitors changed without browsing by hand every week.
- A creative sprint needs fresh angles, and a list of what competitors keep running.
- You suspect a competitor changed price, trial or paywall.

## Inputs to collect first

1. Competitor list: 5 to 15 advertisers, with page ids, app store ids and package names.
2. Markets and languages to watch.
3. Your own current angles, prices and paywall, so the brief can compare.
4. Where snapshots are stored (folder, repository or sheet) and where the brief goes.
5. Schedule: day and time, and who reads the brief.

## Method

### Step 1. Define the watch list

- One row per competitor: ad library page, store listing per market, app name.
- Add a tag for why they are on the list (direct rival, adjacent, market leader).
- Review the list each quarter. Drop dead entries, add newcomers.

### Step 2. Capture ads from public libraries

- Use the official Meta Ad Library (and its API where you have access) and the TikTok Creative Center and its public data.
- Record per ad: ad id, advertiser, first seen date, last seen date, format, copy, call to action, landing target, number of variations when shown.
- Save the media file or a thumbnail only where terms allow. Otherwise save the link and your own text description.
- Stay inside platform terms: no login-wall scraping, no bypassing rate limits.

### Step 3. Snapshot the store pages

Weekly, per market, save a dated copy of:

- App title and subtitle, short and long description.
- Screenshots and preview video (a hash or the files).
- Prices and in-app purchase list, trial length shown.
- Rating, review count and the newest review themes.
- Paywall seen in a fresh install, if you test it by hand: plans, price display, trial wording, close button.

### Step 4. Diff against last week

Compare today with the previous snapshot and list only changes: new ads, ended ads, copy edits, new screenshots, new prices, paywall layout changes, rating moves. Unchanged items are not reported.

### Step 5. Read signals correctly

- Ad library data shows existence, dates and variations. It does not show spend, CTR, conversions or ROAS. Never claim an ad "performs".
- An ad running two or more weeks is a longevity signal, not proof of profit. Say "survived", not "wins".
- Many variations of one idea suggest the advertiser is testing it.
- An approach counts as a market pattern only with two or more independent signals and two or more advertisers (for example the same angle live in ads and in store screenshots, at two companies). One signal is a note, not a trend.

### Step 6. Write the weekly brief

1. New angles: what appeared, by whom, how it differs from yours.
2. Survivors: ads live for two or more weeks, with first seen date.
3. Store and price changes: before and after.
4. Paywall changes.
5. Pattern check: which approaches pass the two signal, two advertiser rule.
6. What to test: three ideas at most, each with a hypothesis and the metric to read.

### Step 7. Schedule and keep history

Run on a fixed day with a scheduler. Keep all snapshots, so a month of diffs can be read as a timeline. Note any capture failures in the brief.

Capture routine (short checklist):

- Same pages, same markets, same day each week.
- Save the raw capture before any summary, so a summary can be rechecked.
- Note the capture time and the tool or method used.
- Use the same file names and folder layout every week.
- Keep a short log of failures: page changed, library down, item missing.

## Output format

- A dated brief of one page.
- A change table: competitor, item, before, after, signal strength.
- A test queue linked to the brief.
- A snapshot folder with consistent file names.

How to keep the brief short:

- Report changes, not the whole state.
- Cap new angles at five and tests at three.
- Put weak signals in a "watch" line, not in the main findings.
- Link each item to its saved snapshot.

## Guardrails

- Public data only, within platform terms. No private accounts, no fake users, no scraping behind logins.
- Do not copy competitor creative. Learn the angle, then write your own.
- Never infer spend or results from ad library data.
- Mark every inference as a hypothesis. State the sample: how many ads, how many advertisers.
- Do not name a trend from a single advertiser.

## Worked example (illustrative)

Ten competitors watched. This week two new ads appear at advertiser A and one at B, all using a "before and after in 7 days" angle (example). Advertiser C changed its first screenshot to show the same promise. That is three advertisers and two kinds of signal (ads and store), so the angle is logged as a pattern. Two of A's ads have run for three weeks, so they are survivors. Advertiser D raised its monthly price and moved the trial toggle (example). Brief says: test one "7 days" concept against our best control, and review our own price display.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-competitor-watch-weekly). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
