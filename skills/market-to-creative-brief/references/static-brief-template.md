# Static brief template (for designers)

One brief per concept. A concept is one angle and one hook; variants change one thing each. Every field below is required unless marked optional, and `brief_pack.py` lists a missing one as blocking.

## Fields in `static_briefs[]`

| Field | What to write | Example (fictional) |
|---|---|---|
| `concept_id` | S1, S2 ... | S1 |
| `decision_id` | The decision this concept serves | D1 |
| `concept` | A name of a few words | Counting sheep or 8 minutes |
| `angle` | Taxonomy value plus one line on what changes for the viewer | save_time: a fixed routine instead of an open-ended struggle |
| `hook` | The headline, word for word | Counting sheep, or an 8-minute wind-down? |
| `layout` | Focal point, text hierarchy, where the offer and button sit, panel widths | Two equal panels, headline across both, price line under the right panel |
| `visual` (optional) | Subject, style, colours, what must not appear | Grey line-art sheep left, phone timer right |
| `copy` | `headline`, `primary_text`, `cta` (button label), verbatim | |
| `offer` | The offer and where it appears | 7 days free, annual price in a footer line |
| `sizes` | Every size with pixels and safe-zone notes | 1:1 1080x1080, 4:5 1080x1350, 9:16 1080x1920 |
| `variants` | One variable per variant, named | v2: left panel "Scrolling till 1am" |
| `references` | Ad ids from the snapshot, each with `take` (the pattern to learn) and `leave` (what not to copy) | s01: take the night palette, leave the outcome promise |
| `avoid` | What must not appear, including the market's risky claims | minutes-to-sleep promises |
| `claims_notes` | Each claim in the copy and why it is allowed, plus what a person must verify | 8 minutes is the routine length, a product fact |
| `acceptance` | Checks a person ticks before the file ships | headline readable at phone size in under 2 seconds |

## Writing rules

- Write the headline and button label verbatim. A designer never invents copy.
- References are patterns, not copies. Name what to learn from each ad id and what to leave. Never ask for a recreation of a competitor's layout, character or line.
- Put the market number that motivated the concept in the decision rationale, not in the ad.
- Prices and figures in the copy use placeholders (`[annual price]`) unless the team gave the real figure. The acceptance list says who checks it.
- Claims: every claim in `copy` appears in `claims_notes`. Health, money and guaranteed-result claims follow the brand rules and the platform's current policy page, which a person reads; run the copy lines through `jev-marketing-gates` (`--gates-csv`) as an advisory pre-check.
- Sizes: 1:1 and 4:5 for feeds, 9:16 for stories and reels placements with text inside the safe zone. Ask the team which placements the test plan uses.
- Variants: change one element per variant (headline, image, offer placement), so the test reads cleanly.

## How it renders

`brief_pack.py` renders each static brief as a section with the fields above, the variants, references by ad id, avoid list, claim notes and a tick-box acceptance list, then names every variant in the test plan as `PROJECT | TEST | Static | S1 v1 | src: market s01+s09`.
