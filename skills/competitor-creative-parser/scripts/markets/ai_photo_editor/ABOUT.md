# Market taxonomy: AI photo editor apps (worked example)

Question sets for one real market, as a worked example of `references/market-taxonomy.md`. They are a starting point for a similar market, not a standard.

- Drafted by Claude from a first read of 54 real ads (20 static, 34 video) in the public Meta Ad Library, category AI photo editor apps, US, captured on 2026-11-15. The files name no advertiser.
- Taxonomy versions: `ai-photo-static-1.1` and `ai-photo-video-1.1` (the `TAXONOMY_VERSION` constant in each file, written into every tag record). The 1.0 drafts were rewritten after the first pilot, see the reference.
- Static dimensions: use case, layout, headline type, angle, offer type, plus eight yes/no flags and a headline specificity score. Video dimensions: use case, hook type, proof device, angle, video format, offer type, plus nine yes/no flags and a hook specificity score.
- Built for an ad library capture: there is no audio, so no question reads a transcript or a spoken hook. Video questions read `first_3s`, `on_screen_text`, `format_notes` and the ad text.
- The options come from what 54 ads happened to run. Re-read after the sample grows and bump the version. Thresholds are the vendor's starting values and were not calibrated on labelled ads.

## Use

From the `scripts` folder, tag with the market files and the confirm pass, then build the snapshot with the same files:

```
python3 tag_creatives.py descriptions.jsonl --track static --questions markets/ai_photo_editor/questions_static.py \
    --confirm-pass --data-handling-confirmed --out-dir run
python3 tag_creatives.py descriptions.jsonl --track video --questions markets/ai_photo_editor/questions_video.py \
    --confirm-pass --data-handling-confirmed --out-dir run
python3 market_snapshot.py --creatives creatives.jsonl --tags run/tags-static.jsonl run/tags-video.jsonl \
    --questions-static markets/ai_photo_editor/questions_static.py \
    --questions-video markets/ai_photo_editor/questions_video.py --out-dir run --market "AI photo editor apps, US"
```

Run `--dry-run` first, then a pilot of about 30 ads, and read the unresolved count per dimension before the full run. For another market, copy the folder, rewrite the options and bump `TAXONOMY_VERSION`.
