#!/usr/bin/env python3
"""Build the concept x profile matrix and the go, rework, drop list.

Reads answers-<track>.jsonl from run_panel.py and profiles.jsonl. Per panel
item (a static concept, or one hook variant of a video concept) it computes
over the profiles that answered:

  engage      mean probability mass on stop or click (the ad held the person)
  click       mean probability mass on click
  uncertain   share of pairs whose stop-or-click mass sits in the review band
              (over 0.35 and under 0.70): the panel cannot tell hold from scroll
  flags       share of profiles at or over the tag threshold, and in the band,
              for hook_about_problem, offer_clear, distrust_claim
  fit         mean of the fit Score (0 to 3)
  loses       profiles where the item does not hold (engage under 0.35)
              or does not fit (fit under 1.0)

Then a ranking per track with guards (no ranking under --min-profiles
profiles, no winner when the lead is thinner than --tie-margin), and a
verdict per item and per concept with the reasons. Writes:

  matrix-<track>.csv   heatmap: items as rows, profiles as columns, engage values
  matrix.md            heatmaps, ranking and verdicts for a person
  verdicts.json        for brief_pack.py --panel-verdicts and for panel_vs_results.py

The verdict is advice for a person. A panel score is a cheap filter and a
signal, not proof of performance; it never replaces a live test.
Standard library only, no network.

  python3 panel_matrix.py --answers out/answers-static.jsonl out/answers-video.jsonl \\
      --profiles sample_panel/profiles.jsonl --out-dir out
"""
import argparse
import csv
import datetime
import json
import os
import sys

# Starting values, not tested on your market. Edit here; every change is a diff.
GO_ENGAGE = 0.50        # mean stop-or-click mass for a go
GO_FIT = 2.0            # mean fit for a go (0 to 3 scale)
DROP_ENGAGE = 0.30      # under this mean mass: drop
DROP_FIT = 1.0          # under this mean fit: drop
DISTRUST_MAX = 0.25     # share of profiles that would distrust a claim; above it a go becomes rework
UNCERTAIN_MAX = 0.50    # share of pairs in the review band; above it no go is given
WEAK_FLAG = 0.50        # under this share of profiles, a missing hook or offer is a rework reason
LOSE_ENGAGE = 0.35
LOSE_FIT = 1.0
MIN_PROFILES = 12
TIE_MARGIN = 0.10
TAG = 0.70
REVIEW_LOW = 0.35
FLAGS = ("hook_about_problem", "offer_clear", "distrust_claim")
ORDER = {"go": 0, "rework": 1, "drop": 2, "no verdict": 3}


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def item_stats(rows, profiles):
    ok = [r for r in rows if r.get("status") == "ok" and r.get("answers")]
    s = {"item_id": rows[0]["item_id"], "concept_id": rows[0]["concept_id"], "track": rows[0]["track"],
         "profiles_sent": len(rows), "profiles_answered": len(ok), "errors": len(rows) - len(ok), "cells": {}}
    if not ok:
        return s
    eng, clk, unc, fit = [], [], 0, []
    flag = {f: {"yes": 0, "review": 0, "mean": 0.0} for f in FLAGS}
    tops = {"scroll": 0, "stop": 0, "click": 0}
    for r in ok:
        a = r["answers"]
        probs = a["action"]["probabilities"]
        e = probs.get("stop", 0.0) + probs.get("click", 0.0)
        eng.append(e)
        clk.append(probs.get("click", 0.0))
        top = a["action"]["choice"]
        tops[top] = tops.get(top, 0) + 1
        # Stop and click both count as holding the person, so uncertainty is read on
        # the hold-or-scroll split, not on the three-way top option.
        uncertain = REVIEW_LOW < e < TAG
        unc += 1 if uncertain else 0
        fit.append(a["fit"]["score"])
        for f in FLAGS:
            p = a[f]["p_yes"]
            flag[f]["mean"] += p / len(ok)
            if p >= TAG:
                flag[f]["yes"] += 1
            elif p > REVIEW_LOW:
                flag[f]["review"] += 1
        s["cells"][r["profile_id"]] = {"engage": round(e, 3), "top": top, "uncertain": uncertain,
                                       "fit": round(a["fit"]["score"], 2)}
    n = len(ok)
    s.update(engage=round(sum(eng) / n, 3), click=round(sum(clk) / n, 3), uncertain_share=round(unc / n, 3),
             fit=round(sum(fit) / n, 2), top_actions=tops,
             flags={f: {"yes_share": round(v["yes"] / n, 3), "review": v["review"], "mean": round(v["mean"], 3)}
                    for f, v in flag.items()})
    labels = {p["profile_id"]: p.get("label", p["profile_id"]) for p in profiles}
    s["loses"] = [{"profile_id": pid, "label": labels.get(pid, pid), "engage": c["engage"], "fit": c["fit"]}
                  for pid, c in s["cells"].items() if c["engage"] < LOSE_ENGAGE or c["fit"] < LOSE_FIT]
    return s


def verdict(s, n_profiles):
    if not s.get("profiles_answered") or s["profiles_answered"] < 0.5 * s["profiles_sent"]:
        return "no verdict", ["fewer than half of the profiles answered (errors); rerun before deciding"]
    reasons = []
    e, f = s["engage"], s["fit"]
    distrust = s["flags"]["distrust_claim"]["yes_share"]
    if e < DROP_ENGAGE:
        reasons.append("holds few profiles: stop-or-click mass %.2f, under %.2f" % (e, DROP_ENGAGE))
    if f < DROP_FIT:
        reasons.append("fit %.2f of 3, under %.1f" % (f, DROP_FIT))
    if reasons:
        return "drop", reasons
    blocking, notes = [], []
    if e < GO_ENGAGE:
        blocking.append("stop-or-click mass %.2f, under %.2f for a go" % (e, GO_ENGAGE))
    if f < GO_FIT:
        blocking.append("fit %.2f of 3, under %.1f for a go" % (f, GO_FIT))
    if distrust > DISTRUST_MAX:
        blocking.append("%d%% of profiles would distrust a claim" % round(100 * distrust))
    if s["uncertain_share"] > UNCERTAIN_MAX:
        blocking.append("%d%% of answers in the review band: too uncertain for a go" % round(100 * s["uncertain_share"]))
    for flag, text in (("hook_about_problem", "hook about the person's problem"),
                       ("offer_clear", "offer or product clear at first sight")):
        share = s["flags"][flag]["yes_share"]
        if share < WEAK_FLAG:
            notes.append("%s for %d of %d profiles" % (text, round(share * s["profiles_answered"]),
                                                        s["profiles_answered"]))
    if s["loses"]:
        notes.append("loses %d of %d profiles" % (len(s["loses"]), s["profiles_answered"]))
    if n_profiles < MIN_PROFILES:
        notes.append("only %d profiles, under %d: directional" % (n_profiles, MIN_PROFILES))
    if blocking:
        return "rework", blocking + notes
    return "go", notes or ["holds and fits most profiles, no blocking flag"]


def rank(items, n_profiles):
    """Sort by engage then click; mark ties and whether a leader can be named."""
    out = sorted(items, key=lambda s: (-s.get("engage", -1), -s.get("click", -1)))
    if n_profiles < MIN_PROFILES:
        return out, "not ranked: %d profiles, under %d" % (n_profiles, MIN_PROFILES)
    if len(out) < 2:
        return out, "one item, nothing to rank"
    lead = out[0]["engage"] - out[1]["engage"]
    if lead < TIE_MARGIN:
        tied = [s["item_id"] for s in out if out[0]["engage"] - s["engage"] < TIE_MARGIN]
        return out, "no leader: %s within %.2f of each other" % (", ".join(tied), TIE_MARGIN)
    return out, "leader %s by %.2f over %s" % (out[0]["item_id"], lead, out[1]["item_id"])


def trailing_hooks(items, n_profiles):
    """Video: a hook that trails the best hook of its own concept by TIE_MARGIN or more is reworked."""
    if n_profiles < MIN_PROFILES:
        return
    by = {}
    for s in items:
        if s.get("profiles_answered") and s["item_id"] != s["concept_id"]:
            by.setdefault(s["concept_id"], []).append(s)
    for group in by.values():
        best = max(group, key=lambda s: s["engage"])
        for s in group:
            gap = best["engage"] - s["engage"]
            if s is not best and gap >= TIE_MARGIN and s["verdict"] == "go":
                s["verdict"] = "rework"
                s["reasons"] = ["trails hook %s of the same concept by %.2f: replace this opening" % (
                    best["item_id"], gap)] + [r for r in s["reasons"] if not r.startswith("holds and fits")]


def concept_rollup(items):
    by = {}
    for s in items:
        by.setdefault(s["concept_id"], []).append(s)
    out = []
    for cid, group in by.items():
        best = sorted(group, key=lambda s: (ORDER[s["verdict"]], -s.get("engage", -1)))[0]
        out.append({"concept_id": cid, "track": group[0]["track"], "verdict": best["verdict"],
                    "best_item": best["item_id"], "reasons": best["reasons"],
                    "items": {s["item_id"]: s["verdict"] for s in group}})
    return out


def build(answer_rows, profiles, min_profiles=MIN_PROFILES):
    global MIN_PROFILES
    MIN_PROFILES = min_profiles
    tracks = {}
    for r in answer_rows:
        tracks.setdefault(r["track"], {}).setdefault(r["item_id"], []).append(r)
    result = {"built": datetime.date.today().isoformat(), "notice": (
        "A panel score is a cheap filter and a signal, not proof of performance. It never replaces a live test "
        "and never touches budgets. A person decides."),
        "rules": {"go_engage": GO_ENGAGE, "go_fit": GO_FIT, "drop_engage": DROP_ENGAGE, "drop_fit": DROP_FIT,
                  "distrust_max": DISTRUST_MAX, "uncertain_max": UNCERTAIN_MAX, "min_profiles": MIN_PROFILES,
                  "tie_margin": TIE_MARGIN, "tag": TAG, "review_low": REVIEW_LOW},
        "tracks": {}, "items": [], "concepts": []}
    for track, by_item in tracks.items():
        n_prof = len({r["profile_id"] for rows in by_item.values() for r in rows})
        items = []
        for rows in by_item.values():
            s = item_stats(rows, profiles)
            s["verdict"], s["reasons"] = verdict(s, n_prof)
            items.append(s)
        trailing_hooks(items, n_prof)
        ranked, note = rank(items, n_prof)
        for i, s in enumerate(ranked, start=1):
            s["rank"] = i if n_prof >= MIN_PROFILES else None
        result["tracks"][track] = {"profiles": n_prof, "items": len(items), "ranking_note": note,
                                   "low_sample": n_prof < MIN_PROFILES,
                                   "order": [s["item_id"] for s in ranked]}
        result["items"] += ranked
        result["concepts"] += concept_rollup(ranked)
    return result


def write_csv(path, items, profile_ids):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["item_id", "concept_id", "engage_mean"] + profile_ids)
        for s in items:
            w.writerow([s["item_id"], s["concept_id"], s.get("engage", "")] +
                       [s["cells"].get(p, {}).get("engage", "") for p in profile_ids])


def render_md(result, profiles):
    labels = {p["profile_id"]: p.get("label", p["profile_id"]) for p in profiles}
    out = ["# Pre-flight panel", "", "Built %s. %s" % (result["built"], result["notice"]), ""]
    out += ["Cells: probability mass on stop or click (0 to 1) for one item and one profile. A `?` marks a pair "
            "in the review band (over %.2f and under %.2f): the panel cannot tell whether this person stops or "
            "scrolls." % (REVIEW_LOW, TAG), ""]
    for track, t in result["tracks"].items():
        items = [s for s in result["items"] if s["track"] == track]
        pids = sorted({pid for s in items for pid in s["cells"]})
        out += ["## %s track" % track.capitalize(), "",
                "%d items x %d profiles. Ranking: %s.%s" % (
                    t["items"], t["profiles"], t["ranking_note"],
                    " LOW SAMPLE, directional only." if t["low_sample"] else ""), "",
                "### Heatmap", "",
                "| Item | " + " | ".join(pids) + " | Mean |", "|---|" + "---|" * (len(pids) + 1)]
        for s in items:
            cells = []
            for p in pids:
                c = s["cells"].get(p)
                cells.append("" if not c else "%.2f%s" % (c["engage"], "?" if c["uncertain"] else ""))
            out.append("| %s | %s | %.2f |" % (s["item_id"], " | ".join(cells), s.get("engage", 0)))
        out += ["", "Profiles: " + "; ".join("%s %s" % (p, labels.get(p, p)) for p in pids) + ".", "",
                "### Ranking and verdicts", "",
                "| Rank | Item | Stop or click | Click | Fit (0-3) | Hook about problem | Offer clear | Distrust | "
                "Review band | Verdict | Reasons |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for s in items:
            if not s.get("profiles_answered"):
                out.append("| | %s | | | | | | | | %s | %s |" % (s["item_id"], s["verdict"], "; ".join(s["reasons"])))
                continue
            fl = s["flags"]
            out.append("| %s | %s | %.2f | %.2f | %.2f | %d%% | %d%% | %d%% | %d%% | %s | %s |" % (
                s["rank"] or "-", s["item_id"], s["engage"], s["click"], s["fit"],
                round(100 * fl["hook_about_problem"]["yes_share"]), round(100 * fl["offer_clear"]["yes_share"]),
                round(100 * fl["distrust_claim"]["yes_share"]), round(100 * s["uncertain_share"]),
                s["verdict"], "; ".join(s["reasons"])))
        out += ["", "### Profiles each item loses", ""]
        for s in items:
            lost = ", ".join("%s (%.2f, fit %.1f)" % (x["profile_id"], x["engage"], x["fit"]) for x in s.get("loses", []))
            out.append("- %s: %s" % (s["item_id"], lost or "none"))
        out.append("")
    out += ["## Concepts: go, rework, drop", "", "| Concept | Track | Verdict | Best item | Items | Reasons |",
            "|---|---|---|---|---|---|"]
    for c in result["concepts"]:
        out.append("| %s | %s | %s | %s | %s | %s |" % (
            c["concept_id"], c["track"], c["verdict"], c["best_item"],
            ", ".join("%s %s" % kv for kv in c["items"].items()), "; ".join(c["reasons"])))
    out += ["", "A person decides. Survivors (go, and rework after the fix) go to the test plan in "
            "meta-creative-testing; the live test decides, the panel does not.", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--answers", nargs="+", required=True, help="answers-<track>.jsonl files from run_panel.py")
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--min-profiles", type=int, default=MIN_PROFILES)
    args = ap.parse_args(argv)
    rows = [r for path in args.answers for r in load_jsonl(path)]
    if not rows:
        print("no answers found", file=sys.stderr)
        return 2
    profiles = load_jsonl(args.profiles)
    result = build(rows, profiles, args.min_profiles)
    os.makedirs(args.out_dir, exist_ok=True)
    for track in result["tracks"]:
        items = [s for s in result["items"] if s["track"] == track]
        pids = sorted({pid for s in items for pid in s["cells"]})
        write_csv(os.path.join(args.out_dir, "matrix-%s.csv" % track), items, pids)
    with open(os.path.join(args.out_dir, "matrix.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(result, profiles))
    with open(os.path.join(args.out_dir, "verdicts.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    for track, t in result["tracks"].items():
        print("%s: %d items x %d profiles; %s" % (track, t["items"], t["profiles"], t["ranking_note"]))
    counts = {}
    for c in result["concepts"]:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
    print("concepts: " + ", ".join("%s %d" % (k, counts[k]) for k in sorted(counts, key=ORDER.get)))
    print("written to %s (matrix.md, verdicts.json, matrix-<track>.csv)" % args.out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
