# User acquisition skills by Vlad Yasinski: agent skills for app and subscription growth

User Acquisition Skills is a set of eleven open agent skills for paid user acquisition, paywalls, onboarding funnels, unit economics and attribution in app and subscription businesses. They are written by [Vlad Yasinski](https://www.roimobi.com), an AI growth consultant in Warsaw with 10+ years of paid acquisition experience, and work in Claude Code, Codex, Cursor and other agents that read SKILL.md files.

## Install

Requires Node.js. Uses the open [`skills` CLI](https://github.com/vercel-labs/skills).

```bash
# Install all skills from this repository (you choose agents interactively)
npx skills add ua5er/user-acquisition-skills

# List what is inside without installing
npx skills add ua5er/user-acquisition-skills --list

# Install one skill into Claude Code, globally, without prompts
npx skills add ua5er/user-acquisition-skills --skill paywall-audit -a claude-code -g -y

# Install everything for every detected agent
npx skills add ua5er/user-acquisition-skills --all
```

Then ask your agent in plain words, for example: "Audit this paywall", "Write kill and scale rules for our Meta campaigns", or "Check why Meta and Stripe disagree on purchases".

## Skills

| Skill | What it does |
|---|---|
| [`ua-kill-scale-rules`](skills/ua-kill-scale-rules/SKILL.md) | Writes kill, scale and budget pacing rules for Meta and TikTok from your CAC target, then applies them to a campaign export. |
| [`paywall-audit`](skills/paywall-audit/SKILL.md) | Audits a subscription paywall or checkout: message match, proof, price display, disclosure, CTA, with a ranked change list and test queue. Adapted in part from two MIT skills (see Credits). |
| [`onboarding-web2app-funnel`](skills/onboarding-web2app-funnel/SKILL.md) | Produces distinct onboarding or web-to-app concepts with hypotheses, measurement plan and test order. |
| [`unit-economics-check`](skills/unit-economics-check/SKILL.md) | Checks CAC, cohort LTV and payback from your own data and sets a safe CAC ceiling. |
| [`attribution-sanity-check`](skills/attribution-sanity-check/SKILL.md) | Reconciles ad platform, MMP, SKAN and backend payments and lists the fixes that matter. |
| [`creative-testing-research`](skills/creative-testing-research/SKILL.md) | Plans a creative testing cycle and researches competitors from public ad libraries only. |
| [`weekly-ua-report`](skills/weekly-ua-report/SKILL.md) | Builds a one-page weekly acquisition report that ends in decisions. |
| [`ai-marketing-system-audit`](skills/ai-marketing-system-audit/SKILL.md) | Maps a marketing system as a loop (acquire, convert, measure, automate, intelligence, decide) and ranks the gaps. |
| [`meta-ads-learning-audit`](skills/meta-ads-learning-audit/SKILL.md) | Audits a Meta ad account stuck in "Learning limited": event volume against the budget learning needs, split signal, CPM of small test ad sets, funnel and CAPI, and a post-mortem table of past campaigns. Works from exports and screenshots, no API token. |
| [`meta-ads-launch-planner`](skills/meta-ads-launch-planner/SKILL.md) | Plans a Meta sales launch that exits learning: budget from target CPA x 50 events a week (with `budget.py`), one broad ad set on CBO, day-by-day decision rules, automated stop and restart rules, scaling schedule, relaunch playbook and a plan document for management. |
| [`meta-creative-testing`](skills/meta-creative-testing/SKILL.md) | Designs creative testing for Meta after Andromeda: which past ads to relaunch and why, three test structures with the cost of an answer, winner, kill and fatigue criteria, a weekly creative flow and a brief template for designers and UGC creators. |

## How these were used

Two design explorations for a subscription AI photo app (app name withheld) used these skills. Both are written up with the method, the versions produced and what is still unmeasured:

- [Onboarding redesign: five concepts](examples/onboarding-redesign-subscription-photo-app.md)
- [Paywall redesign: versions V1 to V6 and hero variants](examples/paywall-redesign-subscription-photo-app.md)

These are design cases. They do not contain measured conversion results.

## Principles

- Your data first. The skills do not insert industry benchmarks. Any number in an example is labelled as an example.
- Public data only for competitor research.
- Decisions, not dashboards: every skill ends in an output someone can act on.
- Honest offers: no fake urgency, hidden fees or placeholder proof.

## About the author

Vlad Yasinski is a performance marketer and growth consultant based in Warsaw, Poland (remote; English, Polish, Russian), with 10+ years of paid acquisition experience since 2015. He took two apps to Top-1 in their US App Store categories, managed Facebook and TikTok budgets of up to $1.5M per month at peak, built web funnels end to end (landing pages, Stripe checkout, Meta Pixel and Conversions API, BI and FunnelFox), and rebuilt an unprofitable app portfolio to positive unit economics for a client under NDA. He builds the analytics, funnels and automation around paid acquisition for app and subscription businesses.

- Site: [roimobi.com](https://www.roimobi.com)
- Background and experience: [roimobi.com/about](https://www.roimobi.com/about)
- LinkedIn: [linkedin.com/in/vlad-yasinski-ua5er](https://www.linkedin.com/in/vlad-yasinski-ua5er/)
- Want a review of your own system? [Request an AI Marketing and Growth Audit](https://www.roimobi.com/contact?intent=audit)

## Credits and licence

This repository is released under the [MIT licence](LICENSE).

`paywall-audit` is adapted in part from:

- `paywalls` in [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), MIT, copyright 2025 Corey Haines.
- `paywall-optimization` in [appeeky/aso-skills](https://github.com/appeeky/aso-skills), MIT, copyright 2026 Erencan.

Their licence texts are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The other seven skills are original. Motion guidance referenced in the paywall case comes from [emilkowalski/skills](https://github.com/emilkowalski/skills) and [ibelick/ui-skills](https://github.com/ibelick/ui-skills), both MIT, and is not included here.

Product and platform names (Meta, TikTok, Stripe, AppsFlyer, Adjust and others) belong to their owners and are used only to describe what the skills work with. This project is not affiliated with or endorsed by them.
