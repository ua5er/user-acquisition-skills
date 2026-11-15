# Example: parse a fictional market, write the briefs

**The market is fictional. The tags are real model output.** Five invented sleep improvement apps ("Brand A" to "Brand E") and their 24 invented ads were written for this example. Jev (`jev-1.14.0`, TypeSafe AI's direct endpoint) tagged the descriptions live on 2026-11-15, and code counted the result. No real ad library was parsed, no real brand appears, and nothing here says anything about how real ads perform. "Brand Z", the team the briefs are written for, is invented too; its budget and target CPA are example values.

The chain uses the Claude + Jev skills in this repository:

1. `competitor-creative-parser`: capture, Claude describes, Jev tags, code builds the snapshot.
2. `market-to-creative-brief`: Claude picks the moves and writes the briefs, code checks every number against the snapshot and assembles the pack.

## What went in

| Input | File | Count |
|---|---|---|
| Capture records | `skills/competitor-creative-parser/scripts/sample_market/creatives.jsonl` | 24 (12 static, 12 video), 5 advertisers |
| Descriptions (the state Jev reads) | `skills/competitor-creative-parser/scripts/sample_market/descriptions.jsonl` | 24, videos with transcripts and cut times |
| Question sets | `questions_static.py` (17 questions), `questions_video.py` (21 questions) | |
| Team constraints and decisions | `skills/market-to-creative-brief/scripts/sample_decisions.json` | 6 decisions, 3 static and 3 motion briefs |

Images and videos never go to Jev: only the text descriptions do.

## Live run: tokens and cost

| Run | Creatives | Requests | Input tokens | Cost at $0.042 per million |
|---|---|---|---|---|
| Smoke (3 creatives, shape check) | 3 | 3 | 5,793 | $0.00024 |
| Static track, with an order check on 6 | 12 | 18 | 31,330 | $0.00132 |
| Video track, with an order check on 6 | 12 | 18 | 35,377 | $0.00149 |
| Total | 24 | 39 | 72,500 | $0.0030 |

Token counts come from the API's usage field. Errors: 0. Every creative came back in the documented response shape.

Order check (the same creative asked twice with Choice options in rotated and reversed order): every static Choice agreed 6 of 6; on video, angle agreed 5 of 6 and hook type 4 of 6, the rest 6 of 6. Hook type on video is the question to keep in review until it is rewritten or calibrated.

Review queue: 19 static rows and 27 video rows wait for a person (review band, conflicts between a Choice and its companion yes/no, untagged items). The saved output is in `skills/competitor-creative-parser/scripts/sample_market/live-run-2026-11-15/`.

Commands:

```
cd skills/competitor-creative-parser/scripts
python3 tag_creatives.py sample_market/descriptions.jsonl --track static --smoke --data-handling-confirmed --out-dir run
python3 tag_creatives.py sample_market/descriptions.jsonl --track static --order-check 6 --max-usd 0.05 --data-handling-confirmed --out-dir run
python3 tag_creatives.py sample_market/descriptions.jsonl --track video --order-check 6 --max-usd 0.05 --data-handling-confirmed --out-dir run
python3 market_snapshot.py --creatives sample_market/creatives.jsonl --tags run/tags-static.jsonl run/tags-video.jsonl \
    --out-dir run --market "sleep improvement apps, English (FICTIONAL sample market)"
cd ../../market-to-creative-brief/scripts
python3 brief_pack.py --decisions sample_decisions.json --snapshot sample_snapshot.json --out brief-pack.md \
    --gates-csv copy-check.csv --panel-concepts concepts.jsonl
```

Both tracks hold 12 creatives, under the 20-creative guard, so the snapshot ranks nothing and marks every label low sample. That is the honest reading of 12 ads: directional.

## Step 1 output: the market snapshot

As written by `market_snapshot.py` (headings shifted one level).

Built 2026-11-15. Ad libraries show what runs and for how long, not spend or results. Shares are of the track's tagged creatives; unresolved items (review band, conflicts, untagged) are counted apart and wait for a person.

### Static track

Creatives tagged: 12 from 5 advertisers (Brand A 3, Brand B 2, Brand C 3, Brand D 2, Brand E 2). Errors: 0. Model: jev-1.14.0. Source: live.

**Low sample: 12 creatives, under 20. Nothing is ranked, labels below are directional, the durability list is withheld.**

#### hook_type (taxonomy order (low sample, not ranked); unresolved 1)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| problem_callout | 0 | 0% | 0 | 0% |  |
| outcome_promise | 8 | 67% | 5 | 100% |  |
| question | 2 | 17% | 2 | 40% |  |
| social_proof | 1 | 8% | 1 | 20% |  |
| curiosity | 0 | 0% | 0 | 0% |  |
| comparison | 0 | 0% | 0 | 0% |  |
| offer_price | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### angle (taxonomy order (low sample, not ranked); unresolved 3)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| save_time | 0 | 0% | 0 | 0% |  |
| feel_better | 5 | 42% | 4 | 80% |  |
| get_result | 4 | 33% | 3 | 60% |  |
| save_money | 0 | 0% | 0 | 0% |  |
| belonging_status | 0 | 0% | 0 | 0% |  |
| fear_of_missing_out | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### offer_type (taxonomy order (low sample, not ranked); unresolved 1)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| free_trial | 8 | 67% | 4 | 80% |  |
| discount | 1 | 8% | 1 | 20% |  |
| freemium_download | 1 | 8% | 1 | 20% |  |
| price_stated | 0 | 0% | 0 | 0% |  |
| none | 1 | 8% | 1 | 20% |  |
| other | 0 | 0% | 0 | 0% |  |

#### visual_format (taxonomy order (low sample, not ranked); unresolved 2)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| ugc_photo | 3 | 25% | 3 | 60% |  |
| app_screenshot | 2 | 17% | 1 | 20% | one advertiser supplies most |
| text_card | 1 | 8% | 1 | 20% |  |
| before_after | 0 | 0% | 0 | 0% |  |
| testimonial_card | 1 | 8% | 1 | 20% |  |
| illustration_3d | 1 | 8% | 1 | 20% |  |
| meme_native | 0 | 0% | 0 | 0% |  |
| lifestyle_stock | 2 | 17% | 2 | 40% |  |
| other | 0 | 0% | 0 | 0% |  |

#### offer_placement (taxonomy order (low sample, not ranked); unresolved 3)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| headline | 0 | 0% | 0 | 0% |  |
| badge_sticker | 3 | 25% | 3 | 60% |  |
| cta_button | 2 | 17% | 2 | 40% |  |
| footer_line | 2 | 17% | 2 | 40% |  |
| not_shown | 2 | 17% | 2 | 40% |  |
| other | 0 | 0% | 0 | 0% |  |

#### Crowded, gaps, single advertiser

- Crowded: hook_type outcome_promise, 67% of creatives, 100% of advertisers (low sample)
- Crowded: angle feel_better, 42% of creatives, 80% of advertisers (low sample)
- Crowded: angle get_result, 33% of creatives, 60% of advertisers (low sample)
- Crowded: offer_type free_trial, 67% of creatives, 80% of advertisers (low sample)
- Gap (no resolved creative uses it): hook_type problem_callout, hook_type curiosity, hook_type comparison, hook_type offer_price, angle save_time, angle save_money, angle belonging_status, angle fear_of_missing_out, offer_type price_stated, visual_format before_after, visual_format meme_native, offer_placement headline (low sample)
- Used by one advertiser only: hook_type social_proof (1), offer_type discount (1), offer_type freemium_download (1), offer_type none (1), visual_format app_screenshot (2), visual_format text_card (1), visual_format testimonial_card (1), visual_format illustration_3d (1)

#### Flags and scores

| Flag | Yes | Share | Review |
|---|---|---|---|
| social_proof | 2 | 17% | 0 |
| urgency | 1 | 8% | 0 |
| risky_claim | 2 | 17% | 5 |
| personal_attribute | 1 | 8% | 4 |

- hook_specificity: mean 1.25 on a 0 to 3 scale, levels {'0': 1, '1': 8, '2': 3, '3': 0}
- cta_clarity: mean 1.52 on a 0 to 2 scale, levels {'0': 0, '1': 6, '2': 6}
- legibility: mean 1.94 on a 0 to 2 scale, levels {'0': 0, '1': 0, '2': 12}

#### Code facts

- words_on_image: {"min": 6, "median": 11.5, "max": 17}
- has_price: 2
- cta_labels: {"Start free": 2, "Start free trial": 2, "Try free": 2, "Claim 50% off": 1, "Download": 1, "Get started": 1, "Join now": 1, "Start free week": 1, "Take the check": 1}
- aspect_ratios: {"1:1": 11, "4:5": 12, "9:16": 1}

#### Durability (weak signal)

Median runtime: 52.0 days.
Longest-running list withheld under the sample guard.

### Video track

Creatives tagged: 12 from 5 advertisers (Brand A 2, Brand B 3, Brand C 2, Brand D 3, Brand E 2). Errors: 0. Model: jev-1.14.0. Source: live.

**Low sample: 12 creatives, under 20. Nothing is ranked, labels below are directional, the durability list is withheld.**

#### hook_type (taxonomy order (low sample, not ranked); unresolved 5)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| problem_callout | 2 | 17% | 2 | 40% |  |
| bold_claim | 1 | 8% | 1 | 20% |  |
| question | 1 | 8% | 1 | 20% |  |
| pattern_interrupt | 0 | 0% | 0 | 0% |  |
| demo_first | 1 | 8% | 1 | 20% |  |
| story_opener | 1 | 8% | 1 | 20% |  |
| social_proof | 0 | 0% | 0 | 0% |  |
| other | 1 | 8% | 1 | 20% |  |

#### hook_channel (taxonomy order (low sample, not ranked); unresolved 1)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| spoken_line | 9 | 75% | 5 | 100% |  |
| on_screen_text | 2 | 17% | 2 | 40% |  |
| visual_action | 0 | 0% | 0 | 0% |  |
| sound | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### angle (taxonomy order (low sample, not ranked); unresolved 7)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| save_time | 0 | 0% | 0 | 0% |  |
| feel_better | 1 | 8% | 1 | 20% |  |
| get_result | 4 | 33% | 3 | 60% |  |
| save_money | 0 | 0% | 0 | 0% |  |
| belonging_status | 0 | 0% | 0 | 0% |  |
| fear_of_missing_out | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### video_format (taxonomy order (low sample, not ranked); unresolved 0)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| ugc_talking_head | 6 | 50% | 5 | 100% |  |
| screen_recording | 2 | 17% | 2 | 40% |  |
| motion_graphics | 1 | 8% | 1 | 20% |  |
| voiceover_broll | 1 | 8% | 1 | 20% |  |
| split_screen_reaction | 1 | 8% | 1 | 20% |  |
| skit_dramatized | 1 | 8% | 1 | 20% |  |
| slideshow_static | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### structure (taxonomy order (low sample, not ranked); unresolved 4)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| problem_solution | 4 | 33% | 3 | 60% |  |
| demo_walkthrough | 2 | 17% | 2 | 40% |  |
| testimonial_story | 0 | 0% | 0 | 0% |  |
| listicle_tips | 1 | 8% | 1 | 20% |  |
| before_after | 1 | 8% | 1 | 20% |  |
| challenge_trend | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### creator_type (taxonomy order (low sample, not ranked); unresolved 2)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| everyday_person | 7 | 58% | 4 | 80% |  |
| expert_authority | 0 | 0% | 0 | 0% |  |
| influencer | 0 | 0% | 0 | 0% |  |
| faceless | 3 | 25% | 3 | 60% |  |
| other | 0 | 0% | 0 | 0% |  |

#### offer_type (taxonomy order (low sample, not ranked); unresolved 0)

| Value | Creatives | Share | Advertisers | Advertiser share | Note |
|---|---|---|---|---|---|
| free_trial | 10 | 83% | 4 | 80% |  |
| discount | 1 | 8% | 1 | 20% |  |
| freemium_download | 1 | 8% | 1 | 20% |  |
| price_stated | 0 | 0% | 0 | 0% |  |
| none | 0 | 0% | 0 | 0% |  |
| other | 0 | 0% | 0 | 0% |  |

#### Crowded, gaps, single advertiser

- Crowded: hook_channel spoken_line, 75% of creatives, 100% of advertisers (low sample)
- Crowded: angle get_result, 33% of creatives, 60% of advertisers (low sample)
- Crowded: video_format ugc_talking_head, 50% of creatives, 100% of advertisers (low sample)
- Crowded: structure problem_solution, 33% of creatives, 60% of advertisers (low sample)
- Crowded: creator_type everyday_person, 58% of creatives, 80% of advertisers (low sample)
- Crowded: offer_type free_trial, 83% of creatives, 80% of advertisers (low sample)
- Gap (no resolved creative uses it): hook_channel visual_action, hook_channel sound, video_format slideshow_static, creator_type expert_authority, creator_type influencer, offer_type price_stated, offer_type none (low sample)
- Possible gap, too many unresolved items in the dimension to be sure: hook_type pattern_interrupt, hook_type social_proof, angle save_time, angle save_money, angle belonging_status, angle fear_of_missing_out, structure testimonial_story, structure challenge_trend
- Used by one advertiser only: hook_type bold_claim (1), hook_type question (1), hook_type demo_first (1), hook_type story_opener (1), angle feel_better (1), video_format motion_graphics (1), video_format voiceover_broll (1), video_format split_screen_reaction (1), video_format skit_dramatized (1), structure listicle_tips (1), structure before_after (1), offer_type discount (1), offer_type freemium_download (1)

#### Flags and scores

| Flag | Yes | Share | Review |
|---|---|---|---|
| product_in_first_3s | 0 | 0% | 1 |
| cta_in_end | 12 | 100% | 0 |
| social_proof | 3 | 25% | 0 |
| urgency | 1 | 8% | 0 |
| risky_claim | 4 | 33% | 4 |
| personal_attribute | 1 | 8% | 3 |

- hook_specificity: mean 1.36 on a 0 to 3 scale, levels {'0': 0, '1': 9, '2': 2, '3': 1}

#### Code facts

- duration_s: {"min": 20.0, "median": 29.0, "max": 40.0, "n": 12}
- cuts_per_10s: {"min": 1.0, "median": 1.58, "max": 2.73, "n": 12}
- avg_shot_s: {"min": 3.14, "median": 5.0, "max": 8.0, "n": 12}
- captions_yes: 10

#### Durability (weak signal)

Median runtime: 52.0 days.
Longest-running list withheld under the sample guard.

## Step 2 output: the brief pack

As written by `brief_pack.py` from `sample_decisions.json`, which Claude wrote by following `market-to-creative-brief` on this snapshot (headings shifted one level).

> FICTIONAL example: the market, the ads and the team are invented. The snapshot numbers are real Jev output on the invented ads. Budget and CPA are example values.

Snapshot built 2026-11-15. Ad libraries show what runs and for how long, not spend or results. A person approves this pack before any production or spend.

- static track: 12 creatives from 5 advertisers, LOW SAMPLE, directional only.
- video track: 12 creatives from 5 advertisers, LOW SAMPLE, directional only.

### Warnings

- track static has 12 creatives, under 20: decisions D1, D2, D3 are directional only
- track video has 12 creatives, under 20: decisions D4, D5, D6 are directional only

### Team constraints

- Brand rules: Calm, plain tone. No medical claims: never cure, treat, fix or diagnose insomnia or any condition. No invented reviews or user counts. No before and after of bodies or faces.
- Offers allowed: 7-day free trial, then an annual plan; the annual price is shown in full wherever a price appears.
- Can produce: Static: one in-house designer. Motion: one motion designer for screen-based and kinetic type work. UGC: one creator shoot per month.
- Own performance data: none supplied, nothing is cited
- Test budget 1500 USD at target CPA 25 (example values): about 30 creatives can reach a kill read (spend of 2x target CPA each, rule from meta-creative-testing); this pack plans 15.

### Decisions

| Id | Track | Move | What | Concepts | Evidence | Ads |
|---|---|---|---|---|---|---|
| D1 | static (low sample) | enter_gap | hook_type comparison | 2 | static hook_type comparison creatives = 0; static hook_type outcome_promise creatives = 8; static hook_type outcome_promise advertiser_share = 100%; static hook_type unresolved = 1 | s01, s05, s09, s11 |
| D2 | static (low sample) | out_execute | hook_type outcome_promise | 1 | static hook_type outcome_promise share = 67%; static hook_specificity score_mean = 1.25; static offer_type price_stated creatives = 0 | s01, s06, s09 |
| D3 | static (low sample) | avoid | risky_claim  | 0 | static risky_claim flag_yes = 2; static risky_claim flag_review = 5 | s03, s04 |
| D4 | video (low sample) | enter_gap | hook_channel visual_action | 2 | video hook_channel visual_action creatives = 0; video hook_channel spoken_line creatives = 9; video product_in_first_3s flag_yes = 0; video product_in_first_3s flag_review = 1 | v06, v12, v02 |
| D5 | video (low sample) | out_execute | video_format ugc_talking_head | 1 | video video_format ugc_talking_head creatives = 6; video video_format ugc_talking_head advertiser_share = 100%; video hook_specificity score_mean = 1.36; video cuts_per_10s.median fact = 1.58 | v01, v03, v11 |
| D6 | video (low sample) | avoid | risky_claim  | 0 | video risky_claim flag_yes = 4; video risky_claim flag_review = 4 | v09, v03 |

**D1.** No static in the market sets the routine against an alternative, while 8 of 12 lead with an outcome promise and all 5 advertisers use it. A comparison hook stands apart in the feed without needing a stronger promise than the others.

Hypothesis for the test: A comparison headline (routine against an alternative) gets a lower cost per trial than an outcome-promise control, because nobody else in the feed uses it.

**D2.** Outcome promises are the crowded default, so one concept enters it with a sharper line: hook specificity averages 1.25 on a 0 to 3 scale and no static reaches the top level (audience, promise and a timeframe). The promise is about the routine, which the product can keep, not about sleep results.

Hypothesis for the test: An outcome promise with audience, promise and timeframe in one line beats the market's vaguer promises on cost per trial.

**D3.** Health and guaranteed-result claims are common in this market (2 statics flagged, 5 more in review). Brand rules forbid them and they invite rejection. No concept uses cure, fix or a sleep-time guarantee.

**D4.** 9 of 12 videos carry the hook with a spoken line and none with a visual action; none shows the product in the first 3 seconds (one in review). Two concepts open on the product doing something on screen, with no talking.

Hypothesis for the test: Opening on the product doing something, with no speech in seconds 0 to 3, holds more viewers past 3 seconds than a spoken opening.

**D5.** Talking heads are half of the market and every advertiser runs one, so the team's monthly UGC shoot only earns its place with a different opening: the app on screen in the creator's hand from the first frame and a specific line (video hook specificity averages 1.36 of 3). Pacing stays near the market median of 1.58 cuts per 10 seconds; the difference is in the first 3 seconds, not the edit.

Hypothesis for the test: A talking head with the app in hand from the first frame beats a talking head that shows the app later, on cost per trial.

**D6.** 4 videos are flagged for health or result claims and 4 more sit in review, including a 'completely cured' line. No script promises a cure, a number of hours or minutes to fall asleep, or a fixed relationship or work outcome.

### Static brief S1: Counting sheep or 8 minutes

For: designers. Decision: D1.

- Angle: save_time: an easy, fixed routine instead of an open-ended struggle
- Hook (headline, verbatim): Counting sheep, or an 8-minute wind-down?
- Layout: Two panels side by side at equal width. Left: hand-drawn sheep in grey line art on a dark background. Right: the app's wind-down screen with the 8:00 timer, in the brand's warm amber. Headline across the top of both panels. Price line under the right panel. Button bottom right.
- Visual: Split image: grey sketch of sheep on the left, a phone screen with an 8:00 timer and a dim amber glow on the right.
- Copy blocks: headline "Counting sheep, or an 8-minute wind-down?"; primary text "Same bed, same night. One way is lying there counting. The other is 8 minutes of lights down, slow breathing and a short story, guided step by step. Try it free for 7 days."; CTA button "Start free trial"
- Offer and its placement: 7 days free, then the annual price in full, in a footer line under the right panel (no static in the market states its price)
- Sizes: 1:1 1080x1080, 4:5 1080x1350, 9:16 1080x1920 with the headline inside the safe zone

Variants (one variable each):

- v1: left panel 'Counting sheep'
- v2: left panel 'Scrolling till 1am', with a bright phone feed in grey line art; everything else unchanged

References by ad id (patterns, not copies):

- s01: take the dark night palette and a large readable headline; do not take the outcome promise and the sticker
- s09: take the plain footer price line; do not take the photo style

Avoid:

- any minutes-to-sleep promise
- sleeping pill or medication imagery
- a mocking tone toward people who cannot sleep

Claim and policy notes:

- 8 minutes is the routine length, a product fact; it is not a promise about falling asleep
- No 'insomnia' wording (brand rule on conditions)

Acceptance checklist:

- [ ] Headline readable at phone size in under 2 seconds
- [ ] Both panels the same width
- [ ] Annual price shown in full
- [ ] No claim about sleep results
- [ ] All three sizes delivered with names from the test plan

### Static brief S2: Price per night, stated openly

For: designers. Decision: D1.

- Angle: save_money: the cost of the routine set against something the viewer already buys
- Hook (headline, verbatim): Less per week than one late-night snack
- Layout: Text card. Headline top, the price per week in large figures in the centre, the full annual price and trial line under it, a small app screen bottom left, button bottom right.
- Visual: Warm dark background, large price figure, a small phone screen with the wind-down timer.
- Copy blocks: headline "Less per week than one late-night snack"; primary text "An 8-minute wind-down every night. [weekly price] a week on the annual plan, [annual price] billed once a year after a 7-day free trial."; CTA button "Start free trial"
- Offer and its placement: 7-day free trial, then the annual price in full; weekly figure computed by the team from the real annual price
- Sizes: 1:1 1080x1080, 4:5 1080x1350

Variants (one variable each):

- v1: comparison with a late-night snack
- v2: comparison with one coffee a week; same layout

References by ad id (patterns, not copies):

- s07: take a clear offer badge that is easy to read; do not take the countdown deadline

Avoid:

- fake urgency or countdowns
- a price that hides the annual billing

Claim and policy notes:

- Ship only if the weekly figure is true for the real annual price
- Comparison item must be a plausible everyday purchase, no named brands

Acceptance checklist:

- [ ] Weekly and annual figures checked by a person against the live price
- [ ] Billing period stated next to the price
- [ ] No deadline wording

### Static brief S3: Awake after 11pm, 8 minutes tonight

For: designers. Decision: D2.

- Angle: save_time: a specific audience and a promise the routine can keep
- Hook (headline, verbatim): Still awake after 11? Here is an 8-minute wind-down for tonight.
- Layout: Headline top third, a phone-style photo of a bedside table with the phone showing the timer, footer price line, button bottom.
- Visual: Phone-style photo of a bedside table at night, lamp off, phone screen showing the 8:00 timer in amber.
- Copy blocks: headline "Still awake after 11? Here is an 8-minute wind-down for tonight."; primary text "Lights down, slow breathing, a short story. Guided step by step, the same 8 minutes every night. 7 days free."; CTA button "Start tonight"
- Offer and its placement: 7 days free, then the annual price in a footer line
- Sizes: 1:1 1080x1080, 4:5 1080x1350, 9:16 1080x1920

Variants (one variable each):

- v1: 'after 11'
- v2: 'after midnight'

References by ad id (patterns, not copies):

- s06: take the product on screen as the hero; do not take the sleep score framing
- s09: take the phone-style photo at night; do not take the 'fall asleep faster' promise

Avoid:

- 'fall asleep in' promises
- a person in bed looking distressed

Claim and policy notes:

- The promise is the routine's length, which the product delivers

Acceptance checklist:

- [ ] Audience, promise and timeframe all in the headline
- [ ] Timer visible on the phone screen
- [ ] Footer price line present

### Motion brief M1: One tap and the room goes dark

For: motion design or video team. Decision: D4.

- Format: screen-led motion: phone screen footage composited with a real bedroom, no presenter
- Aspect ratios: 9:16, 4:5; durations: 15, 24 s
- Voice-over or captions: No voice-over in seconds 0 to 3. Calm voice-over from second 3. Captions burned in for every spoken line, white on a soft dark band inside the 9:16 safe zone.
- Pacing and sound: Market median is 1.58 cuts per 10 s and 5 s per shot; keep the opening a single continuous shot so the action carries the hook, then cut every 3 to 4 s. Sound: a soft tap at 0.5 s, room tone drops when the light goes off, quiet piano from second 3.

Hook, seconds 0 to 3, three variants (only these seconds change between them):

| Variant | Spoken | On screen | Visual | Sound |
|---|---|---|---|---|
| A |  | 1:12 am | Bright phone screen in a dark room, a thumb taps Start wind-down, the screen fades to amber and the bedside lamp clicks off with it | tap, then the room tone drops |
| B |  | One tap | Close-up of the app's 8:00 timer starting, the reflection of the screen in a window goes from white to amber | tap, low chime |
| C |  | Bedtime in 8:00 | Phone placed face up on a bedside table, the app's moon icon slides down and the screen dims as the camera pulls back to show the dark room | soft whoosh |

Beat sheet:

| Time (s) | Visual | Spoken | On screen | Motion | Sound |
|---|---|---|---|---|---|
| 0-3 | hook variant |  | hook variant text | one continuous shot, no cut | hook variant sound |
| 3-8 | Step one on screen: lights down, the room dims | Eight minutes. Lights down first. | 1. Lights down | text slides up from the bottom, 300 ms ease-out | piano starts |
| 8-13 | Breathing circle grows and shrinks | Then breathe with the circle. | 2. Breathe | circle scales with a 4 s cycle | piano |
| 13-19 | Story screen, the phone goes face down | Then a short story. Phone face down. | 3. A short story | cut on the phone turning | voice softens |
| 19-24 | End card | Try it free for seven days. | 7 days free, then [annual price]/year | logo fades in | piano resolves |

- End card: Brand Z logo, '7 days free, then [annual price] a year', button 'Start free trial'

Variants for testing:

- Hooks A, B and C on the same body
- 15 s cut: beats 1, 2 and 5 only

References by ad id (patterns, not copies):

- v06: take screen footage as the main picture; do not take the voice-over hook and the sleep score
- v12: take the three-step routine shown on screen; do not take the spoken opening

Avoid:

- a presenter in the first 3 seconds
- minutes-to-sleep claims
- a stock bedroom that looks like a hotel

Claim and policy notes:

- 8 minutes is the routine length, stated as such
- No condition words (insomnia, disorder)

Acceptance checklist:

- [ ] Product visible from the first frame
- [ ] No speech before second 3
- [ ] Captions inside the safe zone
- [ ] Three hook files share one body
- [ ] Annual price on the end card

### Motion brief M2: The 8 minutes in real time, sped up

For: motion design or video team. Decision: D4.

- Format: kinetic type over a locked-off timelapse of a bedside table
- Aspect ratios: 9:16; durations: 15 s
- Voice-over or captions: No voice. On-screen text carries the message, at most 6 words per screen.
- Pacing and sound: One locked-off shot sped up, type changes every 2 to 3 s. Sound: a quiet clock tick that slows down as the timer runs.

Hook, seconds 0 to 3, three variants (only these seconds change between them):

| Variant | Spoken | On screen | Visual | Sound |
|---|---|---|---|---|
| A |  | Watch 8 minutes in 8 seconds | Timelapse starts at once: lamp on, phone timer at 8:00 counting fast | fast tick |
| B |  | This is the whole routine | Same timelapse, timer visible top right | fast tick |
| C |  | 8:00 | Extreme close-up of the timer, then the camera holds as the room darkens | one tick per second, slowing |

Beat sheet:

| Time (s) | Visual | Spoken | On screen | Motion | Sound |
|---|---|---|---|---|---|
| 0-3 | hook variant |  | hook variant text | type pops in with a short spring | hook variant sound |
| 3-7 | Lamp goes off in the timelapse |  | Lights down | word fades in 200 ms | tick slows |
| 7-11 | Phone screen shows the breathing circle, then the story |  | Breathe. Listen. | two words, one at a time | tick slows more |
| 11-15 | End card over the dark room |  | 7 days free | logo and button rise 8 px | silence |

- End card: Brand Z logo, '7 days free, then [annual price] a year', button 'Start free trial'

Variants for testing:

- Hooks A, B and C on the same timelapse

References by ad id (patterns, not copies):

- v02: take text-only storytelling with sound; do not take the '9 out of 10' claim

Avoid:

- user numbers or ratings the team cannot prove
- more than 6 words on any screen

Claim and policy notes:

- No result claims; the video shows the routine only

Acceptance checklist:

- [ ] Timer visible in every beat
- [ ] No voice
- [ ] Max 6 words per screen
- [ ] 15 s exactly

### Motion brief M3: Creator does the routine with the viewer

For: motion design or video team. Decision: D5.

- Format: UGC talking head, phone look, the app visible in the creator's hand from frame 1
- Aspect ratios: 9:16; durations: 20, 30 s
- Voice-over or captions: Creator speaks; captions burned in, the spoken words verbatim.
- Pacing and sound: Near the market median of 1.58 cuts per 10 s: jump cuts only between steps. Room sound, no music under speech.

Hook, seconds 0 to 3, three variants (only these seconds change between them):

| Variant | Spoken | On screen | Visual | Sound |
|---|---|---|---|---|
| A | Still awake after 11? Do the 8-minute version with me. | 8-minute wind-down | Creator in a dim bedroom holds the phone to camera, timer at 8:00 | room tone |
| B | This is my whole bedtime, it takes 8 minutes. | My 8-minute bedtime | Creator taps Start, the screen dims in their hand | tap |
| C | I stopped counting sheep. I do this instead. | Instead of counting sheep | Creator turns the phone to camera showing the timer starting | tap |

Beat sheet:

| Time (s) | Visual | Spoken | On screen | Motion | Sound |
|---|---|---|---|---|---|
| 0-3 | hook variant, phone in frame | hook variant line | hook variant text | none | room tone |
| 3-9 | Creator switches off the lamp, screen glow on the face | Lights down first. The app walks you through it. | 1. Lights down | jump cut | lamp click |
| 9-15 | Creator breathes with the circle on screen | Breathe with the circle for two minutes. | 2. Breathe | jump cut | room tone |
| 15-20 | Creator lies down, puts the phone face down | Then a short story. That is it. Seven days free if you want to try. | 3. A short story | end card overlay at 18 s | voice from the phone, quiet |

- End card: Overlay: '7 days free, then [annual price] a year', button 'Start free trial'

Variants for testing:

- Hooks A, B and C on the same body
- 30 s cut with one more line about the story library

References by ad id (patterns, not copies):

- v01: take the dark bedroom and phone-lit face; do not take 'I wake up actually rested' and the minutes claim
- v11: take a plain everyday creator; do not take the three-coffees result line

Avoid:

- any result the creator 'got' (hours slept, cured, rested)
- an expert costume or title
- music under speech

Claim and policy notes:

- Creator describes what they do, never what it did to their sleep
- Disclose the paid partnership as the platform requires

Acceptance checklist:

- [ ] App visible in the first frame
- [ ] Hook line spoken in under 3 s
- [ ] No result claims in the script
- [ ] Captions verbatim
- [ ] Three hook files share one body

### Hand-off: test plan for meta-creative-testing

Ad names in the format `PROJECT | TEST | Format | Concept | src`:

- `BRANDZ | MKT01 | Static | S1 v1 | src: market s01+s09`
- `BRANDZ | MKT01 | Static | S1 v2 | src: market s01+s09`
- `BRANDZ | MKT01 | Static | S2 v1 | src: market s07`
- `BRANDZ | MKT01 | Static | S2 v2 | src: market s07`
- `BRANDZ | MKT01 | Static | S3 v1 | src: market s06+s09`
- `BRANDZ | MKT01 | Static | S3 v2 | src: market s06+s09`
- `BRANDZ | MKT01 | Video | M1 hook A | src: market v06+v12`
- `BRANDZ | MKT01 | Video | M1 hook B | src: market v06+v12`
- `BRANDZ | MKT01 | Video | M1 hook C | src: market v06+v12`
- `BRANDZ | MKT01 | Video | M2 hook A | src: market v02`
- `BRANDZ | MKT01 | Video | M2 hook B | src: market v02`
- `BRANDZ | MKT01 | Video | M2 hook C | src: market v02`
- `BRANDZ | MKT01 | Video | M3 hook A | src: market v01+v11`
- `BRANDZ | MKT01 | Video | M3 hook B | src: market v01+v11`
- `BRANDZ | MKT01 | Video | M3 hook C | src: market v01+v11`

Run it with meta-creative-testing: one broad ad set by default, its kill, winner and fatigue criteria, a control that stays live, judged on the primary metric only after the spend gate. Optional before production: creative-preflight-panel on the concepts file. Optional before launch: the copy lines through jev-marketing-gates. Nothing in this pack is published or launched by the skill.

