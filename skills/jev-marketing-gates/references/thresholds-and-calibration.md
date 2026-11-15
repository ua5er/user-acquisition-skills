# Thresholds and calibration

## What the vendor says

Sources: https://docs.typesafe.ai/confidence.md and https://docs.typesafe.ai/cookbooks/llm_guardrails.md (read 2026-11-15).

- Act when confidence is high, verify when medium, do not act when low. Scale to risk: read-only actions can use lower thresholds, destructive ones need more.
- Noul: start near 0.7 for yes and 0.3 for no and handle the band between as its own outcome.
- Choice: threshold on the probability of the option you act on. A 0.9 threshold means acting only when the chance of a wrong option is under 10 percent.
- Score: look at confidence first, then route on the level.
- Guardrails cookbook starting values: strict review 0.35, action 0.70, severity block 2.0; permissive review 0.70, action 0.85, severity block 2.0. Run on 16 items, called a demonstration.
- The numbers depend on your domain and must be tested on your data. The vendor's concepts page says calibration is measured across groups of predictions and is not a guarantee for any single answer. Independent tests found overconfidence in some settings; none is reproduced here.

## Defaults used in the job templates

| Job | Default | Source |
|---|---|---|
| Any Noul | yes at 0.70 or more, no at 0.30 or less, band is review | confidence page |
| Policy and brand-safety pre-check | review at 0.35, action at 0.70, severity block at 2.0 (strict) | guardrails cookbook |
| Choice routing | act on the chosen option only when its probability is at least 0.90 and the companion Noul is at 0.70 or more | confidence page (0.9 example) |
| Clarity or quality Score | level floor is your own example value | none; label it example and tune |

These are starting points, not tested values.

## Review band

Every Noul has three outcomes: yes, no, review. The review band is the work you give a person. Pick the band from the share of items a person can review per day, then see what precision you get at its edges. If the band is too wide for the team, fix the question or the state, not only the numbers.

## Collect labelled examples

- 20 to 200 items from the real job. Fewer than 50 only shows direction.
- One label per question per item, from a person who knows the rules. Write the labelling rule down once and use it for every item.
- Include hard and borderline items, not only clean ones. Include some that look like prompt injection if the job reads outside text.
- Remove personal data before sending anything, and only send what the data owner approved.
- labels.csv columns: `item_id`, `question_id`, `label` (noul: yes or no; choice: option name; score: level number from 0).

## Run, then read the report

1. `python3 scripts/run_batch.py items.csv --questions my_questions.py --smoke --data-handling-confirmed` first.
2. Full batch with a spend guard: add `--max-usd`.
3. `python3 scripts/calibrate.py --log log.csv --labels labels.csv --questions my_questions.py --out report.md`.

The report has, per question:

- A probability bucket table: items in each bucket, share labelled yes (noul) or accuracy (choice, score by confidence).
- Confusion counts.
- For Choice, the first-option check.
- At the thresholds in force: how many were called yes, how many called no, how many fell in the band, and precision on each side.
- A suggestion: the loosest threshold that meets the precision target you set (default 0.9, change it with `--target-precision`) with at least 5 items on that side. If none does, the report says so. That means rewrite the question, split it, or label more items.
- Routing counts and the share sent to review, recomputed from your `route()` on the logged answers.
- Cost from the logged input tokens.

## How to use the suggestions

- A suggestion from under 50 labels is a hint. Run again with more.
- A precision target is a business decision. A false pass on a claim check costs more than a false review. Set the target per question.
- Compare against a baseline on the same labels: a plain rule set, and optionally a text model. If a regular expression gets the same precision, use the regular expression.
- Fill `human_outcome` in the log as people decide. The report shows how often the routed outcome matched the person.
- Calibration drifts. Re-run on a schedule (monthly is a reasonable example) and after any change to the model id, the wording, the rules text or the source of the items.

## Failure handling

- An API error is an error, not a "no". The scripts write the row as ERROR with outcome error and never route it to pass.
- A spend guard stop leaves later items unprocessed and says so.
