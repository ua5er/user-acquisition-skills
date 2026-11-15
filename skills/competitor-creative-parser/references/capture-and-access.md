# Capture: record format and data access

## One record per creative: `creatives.jsonl`

One JSON object per line. Code reads these fields; add your own fields freely, they are ignored.

| Field | Required | Meaning |
|---|---|---|
| `creative_id` | yes | Your id, short and stable (`s01`, `v07`, or the library ad id). Used in every later file and in the briefs. |
| `platform` | yes | `meta`, `tiktok`, `google`, `other`. |
| `advertiser` | yes | Advertiser label as shown in the library. Shares by advertiser are computed from it. |
| `ad_ref` | yes | Library ad id or link, so a person can open the original. |
| `first_seen` | yes | ISO date the library shows as start, or the first date you saw it. |
| `last_seen` | yes | ISO date the library shows as last shown, or the capture date if still active. |
| `format` | yes | `static` or `video`. Carousels: capture each card as a static, note the card number in `creative_id`. |
| `media` | yes | Local path or link to the file or screenshot you looked at. |
| `landing_url` | no | Where the ad sends people. |
| `capture_date` | yes | ISO date of capture. |
| `source` | yes | `meta-ad-library-api`, `manual-browse`, `user-file`, `user-link`, and so on. |

Runtime in days is computed by code as `last_seen - first_seen + 1`. It is a weak durability signal: an ad can run long because nobody switched it off.

## Where records may come from

Use public ad libraries through their official routes, or manual browsing in the user's own browser, plus files, screenshots, links and text the user supplies. Follow each library's terms. This skill bundles no scraper and no login automation, and it never asks for a password.

| Source | Official route | What it covers and its limits |
|---|---|---|
| Meta Ad Library | Graph API `ads_archive` with an access token | All ad types, but an ad that reached no EU location is returned only if it is political or about a social issue, so US-only commercial ads are not in the API. Search terms up to 100 characters, up to 10 page ids per call, a rate limit exists with no published numbers. Outside EU reach, browse the website yourself and save screenshots. |
| TikTok ad library | Commercial Content API, by application (a developer account and a reply in about two working days) | EU only in the current phase. Ad data stays available until one year after the ad was last shown. |
| TikTok Creative Center | No official API found | Browse it yourself; supply files or links. |
| Google Ads Transparency Center | No website API found; a BigQuery public dataset `google_ads_transparency_center` exists | The dataset is reported by a community answer to cover the EEA and Turkey and to lag the website; check Google's own dataset page. Otherwise browse and supply files. |

Facts above were checked on 2026-11-15. Library terms change: read the current terms page before a run. If a library blocks a route, use the user's own browsing and files instead.

## What an ad library can and cannot tell you

- It shows what runs, where, since when and for how long.
- It does not show spend, results, targeting quality or whether the advertiser is happy with the ad. Never write that a competitor's ad "works", "wins" or "is profitable".
- Many active ads from one advertiser can be one concept in many sizes. The snapshot marks a value as dominated when one advertiser supplies most of its creatives.

## Media handling

- Keep the media files local. Claude looks at them and writes the description; Jev receives only that text.
- Do not save personal data that appears in an ad (for example a commenter's name in a screenshot). Crop or skip it.
- For video, a local speech-to-text run gives the transcript (for example whisper.cpp). Cut times can come from Claude's frame notes or from a local scene detection run such as `ffmpeg -i ad.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null -` (read the `pts_time` values). Both stay on the user's machine.

## Folder per run

```
parsed-market/YYYY-MM-DD-<market>/
  creatives.jsonl          capture records
  media/                   files and screenshots (local only)
  descriptions.jsonl       Claude's descriptions (the state Jev reads)
  tags-static.jsonl        tag_creatives.py output
  tags-video.jsonl
  review-queue-static.csv  rows for a person
  review-queue-video.csv
  run-static.json          requests, tokens, cost
  run-video.json
  order-check-*.json       optional first-option bias test
  snapshot.json            market_snapshot.py output for code and the brief skill
  snapshot.md              one page for a person
```
