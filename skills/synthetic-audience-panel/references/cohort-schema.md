# Cohort schema and writing guide

A cohort file describes a factorial design. It does not contain real people or a list of authored biographies. The runner builds distinct people from the design, shuffles them deterministically and keeps `size` profiles.

## Contract

Required top-level fields:

- `factors`: ordered object of factor ids to option objects. Each factor has 2 to 7 options. Each option maps a short id to a nonempty clause.
- `control`: object with `factor` and `option`, naming the no-need group.
- `target_only`: list of factors omitted from controls.
- `mixes`: nonempty object of named mixes.
- `size`: positive integer, no larger than the available grid.
- `seed`: integer for deterministic shuffling.

A mix maps every factor to every option's numeric share. Each factor's shares must sum to 1. Shares are between 0 and 1. Target-only shares are conditional on the target subgroup.

The built-in names are `cold`, `warm` and `retargeting`. A custom cohort may use other names. `report --mix` accepts a saved mix name or a path to a JSON object containing one mix.

Factor and option insertion order controls sentence construction. Option order also affects deterministic grid construction. Keep the same saved cohort file across variants.

`id` is reserved. Exact demographic factor names are rejected as a basic check. The agent must also review semantics; code cannot detect all demographic proxies or unsuitable clauses.

## Full small example

This is an illustrative schema fixture, not a recommended research panel. Its shares are assumptions, not observations.

```json
{
  "factors": {
    "fit": {
      "core": "needs help with the task described in `product`",
      "outside": "has no need for the task described in `product`"
    },
    "moment": {
      "rushed": "has little time to explore",
      "browsing": "has time to explore"
    }
  },
  "control": {
    "factor": "fit",
    "option": "outside"
  },
  "target_only": [],
  "mixes": {
    "cold": {
      "fit": {
        "core": 0.5,
        "outside": 0.5
      },
      "moment": {
        "rushed": 0.5,
        "browsing": 0.5
      }
    }
  },
  "size": 4,
  "seed": 7
}
```

Save it as `cohort-small.json`, then validate and write it:

```sh
python3 skills/synthetic-audience-panel/scripts/audience_panel.py cohort \
  --cohort cohort-small.json --size 4 --seed 7 --out cohort-small-validated.json
```

The `cohort` command's `--size` and `--seed` replace the input values. Pass them explicitly for a small design. Their defaults are 1000 and 7.

## Writing factors for a niche

Start from actual decision situations in the owner's product notes. Ask what changes relevance, effort, trust, urgency or willingness to commit.

Good factors describe a current situation or attitude:

- Already uses an alternative versus is searching for a first solution.
- Needs a result soon versus has no deadline.
- Wants to start quickly versus accepts setup for a better result.
- Reluctant to grant permissions versus comfortable when the benefit is clear.

Do not use age, gender, income or ethnicity. Price attitude is willingness to pay for this type of product, not an income bracket. Do not use identity proxies.

Write one short clause per option. Clauses must form a readable sentence after `This person`. Make options distinct and internally coherent.

Always include a no-need control. The agent must verify that its clause really expresses no need. Naming an option `outside` is not sufficient.

Put factors that do not make sense for controls into `target_only`. The default cohort omits stage and urgency from controls. This prevents a no-need person from also being described as waiting for an offer.

The supported design is a Cartesian product with target-only omissions for controls. It does not support arbitrary exclusion rules or conditional factors beyond that. Rewrite the factorisation when combinations become incoherent.

Aim for about 1,000 profiles. A small sample can miss combinations and destabilise subgroup ratios. The script rejects a sample with no targets or no controls; weighting can also reject an unsupported positive-share option.

Mixes are assumptions until supported by data. Do not describe the default cold, warm or retargeting mixes as market measurements.

## Default design

The generated cohort has these factors:

- `fit`: core, adjacent, outside.
- `stage`: unaware, problem, solution, competitor, lapsed, product, most.
- `urgency`: soon, someday.
- `price`: tight, value, easy.
- `decision`: quick, careful.
- `trust`: sceptic, neutral, open.
- `moment`: rushed, browsing.

The prototype called `moment` attention. The packaged file and reports use `moment` consistently.

The target grid has 1,008 profiles. Controls add 36, for 1,044 total. The default seeded subset has 1,000 distinct people. Use the entire 1,044-profile grid when possible.

## Ready factor grid for onboarding

Use this factor object as a starting point. The clauses describe situations, not demographics. Review it against the product before adding mix assumptions.

```json
{
  "fit": {
    "core": "is exactly the kind of user described in `audience`",
    "adjacent": "has a related need but is not the main intended user",
    "outside": "has no need for a product like the one in `product`"
  },
  "arrival": {
    "ad": "arrived from an ad promising a specific result",
    "search": "searched for an app of this kind",
    "friend": "was told about this app by a friend"
  },
  "motivation": {
    "soon": "needs a result this week",
    "curious": "is curious and has no deadline"
  },
  "patience": {
    "quick": "wants to start in under a minute",
    "guided": "will answer questions to get a better result"
  },
  "privacy": {
    "reluctant": "is reluctant to share personal data or grant permissions",
    "relaxed": "is relaxed about sharing data and granting permissions"
  },
  "price": {
    "tight": "rarely pays for apps",
    "value": "pays when the value is clear",
    "easy": "pays easily"
  },
  "experience": {
    "first": "is trying an app of this kind for the first time",
    "competitor": "uses a competing product today",
    "lapsed": "tried an app of this kind before and quit"
  },
  "moment": {
    "short": "has two minutes",
    "explore": "has time to explore"
  }
}
```

The supplied full grid is `3 x 3 x 2 x 2 x 2 x 3 x 3 x 2 = 1,296`. Set the control to `fit: outside`. Consider making `arrival` and `motivation` target-only so controls are not described as actively seeking a product they do not need. Alternatively, trim options while preserving coherent situations.

The agent must finish the top-level cohort object and supply shares for every option. Do not invent market proportions. State them as assumptions and ask the owner to revise them.

## Output contracts

`cohort` writes the validated specification. `run` saves that specification, the generated people, levels, barriers, context, model, per-variant answers and API accounting.

Each saved person has an `id` plus its factor selections. Each depth answer has normalised level probabilities and expected depth. Sampled people also have a picked `why` barrier.

`report` reconstructs the cohort and checks the saved people against it. It recalculates expected depth from probabilities rather than trusting a saved score.

Multiple answer files can be merged for a sequence. Their cohort, people, levels, barriers, product and audience must match. Variant ids must be unique across files. The order of `--answers` files, then variant order inside each file, defines screen order.
