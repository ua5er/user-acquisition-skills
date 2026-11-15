---
name: creative-preflight-panel
description: Claude + Jev pre-flight panel for ad concepts. Before designers or the motion team spend hours, every concept from the brief pack is shown to 12 to 30 simulated buyer profiles that Claude writes from the team's ICP notes and the market snapshot; Jev answers a small typed set per concept and profile (scroll, stop or click with probabilities, three yes/no checks, a fit score); code builds the concept x profile heatmap, ranks with small-sample and tie guards and gives go, rework or drop with reasons; a person decides. After launch, a calibration script checks the panel against real results. Static and video tracks. Use for "pre-test ad concepts", "screen creative concepts before production", "synthetic audience panel", "which hook should we produce", "concept testing with AI", "simulated buyer panel", "Jev panel".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Creative pre-flight panel (Claude + Jev)

Third step of the Claude + Jev creative system: parse the market (`competitor-creative-parser`), write the briefs (`market-to-creative-brief`), pre-flight the concepts (this skill). Every concept meets a simulated buyer panel before anyone opens a design tool, weak ideas are cut early, and after launch the panel is checked against real results so the team learns where it was right and where it was wrong.

A panel score is a cheap filter and a signal, not proof of performance. It never replaces a live test and never touches budgets.

| Who | Does what |
|---|---|
| Claude | Writes 12 to 30 buyer profiles from the team's ICP notes and the snapshot's audience signals |
| Jev | Answers typed questions for every concept and profile pair: a Choice (scroll, stop, click) with probabilities, three yes/no checks, a fit Score |
| Code | Rotates option order, builds the heatmap, ranks with guards, applies the go, rework, drop rules, compares with real results later |
| A person | Decides what is produced and what goes to the test |

## When to use

- A brief pack has more concepts or hooks than the team can produce this sprint.
- Before a UGC shoot or a motion job, to pick which of three hooks to produce first.
- To see which buyer profiles no concept reaches.
- After a test, to measure whether the panel's order matched the real order and set its weight for next time.

Not for: deciding budgets, declaring winners, replacing a live test, or judging what only the finished asset shows (picture quality, a voice, pacing).

## Pipeline

```
concepts.jsonl (brief_pack.py --panel-concepts)   profiles.jsonl (Claude)
  1 Profiles (Claude)          -> profiles.jsonl
  2 Panel (Jev, run_panel.py)  -> answers-<track>.jsonl, run-<track>.json, order-check-<track>.json
  3 Matrix (code)              -> matrix-<track>.csv, matrix.md, verdicts.json
  4 Decide (a person)          -> brief_pack.py --panel-verdicts verdicts.json: the table goes into the pack
  5 Test (meta-creative-testing), then calibrate (panel_vs_results.py) with real results
```

## Static track and video track

| | Static | Video |
|---|---|---|
| Panel item | one concept (S1) | one hook variant of a concept (M1-A, M1-B, M1-C) |
| State `ad` | headline, primary text, button, offer line, image description | format, first 3 seconds (seen, on screen, spoken), the rest of the beat sheet as text, end card |
| Choice | keeps scrolling, stops and reads, taps | swipes away in 3 s, keeps watching, taps |
| yes/no | headline about the buyer's problem; offer and terms clear from headline, image and button; would distrust a claim | first 3 s about the buyer's problem; product clear from the first 3 s; would distrust a claim |
| Score | fit with situation and goal, 4 levels | the same |
| Extra rule | | a hook that trails its concept's best hook by 0.10 or more is reworked |
| Question file | `scripts/questions_static.py` | `scripts/questions_video.py` |

## Inputs to ask for

1. `concepts.jsonl` from `market-to-creative-brief` (`brief_pack.py --panel-concepts`).
2. The team's ICP notes: who buys, who churns, what reviews, support and sales hear.
3. `snapshot.md` from `competitor-creative-parser`, for audience signals.
4. Confirmation that concepts and profiles may be sent to the vendor (TypeSafe). Written by the guide, they hold no personal data.

## Step 1. Write the profiles

Follow `references/profile-writing.md`: 12 to 30 profiles, each with situation, goal, objections and what makes them stop scrolling; at least two skeptics, one price-sensitive buyer and one control outside the target; situations, not demographics; no real persons.

## Step 2. Run the panel

```
python3 scripts/run_panel.py --concepts concepts.jsonl --profiles profiles.jsonl --track static --dry-run --out-dir panel
python3 scripts/run_panel.py --concepts concepts.jsonl --profiles profiles.jsonl --track static --smoke \
    --data-handling-confirmed --out-dir panel-smoke
python3 scripts/run_panel.py --concepts concepts.jsonl --profiles profiles.jsonl --track video --order-check 12 \
    --max-usd 0.25 --data-handling-confirmed --out-dir panel
```

- Key from the environment only: `TYPESAFE_API_KEY` (or `--key-env`). Never in chat, a file or a log. `--base-url` takes an https gateway URL.
- `--dry-run` is an offline mock with meaningless numbers. `--smoke` runs 3 pairs live and checks the response shape.
- Spend guard `--max-usd` (default 0.25); tokens come from the API's usage field. One request per pair with all five questions.
- Errors never become answers: a failed pair is marked `error`, and an item with fewer than half of its profiles answered gets no verdict.
- Question design and why: `references/question-design.md`.

## Step 3. Build the matrix

```
python3 scripts/panel_matrix.py --answers panel/answers-static.jsonl panel/answers-video.jsonl \
    --profiles profiles.jsonl --out-dir panel
```

Per item: stop-or-click mass, click mass, mean fit, the share of profiles for each yes/no, the share of pairs in the review band, the profiles it loses. Guards: no ranking under 12 profiles, no leader named on a lead under 0.10. Verdict rules and how to read the heatmap: `references/reading-the-matrix.md`.

## Step 4. Back into the brief pack

```
python3 ../market-to-creative-brief/scripts/brief_pack.py --decisions decisions.json --snapshot snapshot.json \
    --out brief-pack.md --panel-verdicts panel/verdicts.json
```

The pack gets the go, rework, drop table; dropped items are held out of the test plan names and rework items are marked. A person decides; any verdict can be overridden.

## Step 5. Calibrate after launch

```
python3 scripts/panel_vs_results.py --verdicts panel/verdicts.json --results results.csv --metric ctr --out panel-vs-results.md
```

`results.csv` holds real per-item numbers the user exports (item_id, impressions, clicks, conversions, spend). Never invent or estimate them. The report gives rank agreement, the misses and advice on the panel's weight next time.

## Output to the user

1. `matrix.md`: heatmaps, ranking with guards, verdicts with reasons, the profiles each item loses.
2. The go, rework, drop table, and the brief pack rendered with it.
3. Plain caveats: the panel read text, not the finished ads; it is a filter and a signal; the live test decides.
4. After a test: `panel-vs-results.md` and the advice on weight.

## Guardrails

- A panel score is not proof of performance and is never presented as one.
- Never touches budgets, ad accounts or launches. A person decides.
- Profiles describe situations, never real or identifiable people.
- Thresholds are starting values until `panel_vs_results.py` has run on the team's own results.
- No invented results: calibration uses only numbers the user supplies.

## What was checked live and what was not

Checked on 2026-11-15 with the owner's key on the fictional brief pack (6 concepts, 12 panel items) and 12 fictional profiles on `jev-1.14.0` through the direct vendor endpoint: a smoke run (3 pairs, 2,407 input tokens), then 144 pairs across both tracks with an order check on 12 pairs per track; 0 errors, 143,539 input tokens in total, $0.0060 at the listed price. Order agreement was 11 of 12 on each track. Saved output: `scripts/sample_panel/live-run-2026-11-15/` (real model output on fictional concepts). Write-up: `examples/competitor-parse-fictional-market.md` in the repository.

Not checked: real concepts and real buyers, the gateway route, and `panel_vs_results.py` on real results (none exist for a fictional market; the script is covered by offline tests with synthetic fixtures). In the example, `offer_clear` and `distrust_claim` mostly stayed in the review band: rewrite or calibrate them on your own concepts before they gate anything.

## Files

- `scripts/questions_static.py`, `scripts/questions_video.py`: questions, thresholds, state builders.
- `scripts/run_panel.py`: panel runner, standard library only.
- `scripts/panel_matrix.py`: heatmap, ranking, verdicts.
- `scripts/panel_vs_results.py`: calibration against real results.
- `scripts/test_offline.py`: tests, no network, no key.
- `scripts/sample_panel/`: fictional profiles and concepts, plus the saved live run.
- `references/profile-writing.md`, `references/question-design.md`, `references/reading-the-matrix.md`.

Related skills: `market-to-creative-brief` (concepts in, verdicts back), `meta-creative-testing` (survivors go to the test plan), `competitor-creative-parser` (audience signals), `jev-marketing-gates` (runner pattern, hard rules).

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-creative-preflight-panel). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
