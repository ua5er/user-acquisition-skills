# Question design for the panel

Each request is one concept (or one video hook) and one profile. The state holds two named objects, `buyer` and `ad`, and nothing else. All wording lives in `scripts/questions_static.py` and `scripts/questions_video.py`, so a change is a reviewable diff.

## The set

| Id | Type | Asks | Code uses it for |
|---|---|---|---|
| `action` | Choice: scroll, stop, click | What this buyer most likely does on seeing the ad | Stop-or-click mass (engage) and click mass per item; the heatmap |
| `hook_about_problem` | yes/no | The headline (static) or the first 3 seconds (video) is about this buyer's problem or goal | A note when under half of the profiles say yes |
| `offer_clear` | yes/no | Static: what is offered and on what terms is clear from the headline, image and button. Video: the product is clear from the first 3 seconds | A note when under half say yes |
| `distrust_claim` | yes/no | This buyer would doubt or distrust a claim in the ad | Blocks a go when more than 25% of profiles say yes |
| `fit` | Score, 4 levels | How well the ad speaks to the buyer's situation and goal | Mean fit gates go and drop |

## Why it is built this way

- One judgment per question. "Would stop and trust it" is two questions.
- The Choice has three options that are real, exclusive actions. There is no "other": every person does one of the three. The option order is rotated per pair to counter first-option bias, and `--order-check N` asks the Choice again in reversed order for N pairs and reports agreement.
- Stop and click both count as "the ad held the person". Uncertainty is read on that hold-or-scroll split (stop-or-click mass over 0.35 and under 0.70), not on the top of three options, which spreads naturally between stop and click.
- The yes/no questions ask for the presence of something, never its absence (no negations).
- Score levels describe situations, not degrees ("speaks to the situation but misses the main objection").
- No counting, prices or dates are asked. Code counts.
- The video track asks about each hook variant separately, with the rest of the beat sheet as context, because the hook is the variable the team will test.
- Labels, sources and notes stay out of the state; only the four profile fields and the ad fields go to Jev.

## Changing the set

- Add a question only when code will use the answer. A question nobody reads is spend and noise.
- Rewrite a question whose answers sit in the review band for most pairs: it does not discriminate on your concepts. In the fictional example, `offer_clear` and `distrust_claim` did this: their means stayed near 0.2 to 0.6 and almost no pair reached 0.70.
- Keep the Choice options fixed between runs you want to compare. A new option set is a new panel.
- Pin the model id in the module (`jev-1.14.0` in the example) so answers do not move under you.
