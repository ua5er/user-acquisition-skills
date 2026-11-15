# Jev API notes

Every fact below was read from the vendor's own pages on 2026-11-15, with the URL next to it. A live check on 2026-11-15 (direct endpoint, jev-1.14.0, Noul, Score and Choice questions on illustrative ad texts) returned the response shapes described here; the gateway route, the long-context header and error paths were not exercised live. The pages were read through a fetch tool that summarises, so confirm anything you build on against the OpenAPI spec at https://api.typesafe.ai/openapi.json. Vendor pages change; check the date.

For API craft (state design, question wording, testing practice) read the vendor's own MIT-licensed skill instead of relying on this file: https://github.com/typesafe-ai/skills (skills/typesafe-ai/SKILL.md). Its topics: judgments versus decisions, designing state, writing questions, composing requests, reading answers, testing with the live API, cookbooks. This repo does not copy its text.

## Request

Source: https://docs.typesafe.ai/api/system-one.md

- `POST https://api.typesafe.ai/v1/systemone`
- Header `Authorization: Bearer <API_KEY>`. Keys come from the vendor console (https://docs.typesafe.ai/introduction/quickstart.md).
- Body is JSON with:
  - `model` (string, required): a model id or alias.
  - `state` (string, object or array, required): what every question refers to.
  - `questions` (object, required, at least one): keys are names you choose.
  - `assets` (object, optional): images. Needs the header `TypeSafe-Danger-Zone-Images: true`. This skill does not use images.
- Question types used here:
  - `noul`: `type`, optional `instructions`, optional `criteria` with the optional string keys `true` and `false`.
  - `choice`: `type`, `criteria` (required, a map of option name to description, 1 to 255 options on the API page and on https://docs.typesafe.ai/primitives/choice.md; the overview page https://docs.typesafe.ai/primitives.md states no maximum).
  - `score`: `type`, `criteria` (required, an ordered list of levels). The API page says 1 to 10 levels; https://docs.typesafe.ai/primitives/score.md says at least two and up to 10. The scripts enforce 2 to 10.
- Several questions can go in one request. They are answered in parallel against the same state and cannot see each other.
- `box` (locate an object in an image) exists and is not used here.

## Response

Source: https://docs.typesafe.ai/api/system-one.md and https://docs.typesafe.ai/primitives/score.md

- `model`: the versioned id that answered (can differ from the alias you sent).
- `answers`: keyed by your question names, each with a `type` equal to the question's type.
  - noul: `noul`, a number from 0 to 1, the probability of yes. No `confidence` field.
  - choice: `choice` (string), `confidence` (0 to 1), `probabilities` (option to number).
  - score: `score` (probability weighted, can be fractional), `confidence`, `legend`, `probabilities`. Levels are numbered from 0 (position in `criteria`). In the JSON, `legend` and `probabilities` are keyed by the level number as a string ("0", "1", "2"). The Python SDK uses integer keys.
- `usage`: `input_tokens` (billed) and `output_tokens` (currently free).
- The documented response schema has no request id field. The scripts therefore log item id and question id, not a vendor request id.
- Error bodies: 400 has `detail` (string or object); 422 has `detail` as a list of validation errors.

## Models, limits, price

Sources: https://docs.typesafe.ai/models.md, https://docs.typesafe.ai/api/errors.md

- Versioned ids: `jev-1.14.0` (from 2026-10-14) and `jev-1.13.0`. Aliases `jev-latest` and `jev-preview` both pointed to `jev-1.14.0`. The skill pins a versioned id so results do not move under you.
- Context: about 64k tokens for state plus all questions in a request, 32k for state plus one question. The header `TypeSafe-Danger-Zone-Long-Context: true` raises both to 262k at the same per-token price, slower and less accurate. No separate limit on the number of questions.
- Request rules: body up to 32 MiB (413 above), UTF-8 JSON, nesting up to 64 levels, gzip or zstd allowed.
- Status codes: 400, 401, 413, 415, 422, 429 (rate limit), 529 (overloaded). Retry 429 and 529 with exponential backoff.
- Rate limits are per organisation in tokens per second and requests per second. The numbers are not published; they are in the vendor console. Higher limits by request.
- Price: $42 per billion input tokens ($0.042 per million). Output tokens are free. Same listed price for both versions. Free tier or credits: none mentioned on the pages read.

## Confidence and thresholds

Source: https://docs.typesafe.ai/confidence.md

- Confidence is computed from the probability spread: 1 when all probability is on one outcome, 0 when spread evenly. For noul the docs give |2p - 1|. For choice with n options and top probability p: (p - 1/n) / (1 - 1/n). For a fixed option count it adds no independent evidence beyond the top probability.
- Starting values for noul: 0.7 for yes and 0.3 for no, with the band in between handled as its own outcome. Scale thresholds to risk. The docs call every number a starting point to test on your own data.

Source: https://docs.typesafe.ai/cookbooks/llm_guardrails.md

- Guardrails cookbook starting values: strict review 0.35, action 0.70, severity block 2.0; permissive review 0.70, action 0.85, severity block 2.0. Run on 16 items on 2026-10-31; the vendor calls it a demonstration, not a benchmark.

## Known weak spots

Source: https://docs.typesafe.ai/model-jaggedness.md

Reads questions literally; counts unreliably; weak on numeric representations and arithmetic; unreliable on date and time comparison; double negatives and multi-hop indirection lower accuracy; irrelevant detail in a large state lowers accuracy; injected or misleading content in the state can steer answers; contradictory criteria confuse it; leans toward the first Choice option; does not generate text. `question-patterns.md` turns each into a rule.

## Access routes

1. Direct vendor API, as above. Key variable used by the scripts: `TYPESAFE_API_KEY`. Signup status could not be verified (the vendor page says early access and does not say whether signups are open); check at signup time.
2. Vercel AI Gateway, TypeSafe-compatible API. Source: https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe (page dated 2026-10-05).
   - Base URL `https://ai-gateway.vercel.sh/typesafe`, endpoint `POST /typesafe/v1/systemone`, model `typesafe-ai/jev`, same request and response shapes, key is an AI Gateway key sent as `Authorization: Bearer`.
   - Use with the script: `--base-url https://ai-gateway.vercel.sh/typesafe --key-env AI_GATEWAY_API_KEY --model typesafe-ai/jev`.
   - Error bodies differ: validation and authentication errors use `message` and `error_type`; other errors use an `error` object with `message` and `type`. The scripts do not depend on the error body.
   - The response adds `provider_metadata.gateway` with cost fields. The scripts ignore it; use it for billing checks.
   - Price through the gateway: not stated on the page read. Do not assume it equals the direct price.
   - Zero data retention and no-training options exist on the gateway; the page shows `providerOptions.gateway.zeroDataRetention` for the Decisions API. The scripts do not set provider options.
   - Vercel also documents a separate `/v1/decisions` endpoint in a different request format (https://vercel.com/docs/ai-gateway/modalities/decision). The scripts do not use it.
3. Vendor SDKs (Python `typesafe-sdk`, JavaScript `@typesafe-ai/sdk`). Not used here: the scripts use the standard library only.

## Data handling

Source: https://docs.typesafe.ai/legal.md

The Privacy Policy states a commitment not to train models on user data. Zero data retention is offered to enterprise customers on request. A Data Processing Agreement exists. Retention periods are not stated on the page read. The pages say nothing specific about ad account or customer data. The data owner decides what may be sent (see SKILL.md hard rules).

## Could not be verified

- Anything about live responses: no call was made. Field names and shapes come from the documentation above.
- Rate limit numbers (console only).
- Whether signups are open.
- Whether Retry-After is sent by the direct API: the errors page does not mention it, the models page says the SDKs follow `retry-after` when present. The script honours a numeric Retry-After if one arrives.
- Gateway pricing for Jev and gateway behaviour under this script's retry logic.
- Whether a request can carry an array of independent items as one state to save requests. The docs describe one state per request; the script sends one request per item.
- Independent accuracy and calibration: published third-party tests exist and disagree on details; none is reproduced here. Measure on your own labelled items with `calibrate.py`.
