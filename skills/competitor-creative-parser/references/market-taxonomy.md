# Claude drafts the market taxonomy

The stock question sets in `scripts/questions_static.py` and `scripts/questions_video.py` were written for a fictional sleep-app market and for captures that have a transcript. A real market runs its own things, and a real capture has its own fields. This step sits between Describe and Tag: Claude reads the descriptions, writes the options this market really uses, and the tagger runs on that file.

Worked example: `scripts/markets/ai_photo_editor/` (see its `ABOUT.md`).

## Method

1. Describe first. Do not draft options before there are descriptions. Read the first 30 or so (static and video apart) and list what this market really runs: what the product does with the user's input, how the image or the first seconds are laid out, what the headline says, what is offered, how the result is proven.
2. Pick the dimensions that matter for a decision. Four to six Choice dimensions per track is enough. Keep a stock dimension only when it describes this market.
3. Write 5 to 10 options per dimension. They must be:
   - mutually exclusive: an ad fits one option, not two;
   - stated positively, as what the ad does ("Promises how the photo will look"), never as what it does not do;
   - one idea per option, with no "and" or "or" joining two claims;
   - ended by `other`.
4. Put "nothing stated" cases into `other`. Do not add a `none` option: "no offer is stated, or a different kind of offer" belongs in `other`. A `none` option sits next to the real options and splits the model's confidence. A high share of `other` is itself a finding.
5. Avoid negations and compound statements, in options and in yes/no questions. The vendor lists negations as a weak spot, and the real run confirmed it.
6. Read only fields the capture really has. An ad library capture shows the picture, the on-screen text, the ad text, the link headline and the button. It has no audio: no transcript, no spoken hook, no voice-over question. The video state is built from `first_3s`, `on_screen_text`, `format_notes` and the ad text. Check `build_state` in the question file against the description template before any run.
7. Write the companion yes/no for every Choice, as before. With `--confirm-pass` the tagger also asks, for the option the model picked, a specific yes/no in that option's own words. That answer replaces the generic companion as the second vote. The generic companion stays in the file for runs without the flag.
8. Add a yes/no flag only for a fact a model reading text can answer (price shown, the word free, social proof, urgency). Anything code can count (words, cuts, duration) stays in `code_features`.
9. Set `TAXONOMY_VERSION` (for example `market-static-1.0`). It is written into every tag record. Tags from two versions never go in one snapshot.

## Pilot before the full run

1. `--dry-run` on the whole set: shape and wiring only, the numbers are meaningless.
2. A live pilot of about 30 ads with `--confirm-pass` and `--order-check 6`.
3. Look at the unresolved count per dimension and at the review queue. If most of a dimension is unresolved, suspect the options before the model: merge options that overlap, split an option that holds two ideas, rewrite a question that has a negation, add the option that the review rows keep pointing at.
4. Bump the version, re-run the pilot, and only then run the full capture.
5. When the sample grows, re-read a fresh batch of descriptions, check how much of each dimension falls into `other`, add options if one pattern keeps landing there, bump the version and re-tag everything.

## One real run (not a benchmark)

Market: AI photo editor apps, public Meta Ad Library, US, 2026-11-15. The first pilot used the stock sets on the first 31 ads (9 static, 22 video). It put 143 rows in the review queue, and on the 22 videos between 12 and 22 were unresolved in each Choice dimension. Three changes followed: a market taxonomy written by Claude from the descriptions, questions that read only the fields the capture has, and the confirm pass.

| | Stock sets, first 31 ads | Market taxonomy and confirm pass |
|---|---|---|
| Review rows | 143 (31 static, 112 video) | 107 on all 54 ads (32 static, 75 video) |
| Videos unresolved per dimension | 12 to 22 of 22 | 0 to 9 of 22 in the last pilot iteration; 0 to 16 of 34 in the full run |
| Choice tags resolved without a person | not recorded | 222 of 304 (73%) |

Full run: 124 tagging requests, 1,371 typed answers, 204,504 input tokens, 0.0086 US dollars, option order check 85 of 88 the same. Four pilot iterations before it cost 0.0128 US dollars in total. This is one market, one day and one model version. The three changes were made together, so this does not say which one mattered most. It says nothing about another market and nothing about accuracy: the tags are model output and no labelled sample was used.
