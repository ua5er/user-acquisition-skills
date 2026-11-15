# Reading the matrix and the verdicts

`panel_matrix.py` writes `matrix.md` (for a person), `matrix-<track>.csv` (the heatmap) and `verdicts.json` (for `brief_pack.py --panel-verdicts` and for `panel_vs_results.py`).

## The heatmap

Rows are panel items (a static concept, or one hook of a video concept such as M1-A). Columns are profiles. A cell is the probability mass Jev put on stop or click for that pair, from 0 to 1. A `?` marks a pair in the review band (over 0.35 and under 0.70): the panel cannot tell whether that person stops or scrolls.

Read it by column as well as by row. A column that is high everywhere is a profile that likes everything (a weak profile or the control failing). A column that is low everywhere is a profile no concept reaches: a gap in the concepts, or someone outside the target.

## The ranking

Items are sorted by stop-or-click mass, then click mass. Guards:

- Under 12 profiles (`--min-profiles`) nothing is ranked.
- No leader is named when the top item leads the next by less than 0.10 (`TIE_MARGIN`): the note lists the items inside that margin.

## Verdicts

Starting values in `panel_matrix.py`, not tested on your market:

| Verdict | Rule |
|---|---|
| drop | stop-or-click mass under 0.30, or mean fit under 1.0 of 3 |
| go | mass at least 0.50, fit at least 2.0, at most 25% of profiles would distrust a claim, at most half of the pairs in the review band |
| rework | everything else, with the blocking reasons listed |
| rework (video) | a hook that trails the best hook of its own concept by 0.10 or more: replace that opening |
| no verdict | fewer than half of the profiles answered (errors) |

Notes that do not block a go: the hook is about the buyer's problem for under half of the profiles, the offer is clear at first sight for under half, the profiles an item loses (mass under 0.35 or fit under 1.0).

A concept takes the verdict of its best item. For video, the concept's best hook is named, and weaker hooks are listed as rework.

## What to do with each verdict

- go: into production as briefed. The live test decides.
- rework: fix the named reason (a sharper hook, a clearer offer line, a claim a skeptic would doubt), then produce. Re-run the panel on the fix only if it is cheap and the change is large.
- drop: held out of the test plan. A person may override, and should when the concept tests something the panel cannot judge (a visual idea, a sound, a creator's delivery).

## What the panel cannot tell you

A panel score is a cheap filter and a signal, not proof of performance. Jev reads text written about the ad, not the ad; it cannot see a picture, hear a voice or feel pacing. Simulated buyers are not buyers. The panel never replaces a live test and never touches budgets. Use it to cut clearly weak ideas early and to find which profiles a concept misses.

## Calibrating the panel

After the test, export per-item results from the ad platform (impressions, clicks, conversions, spend; real numbers only) and run:

```
python3 scripts/panel_vs_results.py --verdicts verdicts.json --results results.csv --metric ctr --out panel-vs-results.md
```

It reports the Spearman rank correlation and pairwise agreement between the panel's order and the real order, per track, and the misses (a go in the real bottom third, a rework in the real top third). Starting advice cutoffs in the script: under 5 items with results, no conclusion; rho at least 0.5 on at least 8 items, keep the panel as a pre-filter; 0.2 to 0.5, a tie-breaker only; under 0.2, do not cut concepts on it. Dropped items are usually never tested, so the panel's drops cannot be checked unless some ran anyway: run one dropped item on purpose now and then.
