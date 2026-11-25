---
name: payment-capi-tracking
description: Designs server-side purchase tracking fired from the payment itself (Stripe webhooks, RevenueCat or Adapty for app subscriptions) to the Meta Conversions API and the TikTok Events API, with click id capture (fbclid, fbc, fbp, ttclid), event deduplication against the pixel, value and currency, refunds, and web2app deep link entitlement, plus a QA checklist and test plan. Use when the user asks for "Meta CAPI from Stripe", "server-side tracking", "TikTok Events API setup", "send purchase events from the backend", "fbclid capture", "dedup pixel and CAPI", "RevenueCat to Meta", "web2app attribution", or "event match quality is low".
license: MIT
metadata:
  author: Vlad Yasinski
  version: "1.0"
  site: https://www.roimobi.com
  telegram: https://t.me/ua5er
---

# Payment-triggered CAPI tracking (Meta and TikTok)

Sends the platforms a purchase event only when money really moved, from the system that knows it: the payment provider or the subscription backend.

## When to use

- Ads optimise for a purchase or trial event, but the browser pixel misses many of them (blockers, in-app browsers, redirects).
- Platform purchases and backend payments disagree.
- A web2app funnel pays on the web but the user lives in the app.
- Event match quality is low or optimisation events are too few.

## Inputs to collect first

1. Payment stack: Stripe (Checkout, Payment Links, Billing), RevenueCat, Adapty, or a mix, and where the webhook endpoint can live.
2. Funnel path: ad click, landing page, checkout, app install, login. Where each id is available.
3. Events to send: for example trial start, first payment, renewal, refund. Which one the campaigns optimise for.
4. Current pixel events and their event names, plus any existing server events.
5. Consent setup: what the user agreed to, and the legal basis for sending identifiers.
6. Access to Meta Events Manager and TikTok Events Manager for test events.

## Method

### Step 1. Capture click ids at the first touch

- Read `fbclid` and `ttclid` from the landing URL. Build `fbc` as `fb.1.<timestamp in ms>.<fbclid>`, and keep the `_fbp` and `_fbc` cookies when the pixel sets them. TikTok: keep `ttclid` and the `_ttp` cookie.
- Store them first-party (cookie on your domain and a server record keyed by a visitor id).
- Pass the visitor id into checkout: Stripe `client_reference_id` or metadata, or the RevenueCat and Adapty customer attributes.
- Never rebuild an id you did not receive. If a click id is missing, send the event without it.

### Step 2. Define one event per real payment fact

Map provider events to ad events and send only on confirmed facts:

| Provider fact | Ad event | Notes |
|---|---|---|
| Trial started, subscription created | StartTrial or Subscribe | Only if the trial is a campaign goal |
| First successful charge | Purchase | Value is the amount actually charged |
| Renewal charge | Optional, usually not sent as Purchase | Decide with the team; many accounts keep it internal |
| Refund or chargeback | Do not delete history; record it in your own data and adjust reporting | See Step 5 |

For Stripe use `invoice.paid` or `checkout.session.completed` (check `payment_status`). For app subscriptions use the RevenueCat or Adapty webhook event for initial purchase or trial start.

### Step 3. Build the payload

- Event name, `event_time` (the real time of payment), `action_source` (`website` for web checkout, `app` where it applies), `event_source_url`.
- `value` and `currency`: the real charged amount and its ISO currency code. State whether tax is included and keep it consistent.
- User data: hashed email and phone (normalised, SHA-256), `fbc`, `fbp`, `ttclid`, IP and user agent from the checkout session where you hold them lawfully, `external_id`.
- `event_id`: a stable id built from the payment id (for example the invoice id), identical on pixel and server.

### Step 4. Deduplicate with the pixel

If the pixel also fires Purchase, give both sends the same `event_name` and `event_id`. Check in Events Manager that duplicates are counted once. If you cannot guarantee the same id, send the browser event only for early funnel steps and the server event for purchase.

### Step 5. Handle refunds and retries

- Make the webhook idempotent: store the payment id and skip repeats. Providers retry.
- Queue and retry failed sends with backoff. Log the response.
- Refunds: do not send a fake negative purchase. Keep refunds in your backend metrics and use them when judging campaigns (net revenue, net CAC). Check each platform's current documentation for supported refund handling.

### Step 6. Web2app entitlement

Pass the account or visitor id through the deep link or the install referrer so the app can unlock the paid plan for the same user (RevenueCat or Adapty customer id, or a signed token). Ad events still come from the payment webhook. Never fire a second Purchase from the app for the same payment.

### Step 7. QA and test plan

- Send a test event from staging with the test code in each Events Manager. Confirm name, value, currency, ids, dedup.
- Make one real small payment and trace it: webhook, payload, platform event, campaign report.
- Compare 7 days of backend payments with platform purchases. Large gaps point to missing ids, consent loss or duplicates.
- Track match quality and the share of events with `fbc` or `ttclid` as a health metric.

### Step 8. Monitor after launch

- Alert when the share of server events with a click id drops below your own baseline.
- Alert when backend payments and platform purchases diverge by more than the gap you saw in the first weeks (see spend-anomaly-alerts).
- Re-run the test plan after every checkout, domain, consent banner or app release change.
- Keep a changelog of event names and values, so campaign history stays readable.
- Review token expiry and webhook failure logs weekly.

## Output format

1. Architecture sketch: where ids are captured, stored, and sent.
2. Event map table and the payload spec with field sources.
3. Webhook handler pseudocode with idempotency and retry.
4. QA checklist with expected results.
5. Reconciliation query to compare backend and platform counts.
6. Open questions (consent, tax, trials).

Common failure modes to check:

- Click ids lost on a redirect or an in-app browser hop.
- Checkout opened on a different domain, so first-party cookies are missing.
- Two systems both sending Purchase for one payment.
- Value sent in cents when the platform expects the main unit.
- Time zone or timestamp errors that push events outside the accepted window.

## Guardrails

- Send only events that really happened, with real values and times. Never spoof, inflate, backdate or invent events, and never send events for users who did not pay.
- Respect consent and local privacy law. Send identifiers only where you have the right to.
- Hash personal data as the platform documentation requires. Never log raw emails or card data.
- Follow current Meta and TikTok developer documentation; field names and limits change, so verify before shipping.
- Keep tokens in a secret store, not in code or chat.

## Worked example (illustrative)

Stripe Checkout, web2app. The landing page stores `fbclid` as `fbc` and a visitor id, and passes the id as `client_reference_id`. On `checkout.session.completed` with `payment_status = paid`, the handler records the session id, then sends Purchase to Meta with `event_id = session id`, value 9.99 and currency EUR (example), hashed email and the stored `fbc`. The pixel on the thank-you page uses the same `event_id`. A test event shows one counted purchase, not two. After a week, backend shows 100 payments and Meta shows 91, with the gap traced to checkouts opened without a click id (example numbers).

## Author

Vlad Yasinski, AI growth consultant for app and subscription businesses. Telegram: @ua5er (https://www.roimobi.com/tg?src=skill-payment-capi-tracking). Site: https://www.roimobi.com/?utm_source=github&utm_medium=skill&utm_campaign=user-acquisition-skills
