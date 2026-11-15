# Writing buyer profiles

Claude writes 12 to 30 buyer profiles before the panel runs. They are the panel: if they are vague, every concept looks fine; if they are all the same person, the matrix has one column repeated.

## Where profiles come from

1. The team's own ICP notes: who buys, who churns, what support tickets and reviews say, what sales calls hear. Mark these `"source": "icp"`.
2. Audience signals in the market snapshot: who competitor hooks speak to (problem callouts name the pain, creator types show who the market casts), which claims are common enough that a skeptic would have seen them many times. Mark these `"source": "snapshot"`.
3. Never a real person. No names, no handles, no photos, no copied review text. A profile is a situation, not an individual.

## The four fields

| Field | Write | Avoid |
|---|---|---|
| `situation` | What their days and nights look like, in one or two concrete sentences | Demographics alone ("woman, 34, urban") |
| `goal` | What they want to change, in their words | The product's feature list |
| `objections` | What makes them doubt or skip: past tries, price fears, trust issues | Generic "is busy" |
| `stops_scrolling_for` | The kind of line, picture or idea that makes them stop | "Good ads" |

Plus `profile_id` (p01 ...), a short `label` for the matrix (not sent to Jev), `source`, and an optional `note`.

Example (fictional):

```json
{"profile_id": "p05", "label": "Skeptical of sleep claims",
 "situation": "Engineer in her forties who has read about sleep and distrusts big promises.",
 "goal": "Find a routine that is plausible and easy to keep.",
 "objections": "Distrusts 'fall asleep in X minutes' claims, user counts and testimonials; wants to know what the app actually does.",
 "stops_scrolling_for": "A plain statement of what the product does, with no hype.",
 "source": "snapshot"}
```

## Mix

- At least two skeptics: people who have seen the market's common claims and distrust them.
- At least one price-sensitive buyer, if the offer has a trial or a subscription.
- At least one person outside the target (a good sleeper, a non-buyer) as a control. If the control loves every concept, the panel is not discriminating: rewrite the questions or the profiles before trusting it.
- Spread across the situations the product really serves. Do not stack the panel with the people the favourite concept was written for.
- 12 profiles is the floor for ranking (`panel_matrix.py --min-profiles`). Under it, the matrix is directional and nothing is ranked.

## Rules

- No protected or sensitive attributes as targeting logic (health conditions, religion, ethnicity, sexual orientation). Describe situations and goals. If the product touches health, describe the experience ("lies awake for an hour"), not a diagnosis.
- Keep every field short. Irrelevant text in the state weakens Jev's answers.
- Write the profiles before reading the concepts, or have a different person write them, so they are not tuned to the favourite.
- Version the profile file with the run. A changed panel is a new panel; compare matrices only on the same profiles.
- Profiles go to the vendor as text. They contain no personal data when written this way; confirm with the user before a live run (`--data-handling-confirmed`).
