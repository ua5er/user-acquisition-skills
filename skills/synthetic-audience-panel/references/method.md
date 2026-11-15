# Method and measured reference

This skill packages the method supplied by Vlad Yasinski. It does not claim a fresh live validation of the packaged script.

The reference checks used `jev-1.14.0` on 2026-11-15. Stimuli were fictional Spanish-app ads represented as text. API timings and costs below are historical measurements or stated estimates, not service guarantees.

## Request layout

Put the stimulus into the state once. Put each person's description into an independent typed question. People do not see or influence one another.

Jev returns probabilities. Code builds profiles, applies weights and computes the report. No language model writes the numerical results.

The documented vendor API is:

```text
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <environment key>
Content-Type: application/json
```

The body contains `model`, `state` and `questions`. Questions are keyed by local ids.

- `score`: instructions plus an ordered `criteria` list, with 2 to 10 levels. Returns level probabilities and a score.
- `choice`: instructions plus an option-to-description `criteria` object. Returns a choice and option probabilities.
- `noul`: instructions returning a yes probability. The packaged runner does not need this type.

The reported context capacity is about 64k tokens for state and questions together. Keep state relevant. The runner uses 125 score questions or 60 choice questions per request, with at most 6 in flight. These counts do not guarantee that arbitrarily long inputs fit the context.

The model reads literally. Negations, numerical reasoning, arithmetic and dates are weak points. It can be steered by text inside the state. Choice questions lean toward the first option. Rotate the substantive options and leave the nothing-blocks option last.

Images through `assets` and a special header were described but not tested. This skill sends text only.

## Historical measurements

- Layout check: 24 people and two ads, with all people in one request versus one request per person. Expected depth had Pearson correlation 0.99 and Spearman correlation 0.98. Mean absolute difference was 0.09 on a 0 to 3 scale.
- Speed check: 250 people in one request took 0.6 seconds and 32,594 input tokens.
- Full panel: 1,000 depth questions plus about 250 barrier questions, in 13 requests with 6 in flight, took 0.9 to 1.0 seconds. The worked tool example reports 0.9 seconds.
- Cost: about 203,000 input tokens per stimulus, costing $0.0085 at $0.042 per million input tokens. Output was free. The worked two-ad example cost $0.0171.
- No rate-limit errors occurred in about 80 requests. Published rate limits were not available. Keep backoff and retries.
- Layout sensitivity, panel answers: the same panel with the ad under a different state key and an extra id field gave higher levels (control tap 0.22 instead of 0.15) and nearly the same gaps between the two ads (+58, +51, +48 against +54, +46, +46 per 1,000). Keep one state layout for every variant you compare, and compare gaps, not levels.
- Repeat noise, panel answers: mean per-person score movement was 0.035 on a 0 to 3 scale. The cohort funnel moved by at most 5 per 1,000.
- Factor directions, panel answers: controls, sceptics, price-tight people and rushed people scored lower.
- Generosity, panel answers: people described as having no need still had tap probability 0.14 to 0.21.
- Subgroup stability, panel answers: 100-person samples using different seeds swung subgroup ratios by a factor of two. A full factorial grid avoids sampling variation. A fixed subset is reproducible, not literally the full grid.

These findings support the request layout and its use as a comparison sieve. They do not establish agreement with real delivery results.

## Historical discrimination example

### panel answers, not delivery metrics

Cold mix, per 1,000:

| Stimulus | Stop | Tap | Intent |
|---|---:|---:|---:|
| A, flawed guarantee claim | 641 | 320 | 38 |
| B, rewrite | 698 | 366 | 81 |
| Generic contrast | 190 | 58 | 8 |
| B minus A | +57 | +46 | +43 |

The method note rounded the hard-to-believe objection to 30 percent, 5 percent and 50 percent. The worked output gives the more precise panel answers below. These are the same evidence at different displayed precision.

### panel answers, not delivery metrics

| Reading | A | B | Generic |
|---|---:|---:|---:|
| Hard to believe | 29.5% | 5.2% | 50.2% |
| No reason to act now | 67.5% | 81.1% | Not supplied |
| Hook strength | 0.678 | 0.759 | Not supplied |
| Follow-through | 0.149 | 0.265 | Not supplied |
| Sceptic gap | 0.369 | 0.540 | Not supplied |
| Price gap | 0.318 | 0.481 | Not supplied |
| Control tap probability | 0.149 | 0.171 | Not supplied |

The worked comparison reported panel answers of 80.6% going further with B, 4.8% with A and 14.6% about the same. Its verdict was B ahead. The prototype's person-better shares were unweighted; the packaged report explicitly uses weighted shares. Do not substitute these archived percentages for a fresh report.

### panel answers, not delivery metrics

| Mix | A stop / tap / intent | B stop / tap / intent |
|---|---|---|
| Warm | 808 / 458 / 56 | 860 / 526 / 125 |
| Retargeting | 857 / 517 / 71 | 909 / 596 / 166 |

B was ahead in all three reference mixes.

## Cohort construction

Use situations and attitudes, never age, gender, income or ethnicity. Include a control option meaning no need for the product. Avoid incoherent control descriptions.

The default target grid is:

```text
2 fits x 7 stages x 2 urgency options x 3 price attitudes
x 2 decision styles x 3 trust attitudes x 2 moments = 1,008
```

Controls omit stage and urgency. Their remaining combinations add 36 profiles, making 1,044. A deterministic shuffle with seed 7 keeps the first 1,000 by default. This is 1,000 distinct descriptions, not all 1,044 combinations. Use the entire grid when feasible.

The packaged script uses Mulberry32 and Fisher-Yates, not the prototype's random-module shuffle. Saved profiles therefore need not match the original panel.

## Weighting

Mix shares are assumptions unless supplied from real data. The balanced design and the desired audience mix are separate.

For each person, multiply the desired share divided by the observed design share for every applicable factor. Normalise the resulting weights. Then perform 8 passes of iterative proportional fitting, rescaling each option to its desired marginal.

Target-only marginals are conditional on people who have that factor. They do not include controls. Other factors use the whole cohort. A zero desired share removes the corresponding people.

The report exposes assumptions, achieved marginals and individual weights. It rejects unsupported mixes and residual marginal differences above 0.005. These are implementation checks, not statistical accuracy bounds.

Effective size is the reciprocal of the sum of squared weights. It describes weight concentration, not the number of independent human observations.

## Funnel and readings

For ordered probabilities `p0 ... pK`, depth at level `j` is the tail sum `pj + ... + pK`.

For the default ad scale:

- Stop is `p1 + p2 + p3`.
- Tap is `p2 + p3`.
- Intent is `p3`.

Multiply the weighted mean by 1,000 for the displayed funnel.

The default readings are:

- Hook strength: target people's stop probability in a rushed moment.
- Follow-through: core intent divided by core tap.
- Control check: tap probability among no-need controls.
- Selectivity: core tap divided by control tap.
- Sceptic gap: sceptic tap divided by open-to-ads tap, within targets.
- Price gap: tight-price intent divided by easy-price intent, within targets.
- Cold pull: unaware-or-problem tap divided by product-or-most-aware tap, within targets.

Despite their names, the gap readings are ratios, not percentage-point differences. Undefined ratios are `null`.

Ask every fourth target person for a main barrier. Aggregate their picked options using weights renormalised within that subsample. This follows the prototype's picked-choice aggregation, not an average of barrier probabilities.

## Comparisons

Use exactly the same people for every variant. The packaged score is expected depth computed from level probabilities on the original level-index scale.

Compare each later variant with the first:

- Show funnel gaps per 1,000.
- Show weighted shares with expected-depth differences greater than 0.05 in each direction.
- Put all other people in the about-same share.
- Call a leader ahead only when the deepest two funnel gaps have the same strict sign and at least one has magnitude at least 10 per 1,000.
- Otherwise say too close to call.

With only one nonzero depth threshold, the two-gap rule cannot be satisfied, so the verdict remains too close to call. The rule is a conservative comparison heuristic, not a significance test.

## Onboarding adaptation

One request state holds one screen and a chunk of people. Include product, arrival promise, step position, prior-step summary and all visible copy, inputs, choices, buttons, skip routes, prices and permissions.

An ordered completion scale can be:

```json
[
  "Closes the app here.",
  "Hesitates and looks for a way to skip.",
  "Completes this step.",
  "Completes this step and feels more committed to the product."
]
```

Possible barrier options:

```json
{
  "too_long": "Too many steps come before any value.",
  "personal_data": "The screen asks for personal data without a reason.",
  "unclear_benefit": "The benefit of this step is unclear.",
  "commitment": "The price or commitment is too high.",
  "permission": "The permission is not justified.",
  "promise": "The content does not match the arrival promise.",
  "nothing": "Nothing stops this person."
}
```

For a paywall, the method note suggests closes, dismisses and continues free, starts trial, buys now. For a permission prompt, it suggests denies and feels pushed, denies, allows. When merging screen runs, first express all screens using a common scale and a consistent completion index.

For person `i`, let `c(i,k)` be the tail probability of completing screen `k`. Entry survival is the product of completion probabilities at earlier screens. Completed survival includes the current screen.

The entry funnel is 1,000 times weighted entry survival. Hazard is weighted loss at the screen divided by weighted entry survival. Weighting happens after the per-person products, not before. This preserves the different people who remain at each step.

Answers are independent across screens. Memory exists only in the written context. Step position and patience approximate fatigue; they do not simulate it.

The supplied onboarding estimate was about 170 tokens per person per screen: about $0.007 for 1,000 people, or about $0.01 including barriers. A 12-screen flow was estimated at about 12 cents, and two variants at about 25 cents. The note estimated about 100 requests per flow, with 6 in parallel and a few seconds in total. These are estimates, not new measurements of this CLI.

## Validation and calibration

Before trusting a new stimulus type:

1. Compare 24 batched people with individual requests.
2. Repeat a request and measure score and cohort movement.
3. Include an obviously worse stimulus.
4. Confirm controls score clearly lower.
5. Check factor directions.
6. Rotate barrier options and test whether the top answer follows position.

For real-result calibration, fewer than 8 matched observations support no calibration output. With 8 to 14, report rank agreement only. From 15, a fitted range with leave-one-out error is defensible.

For onboarding, compare hazard ranks with actual step-drop ranks and report an interval. If the panel fails to track real outcomes, keep it only as a source of wording and barrier hypotheses.
