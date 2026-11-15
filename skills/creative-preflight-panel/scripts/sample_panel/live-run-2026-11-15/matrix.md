# Pre-flight panel

Built 2026-11-15. A panel score is a cheap filter and a signal, not proof of performance. It never replaces a live test and never touches budgets. A person decides.

Cells: probability mass on stop or click (0 to 1) for one item and one profile. A `?` marks a pair in the review band (over 0.35 and under 0.70): the panel cannot tell whether this person stops or scrolls.

## Static track

3 items x 12 profiles. Ranking: no leader: S1, S3 within 0.10 of each other.

### Heatmap

| Item | p01 | p02 | p03 | p04 | p05 | p06 | p07 | p08 | p09 | p10 | p11 | p12 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 0.55? | 0.64? | 0.59? | 0.43? | 0.99 | 0.71 | 0.89 | 0.93 | 0.95 | 0.72 | 0.98 | 0.95 | 0.78 |
| S3 | 0.55? | 0.66? | 0.25 | 0.51? | 0.99 | 0.81 | 0.91 | 0.78 | 0.92 | 0.49? | 0.96 | 0.94 | 0.73 |
| S2 | 0.20 | 0.40? | 0.23 | 0.25 | 0.68? | 0.81 | 0.63? | 0.36? | 0.43? | 0.77 | 0.70 | 0.63? | 0.51 |

Profiles: p01 Racing mind after work; p02 New parent, broken nights; p03 Shift worker; p04 Phone in bed; p05 Skeptical of sleep claims; p06 Price watcher; p07 Travelling for work; p08 Tried everything; p09 Anxious at bedtime; p10 Good sleeper, curious; p11 Parent of a teenager, buying for the family; p12 Hates talking-head ads.

### Ranking and verdicts

| Rank | Item | Stop or click | Click | Fit (0-3) | Hook about problem | Offer clear | Distrust | Review band | Verdict | Reasons |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S1 | 0.78 | 0.25 | 2.24 | 83% | 0% | 8% | 33% | go | offer or product clear at first sight for 0 of 12 profiles |
| 2 | S3 | 0.73 | 0.32 | 2.20 | 83% | 0% | 8% | 33% | go | offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| 3 | S2 | 0.51 | 0.12 | 1.84 | 0% | 0% | 17% | 50% | rework | fit 1.84 of 3, under 2.0 for a go; hook about the person's problem for 0 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles; loses 3 of 12 profiles |

### Profiles each item loses

- S1: none
- S3: p03 (0.25, fit 1.3)
- S2: p01 (0.20, fit 1.8), p03 (0.23, fit 1.3), p04 (0.25, fit 2.1)

## Video track

9 items x 12 profiles. Ranking: no leader: M1-A, M2-B, M3-A, M3-B within 0.10 of each other.

### Heatmap

| Item | p01 | p02 | p03 | p04 | p05 | p06 | p07 | p08 | p09 | p10 | p11 | p12 | Mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1-A | 0.53? | 0.71 | 0.84 | 0.48? | 0.91 | 0.53? | 0.87 | 0.66? | 0.79 | 0.68? | 0.89 | 0.95 | 0.74 |
| M2-B | 0.70 | 0.77 | 0.59? | 0.66? | 0.92 | 0.48? | 0.83 | 0.70 | 0.44? | 0.37? | 0.79 | 0.86 | 0.68 |
| M3-A | 0.49? | 0.86 | 0.51? | 0.77 | 0.84 | 0.71 | 0.88 | 0.49? | 0.71 | 0.31 | 0.89 | 0.58? | 0.67 |
| M3-B | 0.38? | 0.67? | 0.53? | 0.66? | 0.91 | 0.62? | 0.91 | 0.52? | 0.77 | 0.62? | 0.92 | 0.42? | 0.66 |
| M3-C | 0.22 | 0.90 | 0.53? | 0.68? | 0.87 | 0.65? | 0.83 | 0.49? | 0.67? | 0.36? | 0.89 | 0.40? | 0.62 |
| M1-C | 0.17 | 0.60? | 0.38? | 0.39? | 0.83 | 0.45? | 0.78 | 0.60? | 0.73 | 0.61? | 0.93 | 0.93 | 0.62 |
| M2-A | 0.35 | 0.83 | 0.38? | 0.66? | 0.66? | 0.54? | 0.83 | 0.37? | 0.16 | 0.88 | 0.74 | 0.92 | 0.61 |
| M2-C | 0.35 | 0.66? | 0.53? | 0.24 | 0.80 | 0.44? | 0.68? | 0.36? | 0.52? | 0.62? | 0.80 | 0.93 | 0.58 |
| M1-B | 0.21 | 0.50? | 0.60? | 0.40? | 0.77 | 0.49? | 0.87 | 0.35? | 0.51? | 0.46? | 0.84 | 0.91 | 0.58 |

Profiles: p01 Racing mind after work; p02 New parent, broken nights; p03 Shift worker; p04 Phone in bed; p05 Skeptical of sleep claims; p06 Price watcher; p07 Travelling for work; p08 Tried everything; p09 Anxious at bedtime; p10 Good sleeper, curious; p11 Parent of a teenager, buying for the family; p12 Hates talking-head ads.

### Ranking and verdicts

| Rank | Item | Stop or click | Click | Fit (0-3) | Hook about problem | Offer clear | Distrust | Review band | Verdict | Reasons |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | M1-A | 0.74 | 0.09 | 2.27 | 83% | 0% | 8% | 42% | go | offer or product clear at first sight for 0 of 12 profiles |
| 2 | M2-B | 0.68 | 0.05 | 2.24 | 33% | 0% | 0% | 42% | go | hook about the person's problem for 4 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles |
| 3 | M3-A | 0.67 | 0.11 | 2.27 | 83% | 0% | 0% | 33% | go | offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| 4 | M3-B | 0.66 | 0.10 | 2.16 | 25% | 0% | 0% | 67% | rework | 67% of answers in the review band: too uncertain for a go; hook about the person's problem for 3 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles |
| 5 | M3-C | 0.62 | 0.09 | 2.31 | 75% | 0% | 0% | 58% | rework | 58% of answers in the review band: too uncertain for a go; offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| 6 | M1-C | 0.62 | 0.06 | 2.14 | 33% | 8% | 8% | 50% | rework | trails hook M1-A of the same concept by 0.12: replace this opening; hook about the person's problem for 4 of 12 profiles; offer or product clear at first sight for 1 of 12 profiles; loses 1 of 12 profiles |
| 7 | M2-A | 0.61 | 0.07 | 2.18 | 17% | 0% | 0% | 42% | go | hook about the person's problem for 2 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| 8 | M2-C | 0.58 | 0.05 | 2.11 | 8% | 0% | 0% | 58% | rework | 58% of answers in the review band: too uncertain for a go; hook about the person's problem for 1 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| 9 | M1-B | 0.58 | 0.06 | 2.19 | 0% | 0% | 8% | 58% | rework | 58% of answers in the review band: too uncertain for a go; hook about the person's problem for 0 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |

### Profiles each item loses

- M1-A: none
- M2-B: none
- M3-A: p10 (0.31, fit 1.7)
- M3-B: none
- M3-C: p01 (0.22, fit 2.1)
- M1-C: p01 (0.17, fit 1.9)
- M2-A: p09 (0.16, fit 2.0)
- M2-C: p04 (0.24, fit 1.9)
- M1-B: p01 (0.21, fit 1.9)

## Concepts: go, rework, drop

| Concept | Track | Verdict | Best item | Items | Reasons |
|---|---|---|---|---|---|
| S1 | static | go | S1 | S1 go | offer or product clear at first sight for 0 of 12 profiles |
| S3 | static | go | S3 | S3 go | offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |
| S2 | static | rework | S2 | S2 rework | fit 1.84 of 3, under 2.0 for a go; hook about the person's problem for 0 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles; loses 3 of 12 profiles |
| M1 | video | go | M1-A | M1-A go, M1-C rework, M1-B rework | offer or product clear at first sight for 0 of 12 profiles |
| M2 | video | go | M2-B | M2-B go, M2-A go, M2-C rework | hook about the person's problem for 4 of 12 profiles; offer or product clear at first sight for 0 of 12 profiles |
| M3 | video | go | M3-A | M3-A go, M3-B rework, M3-C rework | offer or product clear at first sight for 0 of 12 profiles; loses 1 of 12 profiles |

A person decides. Survivors (go, and rework after the fix) go to the test plan in meta-creative-testing; the live test decides, the panel does not.
