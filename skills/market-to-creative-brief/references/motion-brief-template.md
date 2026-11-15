# Motion brief template (for the motion design or video team)

One brief per concept. The body is shared; three hook variants swap only seconds 0 to 3, so the test reads the hook and nothing else. Every field below is required, and `brief_pack.py` lists a missing one as blocking.

## Fields in `motion_briefs[]`

| Field | What to write |
|---|---|
| `concept_id`, `decision_id`, `concept` | As in the static brief (M1, D4, a short name) |
| `format` | UGC talking head, screen recording, motion graphics, kinetic type, voice-over on b-roll, with the reason in a few words |
| `aspect_ratios` | 9:16 first for reels and stories placements, 4:5 or 1:1 for feeds |
| `durations_s` | Each cut length in seconds, for example `[15, 24]` |
| `hooks` | Exactly three, each with `id` (A, B, C), `spoken` (verbatim, may be empty), `on_screen`, `visual`, `sound` |
| `beats` | The beat sheet: `t` as "start-end" in seconds, `visual`, `spoken`, `on_screen`, `motion`, `sound` |
| `voice_or_captions` | Voice tone, caption style, safe zone |
| `pacing_sound` | Cut rhythm with the market's pacing facts as a range, music energy, sound effects |
| `end_card` | Logo, offer line, price wording, button label |
| `variants` | Hook variants plus any cut-down (for example a 15 s cut of beats 1, 2 and 5) |
| `references` | Ad ids with `take` and `leave`, as in the static brief |
| `avoid`, `claims_notes`, `acceptance` | As in the static brief, plus disclosure of paid partnerships for creators |

## Beat sheet rules (checked by code)

- The first beat starts at 0 and the hook beat ends by 3 s.
- Beats run without gaps: each starts where the previous ended.
- The last beat ends no later than the longest duration.
- The first beat's content is "hook variant": the three hooks fill it.

## Writing rules

- Hooks word for word: the spoken line, the on-screen text and what is seen and heard in seconds 0 to 3. "An engaging opening" is not a hook.
- Use the market's pacing facts (cuts per 10 s, shot length, duration range) as context, not as a target to copy. Say where this concept differs and why.
- On-screen text: a maximum number of words per screen, a caption style and the safe zone for 9:16.
- Motion language: text entrance, easing, transitions, in plain words ("slides up 300 ms, ease-out").
- Product footage: list the app screens or UI states the team must record.
- Sound: voice tone, music energy, the one sound effect that carries the hook if any.
- Creators: describe what they do with the product; never script a result they "got". Paid partnership disclosure follows the platform's rules.
- References are patterns, not copies, as in the static brief.

## How it renders

`brief_pack.py` renders the format block, a hook table (variant, spoken, on screen, visual, sound), the beat table, the end card, variants, references, avoid list, claim notes and acceptance list, and names each hook in the test plan as `PROJECT | TEST | Video | M1 hook A | src: market v06+v12`.
