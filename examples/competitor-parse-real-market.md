# Example: the Claude + Jev system on a real market (AI photo editor apps, US)

**The ads are real, the advertisers are anonymised, the team is an example.** 54 ads from 23 advertisers were captured from the public Meta Ad Library on 2026-11-15. Claude described them, Jev (`jev-1.14.0`, TypeSafe AI's direct endpoint) tagged the descriptions live, code counted. Advertisers appear here only as letters, with no page names, no ad ids and no competitor copy; patterns are described in our own words. "Brand Z", its rules, its offer and its budget are an example written for this walk-through, and so are the 12 buyer profiles.

**An ad library shows what runs, never spend or results.** Nothing below says which ad works. It says what the category runs, where nobody is, and which of our own concepts a simulated panel liked.

This is the sequel to the [fictional-market walk-through](competitor-parse-fictional-market.md). The same three skills ran on real input: `competitor-creative-parser`, `market-to-creative-brief`, `creative-preflight-panel`.

## What went in

| Input | Value |
|---|---|
| Source | Meta Ad Library, public pages, category AI photo editor apps, US |
| Date | 2026-11-15 |
| Sample | 54 distinct creatives: 20 static, 34 video, 23 advertisers |
| What they stand for | About 360 ad copies once near-duplicate variants of the same creative are counted (308 variants seen next to the 54 creatives) |
| Advertisers by creatives in the sample | 7, 6, 4, 4, 4, 4, 3, 3, 3, 2, 2, then twelve advertisers with 1 each (letters A to W, assigned here by this order, not by any order in the source) |

Limits, stated plainly:

- Library results come back newest first, so the sample leans to recent ads. The median runtime in the sample is 5 days for static and 2 days for video. No long-running ads were sampled, so durability says nothing here.
- Pages in this category run one template many times. Distinct creatives per advertiser were few, which is why the sample is 54 and not more.
- An ad library capture has no audio. Nothing in the video track was heard: no transcript, no spoken hook. Videos were described from frames at about 0, 1.5 and 3 seconds, so end cards and durations are mostly missing.
- Images and videos never go to Jev. Only the text descriptions Claude wrote do.

## The taxonomy lesson

The stock question sets were written for a fictional sleep-app market, and the video set reads a transcript. On real ads they failed three ways: the capture has no audio, the generic options did not fit this market (the real ads are about what the app does with a selfie, not about hook types from a sleep app), and the generic companion yes/no pushed confident choices into review. Claude then drafted a market taxonomy from the descriptions (five to ten positive options per dimension, `other` last, questions that read only fields the capture has), and the tagger got a confirm pass: a specific yes/no about the chosen option replaces the generic companion as the second vote. See `skills/competitor-creative-parser/references/market-taxonomy.md`.

| | Stock sets, first 31 ads | Market taxonomy and confirm pass |
|---|---|---|
| Review rows | 143 (31 static, 112 video) | 107 on all 54 ads (32 static, 75 video) |
| Videos unresolved per dimension | 12 to 22 of 22 | 0 to 9 of 22 in the last pilot iteration; 0 to 16 of 34 in the full run |
| Choice tags resolved without a person | not recorded | 222 of 304 (73%) |
| Option order check (Choice asked again in reversed order) | not run | 85 of 88 the same |

This is one run, one market and one model version, not a benchmark. The three changes were made together, so it does not say which one mattered most.

## Snapshot highlights

All numbers come from `snapshot.json` of the full run. Shares are of the track's creatives; the unresolved items wait in the review queue.

### Static track (20 creatives, 7 advertisers)

- Professional headshots are the crowded space: 13 of 20 creatives and 4 of 7 advertisers. The other use cases are small: restoring old photos 3, art style portraits 3, a retouch tool 1. Nobody in the static sample sells a full photo shoot from selfies, a cinematic scene, a funny animation, a makeover or a try-on.
- Money talk: 11 of 20 say free, and 8 lead with a free preview ("see the results free, pay only to keep them"). 4 show a price. None uses urgency, and no static leads with a plain stated price or a free trial.
- 10 of 20 cite social proof such as user numbers, ratings or press. 10 show the original photo in the image.
- The headlines are not specific: the specificity score averages 1.16 on a 0 to 3 scale.
- 14 of 20 are 4:5, 5 are 1:1, 1 is 9:16. Median 18 words on the image.
- Unresolved after the confirm pass: use case 0, layout 5, headline type 7, angle 8, offer type 1 of 20.

### Video track (34 creatives, 18 advertisers)

- No crowded value at the current rules. Use cases are spread: cinematic scenes 4, funny animations 4, headshots 4, photo shoots 3, retouch tools 3, makeovers 2, restoration 2, try-on 1.
- 29 of 34 state no offer, or a kind that is not in the taxonomy; 1 shows a price; 5 offer something free to start. None cites social proof and none uses urgency.
- 12 are fully AI generated clips, 5 are screen recordings, 3 are talking heads, 2 are real footage.
- 25 of 34 put text on screen in the first 3 seconds.
- Proof of the result: 10 use a small inset of the source photo, 1 shows the original and the result at equal size, 13 are in `other`.
- Hooks: 7 are a plain transformation, 3 an instruction in a caption, 2 a first-person caption, 2 a question in a caption, 2 a result reveal, 1 a person talking, 1 a tool demo.
- Unresolved after the confirm pass: use case 11, hook type 16, proof device 10, angle 13, video format 11, offer type 0 of 34. The gaps in proof device, hook type and angle are therefore "possible gaps", not firm ones.

## Six decisions

Written by Claude for the example team. Brand Z (an AI portrait app that turns selfies into headshots and photo shoots) has a test budget of 1,500 US dollars and a target cost per acquisition of 30 US dollars; those are example values and not a recommendation. Its rules: every result shown is real app output from the selfie shown next to it, no promise of a job, income or a date, no famous faces, no luxury brand logos, the price written in full wherever it appears. The offer is a free preview and one payment to download the set. Team capacity: one designer, one motion designer, two paid creators a month. Code re-checked every number cited in the decisions against the snapshot.

| Id | Track | Move | Where | Why, from the snapshot |
|---|---|---|---|---|
| D1 | static | out-execute | headshots | 13 of 20 statics and 4 of 7 advertisers, generic headlines (1.16 of 3), only 4 of 20 show a price: name one buyer and put the price on the image |
| D2 | static | enter a gap | photo shoot | No static sells a full shoot, while 3 videos from 2 advertisers do; a gap, not proof that it works |
| D3 | static | enter a gap | stated price | 11 of 20 say free, 8 lead with a free preview, none leads with a plain price: price as the headline, free preview as the footer |
| D4 | video | enter a gap | free preview in the video | 29 of 34 state no offer and 1 shows a price, while 8 of 20 statics lead with a free preview: say it on screen in the first 3 seconds |
| D5 | video | enter a possible gap | equal-size before and after | 10 videos use a small source inset, 1 shows equal size; 10 videos in this dimension are unresolved |
| D6 | video | enter a possible gap | a person talks | 12 of 34 are AI generated clips and 1 opens with a person talking; 16 videos in this dimension are unresolved |

## Six concepts

Our own texts, quoted. `[price]` stands for the price, which the example team writes in full.

| Concept | From | Headline or hook | Idea |
|---|---|---|---|
| S1 | D1 | "The photo on your proposal. No photographer." | One large headshot in a document-style frame for freelancers and consultants, the source selfie small and labelled, a price line in the bottom band: "Preview free. [price] to download the set." |
| S2 | D2 | "A few selfies in. A full photo shoot out." | A 2x2 grid of four settings of the same person, the selfie as a small inset, the offer in the bottom band |
| S3 | D3 | "[price]. 40 headshots. Yours to keep." | A text-led card: the price fills the top half, one tall result on the right, "See them free before you pay." as the footer |
| M1 | D4 | Hooks A "See your headshots free. Pay only if you keep them.", B "Free to look. [price] to keep.", C "Would you pay before seeing the photos? Neither would we." | Screen-led recording of the app with large captions, 15 seconds, the offer read and not heard |
| M2 | D5 | Hooks A "Left: my selfie. Right: my headshot.", B "Same person. Same day. No studio.", C no text, a side-by-side that zooms to the eyes | Split-screen motion, selfie left and result right at equal width, 12 seconds |
| M3 | D6 | Hooks A "I needed a headshot by Friday and I was not booking a photographer.", B "This is the selfie I gave it.", C "Okay, I am opening the results for the first time on camera." | A paid creator talks to camera with a screen insert, 20 seconds |

## The panel

12 example buyer profiles written by Claude (7 from ICP notes and 5 from snapshot signals; p12 is a control with no need for portraits): p01 job seeker, p02 freelance consultant, p03 real estate agent, p04 team lead, p05 designer who has seen every AI headshot ad, p06 student, p07 privacy-minded professional, p08 person who shares fun AI clips, p09 refreshing a dating profile, p10 paid before and the results looked wrong, p11 coach building a personal brand, p12 control. Jev answered typed questions for every item and profile pair. A `?` marks a cell in the review band (0.35 to 0.70), where the panel cannot tell whether the person stops or scrolls. Cells are the probability of stopping or clicking.

Static, 3 items x 12 profiles:

| Item | p01 | p02 | p03 | p04 | p05 | p06 | p07 | p08 | p09 | p10 | p11 | p12 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S2 | 0.96 | 0.88 | 0.71 | 0.81 | 0.58? | 0.90 | 0.64? | 0.88 | 0.98 | 0.99 | 0.99 | 0.11 | 0.79 |
| S3 | 0.90 | 0.94 | 0.87 | 0.67? | 0.70 | 0.91 | 0.75 | 0.37? | 0.65? | 0.99 | 0.88 | 0.10 | 0.73 |
| S1 | 0.96 | 0.97 | 0.70 | 0.60? | 0.80 | 0.82 | 0.85 | 0.20 | 0.42? | 0.99 | 0.66? | 0.01 | 0.67 |

Video, 9 items (3 concepts x 3 hooks) x 12 profiles:

| Item | p01 | p02 | p03 | p04 | p05 | p06 | p07 | p08 | p09 | p10 | p11 | p12 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1-C | 0.90 | 0.88 | 0.77 | 0.76 | 0.88 | 0.95 | 0.72 | 0.84 | 0.89 | 0.98 | 0.89 | 0.22 | 0.81 |
| M2-B | 0.94 | 0.77 | 0.73 | 0.94 | 0.92 | 0.84 | 0.57? | 0.92 | 0.88 | 0.95 | 0.92 | 0.08 | 0.79 |
| M1-A | 0.80 | 0.85 | 0.80 | 0.76 | 0.73 | 0.97 | 0.56? | 0.77 | 0.78 | 0.99 | 0.97 | 0.07 | 0.75 |
| M1-B | 0.78 | 0.89 | 0.71 | 0.83 | 0.46? | 0.87 | 0.60? | 0.47? | 0.84 | 0.99 | 0.95 | 0.08 | 0.71 |
| M2-C | 0.92 | 0.68? | 0.59? | 0.91 | 0.95 | 0.55? | 0.25 | 0.71 | 0.78 | 0.93 | 0.88 | 0.04 | 0.68 |
| M2-A | 0.86 | 0.73 | 0.60? | 0.94 | 0.92 | 0.78 | 0.30 | 0.60? | 0.57? | 0.95 | 0.84 | 0.05 | 0.68 |
| M3-A | 0.85 | 0.93 | 0.75 | 0.72 | 0.40? | 0.84 | 0.75 | 0.18 | 0.74 | 0.78 | 0.65? | 0.01 | 0.63 |
| M3-B | 0.81 | 0.72 | 0.52? | 0.54? | 0.83 | 0.79 | 0.52? | 0.52? | 0.63? | 0.88 | 0.57? | 0.10 | 0.62 |
| M3-C | 0.75 | 0.47? | 0.46? | 0.33 | 0.68? | 0.74 | 0.47? | 0.48? | 0.72 | 0.96 | 0.54? | 0.08 | 0.56 |

The control profile (p12) scored 0.01 to 0.22 on every item, so on this run the panel separates people who would buy portraits from people who would not. That is a sanity check on the panel, not a measure of how good the ads are.

Verdicts (a go needs a fit of at least 2.0 of 3; the reasons are the notes code attaches to each item):

| Concept | Verdict | Best item | Main reasons |
|---|---|---|---|
| S1 | rework | S1 | fit 1.92 of 3, under the 2.0 needed; a third of profiles would distrust a claim; offer not clear at first sight for any profile; loses p08 and p12 |
| S2 | rework | S2 | a third of profiles would distrust a claim; offer not clear at first sight for any profile |
| S3 | go | S3 | fit 2.16 of 3; the hook speaks to the person's problem for only 2 of 12 profiles and the offer is clear for 1 of 12; loses p12 |
| M1 | go | hook C | hooks A and B rework: half of the profiles or a third would distrust a claim |
| M2 | go | hook B | hooks A and C rework; hook C trails hook B by 0.11 |
| M3 | rework | M3-A | 42 to 50% of profiles would distrust a claim in every hook |

Go: S3, M1 with hook C, M2 with hook B. Rework: S1, S2, M3. The ranking among the leaders is close: in static S2 and S3 are within 0.10, in video M1-C, M2-B and M1-A are within 0.10. A person decides, and survivors go to a live test (`meta-creative-testing`).

## The honest ledger

Jev input tokens come from the API's usage field, at the listed $0.042 per million (output free). Claude's own work (descriptions, taxonomy, decisions, briefs, profiles) ran in the chat session and is not in these numbers.

| Run | Requests | Typed answers | Input tokens | US dollars |
|---|---|---|---|---|
| Tagging, static (20 creatives, confirm pass) | 48 | 470 | 78,288 | 0.0033 |
| Tagging, video (34 creatives, confirm pass) | 76 | 901 | 126,216 | 0.0053 |
| Panel, static (36 pairs) | 48 | | 35,728 | 0.0015 |
| Panel, video (108 pairs) | 120 | | 106,294 | 0.0045 |
| **Final run, total** | **292** | **2,091** | **346,526** | **0.0146** |
| Four pilot iterations before it | | | 304,359 | 0.0128 |

Errors in the final run: 0. The review queue holds 107 rows from tagging. The pilots cost almost as much as the final run, and that is where the taxonomy was fixed: budget for two or three pilot rounds, not one pass.

## What this does not prove

- The tags are model output with a review queue. 73% of choice tags were accepted by code without a person; that is not an accuracy. Nobody has labelled a sample of these ads, so no precision is known.
- The thresholds (tag at 0.70, review from 0.35) are the vendor's starting values and were not calibrated on labelled ads.
- The sample is 54 creatives, newest first, from one day, with no audio. A gap is a place where this sample shows nobody, not a place where something works.
- A panel score is a cheap filter and a signal. The profiles are example profiles written by Claude. The live test decides; the panel never touches a budget.
- The budget, target cost per acquisition and team are an example. Nothing here is a benchmark for the category.
