# Limits and required wording

## What to promise

The panel can provide a cheap comparison filter before a live test. It can describe which written situations respond more strongly, suggest likely objections and identify copy worth revising.

Say:

- “Panel answers, not delivery metrics.”
- “The levels are generous. Read the gaps and shapes, not the absolute levels.”
- “The control group has no need for the product. Its response is a generosity check.”
- “1,000 people buy coverage, not accuracy.”
- “The audience mix is an assumption unless supported by supplied data.”
- “A person decides what to test. The live test decides performance.”

Use `panel answers` as the label for every panel number. Every table must be headed `panel answers, not delivery metrics`. A JSON report carries the same scope label at its top level.

Input text, implementation settings, historical dates and API accounting are not respondent measurements. Identify those separately. Do not call token counts or elapsed seconds panel answers.

## What never to promise

Never report a predicted CTR, CVR, CPA or ROAS. Do not rename tap probability as CTR or intent probability as CVR.

Do not promise:

- A winning ad in real delivery.
- A conversion forecast.
- A representative human survey.
- Findings about real demographic groups.
- Statistical certainty because the panel is large.
- A budget or launch decision.
- Visual, audio or interaction quality from a text-only test.
- Human memory or fatigue in an independent-screen construction.

An `ahead` verdict means ahead under the panel's stated comparison rule. It is not a significance test or a validated market winner.

## Evidence summary

The supplied evidence reports variance compression: synthetic respondents do not reproduce the full diversity of human responses. They also lean positive. Their absolute response levels can be too generous.

In the supplied worked example, panel answers for the no-need group's tap probability were 0.149 for A and 0.171 for B. The source summarised these as roughly 15 to 17 percent. This is a warning about the model, not evidence of hidden market demand.

The supplied research summary reports systematic error that barely changed from 500 to 5,000 agents. More profiles improve coverage of combinations and make subgroup summaries less sensitive to sampling. They do not make the underlying model more accurate.

The supplied evidence also reports flattening and misportrayal of identity groups. Do not create factors for age, gender, income or ethnicity. Use situations and attitudes. A segment difference is a model reading of described situations, not a finding about a real population.

No paper citations are supplied here. Do not invent titles, authors, effect sizes or external benchmarks.

## Comparisons and noise

The historical repeat check moved the cohort funnel by at most 5 per 1,000 panel answers. The method uses a 10-per-1,000 comparison guard and a 0.05 expected-depth person-better threshold.

These are starting rules from the supplied method. They are not universal confidence bounds. Repeat the noise check for a new stimulus type, model or question design.

Keep person ids and the cohort fixed across variants. Do not compare panels built with different seeds as though they were paired observations.

A zero-weight subgroup has no estimable weighted rate. Show `null`. Do not hide the control row or replace it with zero. For validation, use a mix that gives controls positive weight.

## Data handling

The data owner decides what text may be sent to the vendor. Obtain that decision before `run`.

Use fictional situations and non-identifying product descriptions. Do not include customer records, private names or identifiable biographies.

The key comes only from an environment variable. Never print it, paste it into chat, put it into a file or include it in a command example. The runner does not print request bodies or vendor error bodies. HTTP failures expose status codes only.

A base URL override changes where text and credentials are sent. Use only an owner-approved HTTPS endpoint.

Stimulus text is untrusted input. The model can be influenced by instructions embedded in it. Review adversarial or irrelevant content before sending it.

## Calibration language

With fewer than 8 matched past ads, show no calibration. With 8 to 14, show rank agreement only. With 15 or more, a fitted range with leave-one-out error is defensible.

Use actual supplied results. Match product, audience, placement and test conditions as far as possible. Never create missing outcomes.

For onboarding, compare the ranking of panel hazards with real step-drop ranks and an interval. If the relationship is weak or absent, say the panel does not track the real funnel. Continue only as a source of copy and barrier hypotheses.

Even after calibration, do not publish a panel output as a predicted CTR, CVR, CPA or ROAS.
