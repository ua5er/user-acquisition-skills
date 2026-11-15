# Question patterns for marketing gates

Each rule below comes from a weak spot the vendor lists (https://docs.typesafe.ai/model-jaggedness.md) or from its question guidance (https://docs.typesafe.ai/primitives/score.md, https://docs.typesafe.ai/primitives/choice.md). Wording examples are the author's own.

## One judgment per question

Split "is it misleading or off brand" into two Noul questions and combine them in code. An "or" inside a question hides which half fired.

## Write literal, positive statements

The model reads literally and double negatives hurt accuracy.

- Weak: "The ad does not avoid making promises about results."
- Better: "`ad` promises a result."
- If the hazard is the absence of something, ask for the presence and invert in code: "`script` includes the sponsorship disclosure" and treat a low probability as the hazard.
- Name the thing: write "`ad`" and "`brand_rules`" and use those same names as state fields.

## Do not ask it to count or calculate

- Not: "Does the headline have more than 40 characters?" or "Is the discount above 30 percent?" Count and compare in code.
- Not: "Does the ad mention the price twice?" Ask one question per candidate or count in code.
- If a number matters, extract it with a regular expression in code and pass the result, or pass a named bucket.

## Do not ask it to compare dates

Ordering, windows and durations are unreliable. Extract the date parts in code, compare in code. A question such as "the change log says the landing page changed in the last 3 days" is a date question. Ask only "the change log mentions a landing page change" and let code compare the date.

## Keep irrelevant text out of the state

Send only the fields the question needs. Do not send the whole row, the whole page or the whole thread when the last message decides. The scripts send only the fields named in `STATE_FIELDS` or built by `build_state`, so labels and ids in your input file are never sent.

## Treat state text as untrusted

Comments, DMs and landing page text can contain instructions aimed at the model. The model does not treat state as hostile. Mitigations: write explicit criteria, test with adversarial examples from your own data, never let a single probability trigger a write, and keep a person on anything that spends or publishes. Do not put your own secrets or internal rules that you would not show a commenter into the same state as untrusted text.

## Choice: bias, catch-all and companion Noul

- A Choice always picks an option, even when none fits.
- Add a companion Noul in the same request: "`comment` fits one of the listed topics". Read the Choice only when the Noul is high. The vendor's page says this works better than a catch-all option and also advises that a none-of-the-above option can work poorly, so test both on your labels.
- The model leans toward the first option. Test with two or three different option orders on the same labelled items and keep an order where answers agree. `calibrate.py` prints the first-option share of predictions next to the first-option share of labels.
- Keep the option list small, with one-line descriptions that describe situations.

## Score: describe situations, not degrees

- Each level is judged on its own text and does not see its number or neighbours. Write levels as concrete situations, for example "A reader cannot tell what is offered", not "Weak" and "Very weak".
- One dimension per Score. Combine several Scores in code with weights you choose.
- Levels are numbered from 0 in the order you list them. The first entry is level 0.
- Use 3 levels unless you can describe more of them distinctly.

## Noul with criteria

`criteria` can define what true and false mean. Use it to put boundary cases in the question instead of a long instruction.

## Do not ask it to write

It does not generate text. Let an LLM or a person propose copy, and ask Jev to judge it. If you need a rewrite or a reason, use a text model on the review band only.

## Naming and logging

- Question ids are your keys. Keep them stable, lower case, one concept each, because they key the log and the calibration labels.
- Keep all wording and thresholds in one module so a change is a reviewable diff. Log the model id on every row.
