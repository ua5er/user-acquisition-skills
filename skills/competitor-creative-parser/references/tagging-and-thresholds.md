# Tagging with Jev: questions, decisions, calibration

## Why the questions look the way they do

Each rule answers a weak spot the vendor lists for Jev (literal reading, counting, numbers, dates, irrelevant detail, injected text, first-option bias).

- One judgment per question, stated as a positive fact. No "or not", no double negatives.
- Facts code can compute (word count, price shown, duration, cuts, captions, runtime) are computed, never asked.
- Every Choice ends with `other`, and every Choice has a companion yes/no that asks whether a listed option fits. A Choice always picks something, so the companion catches the case where nothing fits. With `--confirm-pass` a second request asks a narrower yes/no about the option the model picked, and that answer takes the companion's place (see the two-vote rule below). For options that are written for one market, see `market-taxonomy.md`.
- Option order is rotated per creative (deterministic from the creative id and question id, `other` always last), so no single option sits first for every ad. The order sent is logged in `option_order`.
- `--order-check N` asks the Choice questions again with the options reversed for the first N creatives and reports agreement per question. Low agreement means the answer moves with the order: rewrite the options or widen review for that question.
- All questions of one creative go in one request against the same state. They cannot see each other.
- The state holds only the description fields a person would look at. No advertiser, no id, no capture metadata.

## Question sets

| | Static (`questions_static.py`) | Video (`questions_video.py`) |
|---|---|---|
| Choice with companion | hook type, angle, offer type, visual format, offer placement | hook type, hook channel, angle, video format, structure, creator type, offer type |
| Yes/no flags | social proof, urgency, risky claim, personal attribute | product in first 3 s, CTA at the end, social proof, urgency, risky claim, personal attribute |
| Score | hook specificity, CTA clarity, legibility | hook specificity |
| Code facts | words on image, text blocks, price shown, aspect ratios, CTA label | duration, cuts, cuts per 10 s, average shot, captions |

Questions in total: 17 static, 21 video. Edit the modules to change wording; the runner validates the contract (Choice ends with `other`, every Choice has a companion, flag and score types match).

## How code turns probabilities into tags

Starting thresholds: `tag` 0.70, `review_low` 0.35 (vendor guardrails cookbook and confidence page values, not tested on your market). They live in each question module as `THRESHOLDS`.

Choice, with top option probability p and a second vote c. Without the flag c is the generic companion yes probability. With `--confirm-pass` c is the yes probability of the confirmation question about the chosen option, written in that option's own words, and the generic companion is not used. A tag needs two yes votes at 0.70 or more: the Choice and c.

| Condition | Result |
|---|---|
| p below 0.35 | untagged, low priority row in the review queue |
| top is `other`, p at least 0.70 | tagged `other` (no confirmation is asked) |
| top is `other`, p below 0.70 | review |
| c at or below 0.35 while a listed option was picked | review (conflict) |
| p at least 0.70 and c at least 0.70 | tagged with the top option |
| anything else | review |

The confirm pass is a second request per creative, so requests double and input tokens rise by less than that, because the confirmation asks only about the Choices that picked a listed option (in two real pilots on the same 31 ads, 72,563 input tokens without the pass and 97,239 with it). Every tag record keeps `companion_p` and `confirm_p` (empty when the pass is off or was skipped for that Choice), and the review queue has a `confirm_probability` column. If the confirm request fails for a creative, the generic companion decides for that creative and the failure is logged. The run summary records `confirm_pass` and `decisions`, the number of typed answers received.

Yes/no flag with probability p: yes at 0.70 or more, no at 0.35 or less, review in between. `risky_claim` rows in review are high priority.

Score: the probability-weighted score and its confidence are stored; the level is the rounded score. Scores are reported as averages and level counts and never queued.

Errors (HTTP errors after retries, a response that does not match the documented shape) mark the whole creative as `error`. An error is never a tag and never a "no".

## Review queue

`review-queue-<track>.csv` columns: creative id, track, question id, kind (choice, flag, error), reason, model answer, probability, runner up and its probability, companion probability, confirm probability, priority, and an empty `human_label`. A person fills `human_label`. Those labels are your calibration set.

## Calibration before you trust the shares

The live check on the fictional sample proves the pipeline and the response shape, not accuracy. Before shares from a real market go into decisions:

1. Label about 100 of your own captured ads by hand for every Choice and flag (two people on a shared sample of 20 shows how much people disagree).
2. Tag them with the current module and compare: per question, precision of tagged items, share sent to review, and how often the companion and the Choice disagree.
3. Move `tag` up for questions with wrong tags, down for questions where review is full of items people label the same as the model. Rewrite or split any question that no threshold makes reliable.
4. Run `--order-check` on 20 items after any wording change.
5. Pin the model id. Re-tag the whole dataset after a model or wording change; do not mix tags from two versions in one snapshot.

The calibration script in `jev-marketing-gates` (`calibrate.py`) reads a log and a labels file; export the tags you want to check into its log format, or compare in a spreadsheet.

## Cost

Tokens are counted from the API's `usage.input_tokens`; price is input tokens times the listed price ($0.042 per million on 2026-11-15, output free). The live check on 2026-11-15 used about 1,900 input tokens per static creative and about 2,100 per video (all questions in one request). The spend guard (`--max-usd`, default 0.50) stops before the estimated spend of the next request would pass the cap. The vendor console has the real bill.
