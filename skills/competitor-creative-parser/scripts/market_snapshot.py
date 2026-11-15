#!/usr/bin/env python3
"""Aggregate tagged creatives into a market snapshot, per track.

Reads creatives.jsonl (capture records) and tags-static.jsonl and or
tags-video.jsonl (from tag_creatives.py). Writes snapshot.json (for code and
for market-to-creative-brief) and snapshot.md (one page for a person).

Per track it reports, for every tagged dimension: creatives per value, share
of the track, advertisers using it and their share, how much one advertiser
dominates the value, unresolved items, then crowded values, gaps, flags,
score averages, code facts (pacing, words, price shown) and the longest
running creatives as a weak durability signal.

Guards: below --min-n creatives (default 20) in a track nothing is ranked,
crowded and gap labels are marked low sample, and the durability list is
withheld. An ad library shows what runs and for how long, never spend or
results: nothing here is a performance claim.

Standard library only, no network.

  python3 market_snapshot.py --creatives creatives.jsonl --tags out/tags-static.jsonl out/tags-video.jsonl \\
      --out-dir out --market "sleep apps, US English (fictional)"

With a market taxonomy, point the snapshot at the same question files the tags were made with:

  python3 market_snapshot.py ... --questions-static markets/ai_photo_editor/questions_static.py \\
      --questions-video markets/ai_photo_editor/questions_video.py
"""
import argparse
import datetime as dt
import json
import os
import runpy
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTION_FILES = {"static": os.path.join(HERE, "questions_static.py"),
                  "video": os.path.join(HERE, "questions_video.py")}
CROWDED_SHARE = 0.30        # value used by at least this share of the track's creatives
CROWDED_ADV_SHARE = 0.50    # and by at least this share of its advertisers
DOMINATED_SHARE = 0.50      # one advertiser supplies more than this share of a value's creatives


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def runtime_days(cap):
    try:
        first = dt.date.fromisoformat(cap["first_seen"])
        last = dt.date.fromisoformat(cap.get("last_seen") or cap.get("capture_date"))
    except (KeyError, TypeError, ValueError):
        return None
    return (last - first).days + 1


def pct(x):
    return "%d%%" % round(100 * x)


def track_snapshot(track, recs, caps, qs, min_n):
    ok = [r for r in recs if r.get("status") == "ok"]
    errors = [r["creative_id"] for r in recs if r.get("status") != "ok"]
    n = len(ok)
    low = n < min_n
    advs = sorted({caps.get(r["creative_id"], {}).get("advertiser", "(unknown)") for r in ok})
    n_adv = len(advs)
    per_adv = {a: sum(1 for r in ok if caps.get(r["creative_id"], {}).get("advertiser", "(unknown)") == a)
               for a in advs}
    dims = {}
    crowded, gaps, rare = [], [], []
    for dim in qs["CHOICE_COMPANION"]:
        options = list(qs["QUESTIONS"][dim]["criteria"])
        rows = []
        unresolved = [r["creative_id"] for r in ok if r["tags"][dim]["status"] != "tagged"]
        for opt in options:
            ids = [r["creative_id"] for r in ok if r["tags"][dim]["status"] == "tagged"
                   and r["tags"][dim]["value"] == opt]
            adv_counts = {}
            for cid in ids:
                a = caps.get(cid, {}).get("advertiser", "(unknown)")
                adv_counts[a] = adv_counts.get(a, 0) + 1
            top_adv_share = max(adv_counts.values()) / len(ids) if ids else 0.0
            row = {"value": opt, "creatives": len(ids), "share": round(len(ids) / n, 3) if n else 0.0,
                   "advertisers": len(adv_counts), "advertiser_share": round(len(adv_counts) / n_adv, 3) if n_adv else 0.0,
                   "dominated_by_one_advertiser": bool(ids) and len(adv_counts) > 0 and top_adv_share > DOMINATED_SHARE
                   and len(ids) >= 2,
                   "ids": ids}
            rows.append(row)
            if opt == "other":
                continue
            if row["share"] >= CROWDED_SHARE and row["advertiser_share"] >= CROWDED_ADV_SHARE:
                crowded.append({"dimension": dim, "value": opt, "share": row["share"],
                                "advertiser_share": row["advertiser_share"], "low_sample": low})
            elif row["creatives"] == 0:
                # A gap is only firm when few items of this dimension are unresolved:
                # an unresolved creative could still carry the value.
                firm = n > 0 and len(unresolved) / n <= 0.25
                gaps.append({"dimension": dim, "value": opt, "low_sample": low, "unresolved": len(unresolved),
                             "firm": firm})
            elif row["advertisers"] == 1:
                rare.append({"dimension": dim, "value": opt, "creatives": row["creatives"], "low_sample": low})
        if not low:
            rows.sort(key=lambda r: (-r["creatives"], r["value"]))
        dims[dim] = {"rows": rows, "unresolved": len(unresolved), "unresolved_ids": unresolved,
                     "ordered_by": "taxonomy order (low sample, not ranked)" if low else "creatives, descending"}
    flags = {}
    for f in qs["FLAGS"]:
        yes = [r["creative_id"] for r in ok if r["flags"][f]["value"] == "yes"]
        rev = [r["creative_id"] for r in ok if r["flags"][f]["value"] == "review"]
        flags[f] = {"yes": len(yes), "share": round(len(yes) / n, 3) if n else 0.0, "review": len(rev),
                    "yes_ids": yes, "review_ids": rev}
    scores = {}
    for s in qs["SCORES"]:
        vals = [r["scores"][s]["score"] for r in ok]
        levels = qs["QUESTIONS"][s]["criteria"]
        scores[s] = {"mean": round(statistics.mean(vals), 2) if vals else None,
                     "max_level": len(levels) - 1,
                     "levels": {str(i): sum(1 for r in ok if r["scores"][s]["level"] == i) for i in range(len(levels))}}
    facts = {}
    feats = [r.get("features") or {} for r in ok]
    if track == "video":
        for k in ("duration_s", "cuts_per_10s", "avg_shot_s"):
            vals = [f[k] for f in feats if f.get(k) is not None]
            facts[k] = ({"min": min(vals), "median": round(statistics.median(vals), 2), "max": max(vals), "n": len(vals)}
                        if vals else None)
        if any("captions" in f for f in feats):
            facts["captions_yes"] = sum(1 for f in feats if f.get("captions") is True)
    else:
        words = [f["words_on_image"] for f in feats if f.get("words_on_image") is not None]
        facts["words_on_image"] = ({"min": min(words), "median": statistics.median(words), "max": max(words)}
                                   if words else None)
        if any("has_price" in f for f in feats):
            facts["has_price"] = sum(1 for f in feats if f.get("has_price"))
        if any("cta_label" in f for f in feats):
            ctas = {}
            for f in feats:
                label = f.get("cta_label", "(no button)")
                ctas[label] = ctas.get(label, 0) + 1
            facts["cta_labels"] = dict(sorted(ctas.items(), key=lambda kv: (-kv[1], kv[0])))
        ratios = {}
        for f in feats:
            for a in f.get("aspect_ratios", []):
                ratios[a] = ratios.get(a, 0) + 1
        if ratios:
            facts["aspect_ratios"] = dict(sorted(ratios.items()))
    runtimes = []
    for r in ok:
        days = runtime_days(caps.get(r["creative_id"], {}))
        if days is not None:
            runtimes.append({"creative_id": r["creative_id"],
                             "advertiser": caps[r["creative_id"]].get("advertiser"), "days": days,
                             "tags": {d: r["tags"][d]["value"] for d in qs["CHOICE_COMPANION"]}})
    durability = {"note": "Runtime is a weak durability signal, not proof of results.",
                  "median_days": statistics.median([x["days"] for x in runtimes]) if runtimes else None,
                  "longest": [] if low else sorted(runtimes, key=lambda x: (-x["days"], x["creative_id"]))[:5],
                  "withheld": low}
    index = [{"creative_id": r["creative_id"], "advertiser": caps.get(r["creative_id"], {}).get("advertiser"),
              "days": runtime_days(caps.get(r["creative_id"], {})),
              "tags": {d: r["tags"][d]["value"] for d in qs["CHOICE_COMPANION"]},
              "flags": {f: r["flags"][f]["value"] for f in qs["FLAGS"]}} for r in ok]
    return {"n": n, "min_n": min_n, "low_sample": low, "errors": errors, "advertisers": advs,
            "creatives_per_advertiser": per_adv, "dimensions": dims, "crowded": crowded, "gaps": gaps,
            "single_advertiser": rare, "flags": flags, "scores": scores, "facts": facts,
            "durability": durability, "creatives": index,
            "models": sorted({r.get("model") or "" for r in ok}), "sources": sorted({r.get("source") for r in ok})}


def build(caps_list, tag_files, market, min_n, captured=None, question_files=None):
    caps = {c["creative_id"]: c for c in caps_list}
    by_track = {}
    for path in tag_files:
        for r in load_jsonl(path):
            by_track.setdefault(r["track"], []).append(r)
    snap = {"market": market, "built": captured or dt.date.today().isoformat(),
            "rules": {"min_n": min_n, "crowded_share": CROWDED_SHARE, "crowded_advertiser_share": CROWDED_ADV_SHARE,
                      "dominated_share": DOMINATED_SHARE},
            "caveat": "Ad libraries show what runs and for how long, not spend or results.", "tracks": {}}
    files = dict(QUESTION_FILES)
    files.update({k: v for k, v in (question_files or {}).items() if v})
    for track, recs in sorted(by_track.items()):
        path = files[track]
        qs = runpy.run_path(path)
        snap["tracks"][track] = track_snapshot(track, recs, caps, qs, min_n)
    return snap


def render_md(snap):
    out = ["# Market snapshot: %s" % snap["market"], "",
           "Built %s. %s Shares are of the track's tagged creatives; unresolved items (review band, conflicts, "
           "untagged) are counted apart and wait for a person." % (snap["built"], snap["caveat"]), ""]
    for track, t in snap["tracks"].items():
        out += ["## %s track" % track.capitalize(), "",
                "Creatives tagged: %d from %d advertisers (%s). Errors: %d. Model: %s. Source: %s."
                % (t["n"], len(t["advertisers"]), ", ".join("%s %d" % kv for kv in t["creatives_per_advertiser"].items()),
                   len(t["errors"]), ", ".join(t["models"]) or "none", ", ".join(t["sources"]) or "none"), ""]
        if t["low_sample"]:
            out += ["**Low sample: %d creatives, under %d. Nothing is ranked, labels below are directional, the "
                    "durability list is withheld.**" % (t["n"], t["min_n"]), ""]
        for dim, d in t["dimensions"].items():
            out += ["### %s (%s; unresolved %d)" % (dim, d["ordered_by"], d["unresolved"]), "",
                    "| Value | Creatives | Share | Advertisers | Advertiser share | Note |", "|---|---|---|---|---|---|"]
            for r in d["rows"]:
                note = "one advertiser supplies most" if r["dominated_by_one_advertiser"] else ""
                out.append("| %s | %d | %s | %d | %s | %s |" % (r["value"], r["creatives"], pct(r["share"]),
                                                               r["advertisers"], pct(r["advertiser_share"]), note))
            out.append("")
        mark = lambda x: " (low sample)" if x["low_sample"] else ""
        out += ["### Crowded, gaps, single advertiser", ""]
        out += ["- Crowded: %s %s, %s of creatives, %s of advertisers%s" % (c["dimension"], c["value"], pct(c["share"]),
                pct(c["advertiser_share"]), mark(c)) for c in t["crowded"]] or ["- Crowded: none at the current rules"]
        firm = [g for g in t["gaps"] if g["firm"]]
        weak = [g for g in t["gaps"] if not g["firm"]]
        out += ["- Gap (no resolved creative uses it): " + ", ".join("%s %s" % (g["dimension"], g["value"]) for g in firm)
                + (" (low sample)" if t["low_sample"] else "")] if firm else ["- Firm gaps: none"]
        if weak:
            out.append("- Possible gap, too many unresolved items in the dimension to be sure: "
                       + ", ".join("%s %s" % (g["dimension"], g["value"]) for g in weak))
        if t["single_advertiser"]:
            out.append("- Used by one advertiser only: " + ", ".join("%s %s (%d)" % (s["dimension"], s["value"],
                       s["creatives"]) for s in t["single_advertiser"]))
        out += ["", "### Flags and scores", "", "| Flag | Yes | Share | Review |", "|---|---|---|---|"]
        for f, v in t["flags"].items():
            out.append("| %s | %d | %s | %d |" % (f, v["yes"], pct(v["share"]), v["review"]))
        out.append("")
        for s, v in t["scores"].items():
            out.append("- %s: mean %s on a 0 to %d scale, levels %s" % (s, v["mean"], v["max_level"], v["levels"]))
        out += ["", "### Code facts", ""]
        for k, v in t["facts"].items():
            out.append("- %s: %s" % (k, json.dumps(v)))
        dur = t["durability"]
        out += ["", "### Durability (weak signal)", "", "Median runtime: %s days." % dur["median_days"]]
        if dur["withheld"]:
            out.append("Longest-running list withheld under the sample guard.")
        else:
            out += ["- %s (%s): %d days, %s" % (x["creative_id"], x["advertiser"], x["days"],
                    ", ".join("%s=%s" % kv for kv in x["tags"].items())) for x in dur["longest"]]
        out.append("")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--creatives", required=True, help="creatives.jsonl capture records")
    ap.add_argument("--tags", nargs="+", required=True, help="tags-static.jsonl and or tags-video.jsonl")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--market", default="unnamed market")
    ap.add_argument("--min-n", type=int, default=20, help="no ranking below this many creatives per track")
    ap.add_argument("--questions-static", help="static question set module (default questions_static.py next to "
                                               "this script); use the file the tags were made with")
    ap.add_argument("--questions-video", help="video question set module (default questions_video.py next to "
                                              "this script)")
    ap.add_argument("--date", help="build date to print (default today)")
    args = ap.parse_args(argv)
    snap = build(load_jsonl(args.creatives), args.tags, args.market, args.min_n, args.date,
                 {"static": args.questions_static, "video": args.questions_video})
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "snapshot.json"), "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(args.out_dir, "snapshot.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(snap))
    for track, t in snap["tracks"].items():
        print("%s: %d creatives, %d advertisers%s, crowded %d, gaps %d" % (
            track, t["n"], len(t["advertisers"]), " (LOW SAMPLE)" if t["low_sample"] else "",
            len(t["crowded"]), len(t["gaps"])))
    print("snapshot written to %s" % args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
