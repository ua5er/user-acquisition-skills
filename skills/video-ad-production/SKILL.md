---
name: video-ad-production
description: Production pipeline for short video ads (UGC-style, motion graphics, explainers): brief, hook-first script with three hook variants, scene storyboard, voice-over with text to speech, music and sound effects mix rules, scene assembly as an HTML or motion composition rendered to MP4, optional AI live shots with a dry-run cost quote, 9:16 and 4:5 versions, burned-in captions, a frame-exact shot library for reuse, QA and a cost line. Use when the user asks for "video ad pipeline", "make short video ads", "UGC style ad script", "hook variants for video", "AI voiceover for ads", "captions on video ads", "render ad video from code", "video creative QA", or "cost of a video ad batch".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Video ad production pipeline

Turns a brief into short vertical video ads with a repeatable build, so new hooks and versions are cheap exports instead of new projects.

## When to use

- You need 5 to 20 short videos for a test and editing by hand is the bottleneck.
- Hooks are the main variable and you want several for one body.
- Costs from AI video tools are unpredictable.

## Inputs to collect first

1. Product facts file: real features, prices, trial terms, proof. Claims come only from here.
2. Audience, angle and the one promise of the video.
3. Format: UGC-style, motion, explainer, or a mix. Length target (often 15 to 30 seconds, example).
4. Assets: screen recordings, logo, fonts, colours, any real footage you own the rights to.
5. Voice choice, music source with a licence, and platform specs.
6. Budget for generation and who approves.

## Method

### Step 1. Brief

One page: goal, audience, promise, proof, offer, call to action, banned claims. Each line cites the facts file.

### Step 2. Hook-first script

- Write the first 3 seconds first. Produce three hook variants for the same body: a question, a bold statement, a visual surprise (example set).
- Then the body: problem, proof, how it works, offer, call to action.
- Spoken lines short, one idea per sentence. Keep a word count that fits the length.

### Step 3. Storyboard by scene

Table per scene: number, seconds, visual, on-screen text, voice-over line, sound. Mark which scenes are reusable across versions and which are hook-only.

### Step 4. Voice-over (TTS)

- Generate each line separately so a changed line is a small fix, not a full redo.
- Listen for stress, numbers and brand names. Correct by respelling.
- Trim silence at line ends. Keep gaps consistent.

### Step 5. Music and sound effects

- Use one continuous music excerpt for the whole video. Do not stitch many clips together.
- Duck the music gently under the voice (a small, smooth dip, not a gate), and bring it back between lines.
- Keep effects sparse and tied to a visual action. Check the final mix on phone speakers and with a headset.
- Use only licensed or self-produced audio.

### Step 6. Assemble as a composition

- Build scenes as an HTML or motion composition with live text layers, timing in one config, and brand tokens.
- Render to MP4 from code, so every version is a re-render with changed parameters.
- Optional live shots: generate them with an AI video model only for scenes that need them. Run a dry run first that returns the planned clips, length and cost, and get approval before spending.

### Step 7. Versions and captions

- Render 9:16 and 4:5 from the same composition, with safe zones for platform UI.
- Burn in captions from the voice-over script, large enough to read on a phone, high contrast, timed to the audio.
- Swap only the hook scene to make hook variants.

### Step 8. Shot library

Cut each render into frame-exact shots (with and without text) and file them with a catalogue: scene, source, in and out frames, tags. Reuse shots in later videos instead of regenerating them.

### Step 9. QA and cost

- First 3 seconds: does the hook land with sound off?
- Text legibility, caption sync, nothing hidden by UI zones.
- Audio: loudness steady, music under voice, no clipping.
- Claims traced to the facts file. Policy check for health, money, before and after, and likeness rights.
- Cost line: TTS, any live shots, renders, total against the quote.

Per-video record to keep in a sheet:

- Video name, hook variant, ratio and length.
- Script version and source fact row for each claim.
- Voice, music source and licence.
- Live shots used, with the quote and the actual cost.
- Launch date, test cell and the result when it arrives.

## Output format

1. Brief and script with three hooks.
2. Storyboard table.
3. Audio files and mix notes.
4. Composition project and MP4 versions by ratio.
5. Shot library catalogue.
6. QA checklist and the cost line.

Reuse rules: a hook can be swapped without touching the body, and a body can carry many hooks. Keep scenes numbered the same in every version so shots and captions map one to one.

## Guardrails

- Claims only from the facts file. No fake testimonials, fake UI or invented results.
- Do not clone a real person's voice or face without written rights. Label synthetic voices where platform rules ask.
- Quote before paid generation and stop at the cap.
- Follow platform ad policies and music licences.
- A person approves each video before launch.

## Worked example (illustrative numbers)

Example: 20 second video, 3 hooks, 1 body, 2 ratios. TTS cost 0.30 (example). One live shot of 4 seconds planned: dry run quotes 1.20 (example), approved. Renders happen locally at no extra cost. Output: 3 hooks x 2 ratios = 6 MP4 files, all from one composition. QA finds the caption overlaps the UI zone in 4:5, the margin is changed in the config and all files re-render. Total cost line: 1.50 against a quote of 1.60.

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-video-ad-production). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
