# Decision rules and the decisions file

How Claude turns `snapshot.json` into production decisions, and the exact shape of `decisions.json` that `scripts/brief_pack.py` checks and renders.

## The four moves

| Move | Use it when the snapshot shows | Concepts | What the brief must do |
|---|---|---|---|
| `enter_gap` | A taxonomy value no resolved creative uses, or only one advertiser uses | 1 to 2 per gap | Make the new value obvious in the first screen or the first 3 seconds |
| `out_execute` | A value the snapshot marks crowded (at least 30% of creatives and 50% of advertisers) that the team still needs | 1 per crowded value | Name the one thing done better, tied to a weak score or flag in the snapshot (low hook specificity, unclear CTA, no price shown) |
| `avoid` | A flag the market overuses that the brand rules forbid, or a risky claim cluster | 0 | Add the item to every brief's "Avoid" and claim notes |
| `iterate_own` | The team supplied its own winners and their numbers | 1 per winner | New hook or format on a proven idea; cite the team's own numbers only |

Rules that `brief_pack.py` enforces:

- `enter_gap` on a value used by two or more advertisers is an error. A possible gap (too many unresolved items in the dimension) passes with a warning: say "possible gap" in the rationale.
- `out_execute` on a value the snapshot does not mark crowded is an error.
- Every decision carries at least one evidence line, and each line is re-read from the snapshot. A number that does not match is an error and the pack is not rendered.
- `cites_own_performance: true` needs `constraints.own_performance` to be supplied by the team. Claude never writes a CTR, CPA or ROAS the team did not give.
- Every ad id in `refs` and in brief references must exist in the snapshot.
- A low-sample track (under 20 creatives) marks its decisions as directional in the pack.

Rules Claude follows that code cannot check:

- Pick 3 to 6 decisions in total. More dilutes the test budget.
- Prefer gaps the team can produce with what it has (`constraints.can_produce`). A gap in a format nobody on the team can make is a note, not a decision.
- A gap is a place nobody stands, not proof that the place works. Write the rationale as "nobody does X", never "X will win".
- Durability (long-running ads) is a weak signal. Use it to pick references, not to claim results.
- Every decision that enters production gets a one-sentence hypothesis in the form "A beats B on metric M because R". The test plan judges it.
- Keep the split by track: static decisions use static evidence, video decisions use video evidence. Cross-track observations go in the rationale text only.

## How many concepts and creatives

The pack counts creatives as one per static variant and one per motion hook variant. With `constraints.test_budget` (amount and target CPA) it compares that count with the number of creatives that can reach a kill read: about 2x target CPA of spend each, the kill rule of `meta-creative-testing`. If the plan is larger, the pack warns: cut variants before cutting concepts.

## decisions.json

```json
{
  "market": "category, country, language",
  "notice": "optional line shown at the top, for example a FICTIONAL label",
  "project": "PROJECT",
  "test_name": "TEST",
  "constraints": {
    "product": "one line",
    "brand_rules": "tone, banned claims, banned imagery",
    "offers": "what may be offered and how the price is shown",
    "can_produce": "who makes statics, motion, UGC",
    "test_budget": {"amount": 0, "currency": "USD", "target_cpa": 0, "label": "example values or real"},
    "own_performance": null
  },
  "decisions": [
    {
      "id": "D1", "track": "static", "move": "enter_gap",
      "dimension": "hook_type", "value": "comparison", "concepts": 2,
      "rationale": "plain sentences with the numbers",
      "hypothesis": "A beats B on cost per trial because R",
      "evidence": [
        {"track": "static", "dimension": "hook_type", "value": "comparison", "metric": "creatives", "expected": 0}
      ],
      "refs": ["s01", "s05"]
    }
  ],
  "static_briefs": [],
  "motion_briefs": []
}
```

Evidence metrics:

| Metric | Reads | Needs `value` |
|---|---|---|
| `creatives`, `share`, `advertisers`, `advertiser_share` | a row of a tagged dimension | yes |
| `unresolved` | unresolved count of a dimension | no |
| `flag_yes`, `flag_share`, `flag_review` | a yes/no flag (`risky_claim`, `social_proof`, `product_in_first_3s` ...) | no |
| `score_mean` | mean of a score (`hook_specificity`, `cta_clarity` ...) | no |
| `fact` | a code fact by dotted path, such as `cuts_per_10s.median` | no |

Shares are fractions (0.667), compared to 0.005.

Brief fields are listed in `static-brief-template.md` and `motion-brief-template.md`. A missing required field is "blocking": the pack renders, lists it under "Not ready" and the script exits with 1.
