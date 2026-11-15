---
name: market-to-creative-brief
description: Claude + Jev market-to-brief step. Turns the market snapshot from competitor-creative-parser plus the team's own constraints into production decisions and two briefs, one for static designers and one for the motion design or video team, with every recommendation tied to snapshot numbers and parsed ad ids. Code re-checks each number against the snapshot, checks gaps and crowded values, beat timings and the test budget, then assembles the brief pack, a copy-check file and a concepts file for the pre-flight panel. Use for "write creative briefs from competitor research", "brief for designers", "motion brief", "video ad brief", "what creatives should we make next", "turn the ad library teardown into briefs", "creative strategy from competitor ads".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Market to creative brief (Claude + Jev)

Second step of the Claude + Jev creative system. `competitor-creative-parser` gives a counted picture of the market (Jev tagged every competitor ad, code counted). This skill turns that picture into what to make next: decisions with their numbers, a static brief for designers and a motion brief for the video team. Claude writes, code checks every number, a person approves.

| Who | Does what |
|---|---|
| Claude | Reads the snapshot and the team's constraints, picks the moves, writes `decisions.json` with the briefs |
| Jev | Already did its part: the tags and probabilities behind every share in the snapshot. Optional: advisory copy checks through `jev-marketing-gates` |
| Code (`brief_pack.py`) | Re-reads each cited number from the snapshot, checks gaps, crowded values, ad ids, beat timings and the test budget, renders the pack |
| A person | Approves the pack before any production or spend |

## When to use

- Right after a market snapshot: "what do we make next, and why".
- Before a creative sprint, so designers and the motion team get briefs with references by ad id instead of a mood board.
- When a stakeholder asks why a concept was chosen: every decision shows the numbers and the ads behind it.

Not for: inventing performance, copying competitor ads, launching anything. Use `meta-creative-testing` for the test itself.

## Pipeline

```
snapshot.json (+ tags) + team constraints (+ own results, if supplied)
  1 Decide (Claude)          -> decisions.json: moves, evidence, hypotheses
  2 Brief (Claude)           -> static_briefs and motion_briefs inside decisions.json
  3 Check and assemble (code)-> brief-pack.md, copy-check.csv, concepts.jsonl
  4 Approve (a person)       -> production starts
  5 Hand-off                 -> meta-creative-testing (test plan), jev-marketing-gates (copy check)
```

## Static track and video track

| | Static | Video |
|---|---|---|
| Evidence used | hook type, angle, offer type and placement, visual format, risky claims, hook specificity, CTA clarity, words on image, price shown | hook type and channel, angle, format, structure, creator type, product in first 3 s, risky claims, pacing facts, captions |
| Brief for | designers | motion design or video team |
| Template | `references/static-brief-template.md` | `references/motion-brief-template.md` |
| Variants | one variable each (headline, image, offer placement) | three hooks for seconds 0 to 3 on one body, plus cut-downs |
| Code checks | required fields, ad ids | required fields, ad ids, exactly three hooks, beats from 0 without gaps, hook ends by 3 s, length within the durations |
| Test plan names | `PROJECT \| TEST \| Static \| S1 v1 \| src: market s01+s09` | `PROJECT \| TEST \| Video \| M1 hook A \| src: market v06+v12` |

## Inputs to ask for

1. `snapshot.json` and the tags files from `competitor-creative-parser`.
2. The product in one line and what it really does (facts the copy may state).
3. Brand rules: tone, banned claims, banned imagery.
4. Offers allowed and how the price must be shown.
5. What the team can produce: designers, motion, UGC shoots per month.
6. Test budget and target CPA, or say none.
7. Own performance data (past winners with their numbers), only if the team has it. Never estimate it.

## Step 1. Decide

Read `snapshot.md`, then pick 3 to 6 decisions across the two tracks with the moves in `references/decision-rules.md`: `enter_gap`, `out_execute`, `avoid`, `iterate_own`. For each one write:

- the dimension and value, the number of concepts;
- the rationale in plain sentences with the snapshot numbers and ad ids ("8 of 12 statics, all 5 advertisers, lead with an outcome promise; none uses comparison");
- evidence lines that `brief_pack.py` re-reads from the snapshot;
- a hypothesis for the test: "A beats B on metric M because R".

A gap means nobody stands there, not that it works. Low-sample tracks are directional and say so.

## Step 2. Write the briefs

Fill one static brief per static concept and one motion brief per video concept from the templates. Headlines, buttons and hooks are written word for word. References name what to learn from each ad id and what to leave. Claims in the copy are listed with why they are allowed.

## Step 3. Check and assemble

```
python3 scripts/brief_pack.py --decisions decisions.json --snapshot snapshot.json --out brief-pack.md \
    --gates-csv copy-check.csv --panel-concepts concepts.jsonl
```

- A cited number that does not match the snapshot, an unknown ad id, a gap that is not a gap, an `out_execute` on a value that is not crowded or own results cited without data: error, nothing is rendered (`--allow-errors` renders a draft marked "Not ready").
- A missing brief field or a wrong hook count: blocking, listed under "Not ready", exit code 1.
- Low sample and a plan larger than the budget's kill reads: warnings in the pack.

Try it on the fictional sample: `python3 scripts/brief_pack.py --decisions scripts/sample_decisions.json --snapshot scripts/sample_snapshot.json --out brief-pack.md`.

## Step 4. Hand-offs

- `copy-check.csv` (id, headline, body, brand_rules) goes to `jev-marketing-gates` for an advisory copy check against the brand rules. The platform's review stays the real check.
- `concepts.jsonl` feeds the pre-flight panel, which screens concepts against buyer profiles before production.
- The test plan section lists every ad name for `meta-creative-testing`: one broad ad set by default, its kill and winner criteria, a control that stays live.
- Nothing is published, uploaded or launched by this skill. A person approves the pack.

## Output to the user

1. `brief-pack.md`: decisions table with evidence and ad ids, rationale and hypothesis per decision, the static briefs, the motion briefs, the test plan names.
2. The open items: errors, blocking fields, warnings.
3. What the pack cannot say: how the concepts will perform. That is what the test is for.

## Guardrails

- Every number comes from the snapshot or from data the team supplied. No invented benchmarks, CTRs or CPAs.
- Patterns, not copies. References say what to leave.
- Claims follow the brand rules and the platform's current policy, read by a person.
- Budget and spend decisions belong to a person and to `meta-creative-testing`.

## What was checked and what was not

Checked on 2026-11-15: the pack for the fictional sample market (`scripts/sample_decisions.json` against `scripts/sample_snapshot.json`, a copy of the live snapshot from `competitor-creative-parser`) renders with no errors and no blocking fields; `scripts/test_offline.py` covers the checks. The example write-up is `examples/competitor-parse-fictional-market.md` in the repository. Not checked: briefs from a real market, and whether these concepts perform; only a live test answers that.

## Files

- `scripts/brief_pack.py`: checker and renderer, standard library only, no network.
- `scripts/test_offline.py`: tests, no network, no key.
- `scripts/sample_decisions.json`, `scripts/sample_snapshot.json`: the fictional example.
- `references/decision-rules.md`: moves, rules, the `decisions.json` shape.
- `references/static-brief-template.md`, `references/motion-brief-template.md`: brief fields and writing rules.

Related skills: `competitor-creative-parser` (input), `meta-creative-testing` (test plan), `jev-marketing-gates` (copy check), `creative-testing-research` (hypotheses and test design).

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-market-to-creative-brief). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
