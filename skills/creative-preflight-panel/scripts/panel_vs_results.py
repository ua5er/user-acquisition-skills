#!/usr/bin/env python3
"""Check the pre-flight panel against real post-launch results.

Takes verdicts.json from panel_matrix.py and a CSV of real numbers the user
supplies from the ad platform (never invented, never estimated). Per track it
reports how well the panel's order matches the real order: Spearman rank
correlation, pairwise agreement, the misses (panel go that ranked in the
bottom third, panel rework that ranked in the top third), and what that means
for the panel's weight in the next round of decisions.

Results CSV, one row per panel item (static concept id, or concept-hook id
for video such as M1-A), with any of these columns:

  item_id, impressions, clicks, conversions, spend, ctr, cvr, cpa

Missing rates are computed from counts: ctr = clicks / impressions,
cvr = conversions / clicks, cpa = spend / conversions. Rows under the sample
floor (--min-impressions for ctr, --min-conversions for cvr and cpa) are left
out and listed. Standard library only, no network.

  python3 panel_vs_results.py --verdicts verdicts.json --results results.csv --metric ctr --out report.md
"""
import argparse
import csv
import json
import sys

# Starting cutoffs for the weight advice, not tested; change them here.
MIN_ITEMS = 5
STRONG_RHO = 0.5
STRONG_MIN_ITEMS = 8
WEAK_RHO = 0.2
DEFAULT_SCORE = {"ctr": "engage", "cvr": "click", "cpa": "click"}


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except ValueError:
        return None


def load_results(path, metric, min_impr, min_conv):
    kept, dropped = {}, []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            iid = (row.get("item_id") or "").strip()
            if not iid:
                continue
            impr, clicks, conv, spend = (_num(row.get(k)) for k in ("impressions", "clicks", "conversions", "spend"))
            value = _num(row.get(metric))
            if value is None:
                if metric == "ctr" and impr and clicks is not None:
                    value = clicks / impr
                elif metric == "cvr" and clicks and conv is not None:
                    value = conv / clicks
                elif metric == "cpa" and conv and spend is not None:
                    value = spend / conv
            if value is None:
                dropped.append((iid, "no %s and no counts to compute it" % metric))
                continue
            if metric == "ctr" and (impr is None or impr < min_impr):
                dropped.append((iid, "impressions %s under %d" % (impr, min_impr)))
                continue
            if metric in ("cvr", "cpa") and (conv is None or conv < min_conv):
                dropped.append((iid, "conversions %s under %d" % (conv, min_conv)))
                continue
            kept[iid] = value
    return kept, dropped


def ranks(values):
    """Average ranks, 1 = highest value."""
    order = sorted(range(len(values)), key=lambda i: -values[i])
    r = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 2:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return round(cov / (va * vb), 3) if va and vb else None


def pairwise(a, b):
    same = diff = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            s = (a[i] - a[j]) * (b[i] - b[j])
            if s > 0:
                same += 1
            elif s < 0:
                diff += 1
    return round(same / (same + diff), 3) if same + diff else None, same, diff


def advice(n, rho):
    if n < MIN_ITEMS or rho is None:
        return "too few items with real results (%d, need %d) to judge the panel: keep its weight low" % (n, MIN_ITEMS)
    if rho >= STRONG_RHO and n >= STRONG_MIN_ITEMS:
        return "the panel's order agrees with the results (rho %.2f on %d items): keep it as a pre-filter" % (rho, n)
    if rho >= WEAK_RHO:
        return "weak agreement (rho %.2f on %d items): use the panel as a tie-breaker only" % (rho, n)
    return "the panel does not track the results here (rho %.2f on %d items): do not cut concepts on it" % (rho, n)


def compare(verdicts, results, metric, score_key):
    by_track = {}
    for s in verdicts.get("items", []):
        if s.get("profiles_answered"):
            by_track.setdefault(s["track"], []).append(s)
    out = {"metric": metric, "panel_score": score_key, "tracks": {}}
    for track, items in by_track.items():
        matched = [s for s in items if s["item_id"] in results]
        panel = [s[score_key] for s in matched]
        real = [results[s["item_id"]] for s in matched]
        if metric == "cpa":
            real = [-x for x in real]  # lower CPA is better
        rho = spearman(panel, real)
        agree, same, diff = pairwise(panel, real)
        misses = []
        if len(matched) >= 3:
            rr = ranks(real)
            third = len(matched) / 3.0
            for s, r in zip(matched, rr):
                if s["verdict"] == "go" and r > len(matched) - third:
                    misses.append({"item_id": s["item_id"], "panel": "go", "real_rank": r,
                                   "note": "panel said go, results put it in the bottom third"})
                if s["verdict"] in ("rework", "drop") and r <= third:
                    misses.append({"item_id": s["item_id"], "panel": s["verdict"], "real_rank": r,
                                   "note": "panel held it back, results put it in the top third"})
        out["tracks"][track] = {
            "items_with_results": len(matched), "items_without_results": [s["item_id"] for s in items if s not in matched],
            "spearman": rho, "pairwise_agreement": agree, "pairs_same": same, "pairs_opposite": diff,
            "misses": misses, "advice": advice(len(matched), rho),
            "rows": [{"item_id": s["item_id"], "verdict": s["verdict"], "panel": s[score_key],
                      "real": results[s["item_id"]]} for s in matched]}
    return out


def render(rep, dropped):
    out = ["# Panel against real results", "",
           "Metric: %s. Panel score compared: %s. Real numbers as supplied by the user." % (rep["metric"], rep["panel_score"]),
           "", "A panel score is a cheap filter and a signal, not proof of performance. This report sets how much "
           "weight it gets next time; the live test stays the decision.", ""]
    for track, t in rep["tracks"].items():
        out += ["## %s track" % track.capitalize(), "",
                "- Items with results: %d. Spearman rank correlation: %s. Pairwise agreement: %s (%d same order, %d opposite)." % (
                    t["items_with_results"], t["spearman"], t["pairwise_agreement"], t["pairs_same"], t["pairs_opposite"]),
                "- Advice: %s." % t["advice"]]
        if t["items_without_results"]:
            out.append("- No results for: %s (dropped items are never tested, so the panel's drops cannot be checked "
                       "unless some ran anyway)." % ", ".join(t["items_without_results"]))
        out += ["", "| Item | Panel verdict | Panel score | Real %s |" % rep["metric"], "|---|---|---|---|"]
        for r in sorted(t["rows"], key=lambda r: -r["panel"]):
            out.append("| %s | %s | %.3f | %.4g |" % (r["item_id"], r["verdict"], r["panel"], r["real"]))
        out += ["", "Misses:", ""]
        out += ["- %s: %s (real rank %g)" % (m["item_id"], m["note"], m["real_rank"]) for m in t["misses"]] or ["- none"]
        out.append("")
    if dropped:
        out += ["## Left out", ""] + ["- %s: %s" % d for d in dropped] + [""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--results", required=True, help="CSV of real results the user supplies")
    ap.add_argument("--metric", choices=["ctr", "cvr", "cpa"], default="ctr")
    ap.add_argument("--panel-score", choices=["engage", "click", "fit"], help="default: engage for ctr, click otherwise")
    ap.add_argument("--min-impressions", type=int, default=1000)
    ap.add_argument("--min-conversions", type=int, default=5)
    ap.add_argument("--out", default="panel-vs-results.md")
    ap.add_argument("--json-out")
    args = ap.parse_args(argv)
    with open(args.verdicts, encoding="utf-8") as fh:
        verdicts = json.load(fh)
    results, dropped = load_results(args.results, args.metric, args.min_impressions, args.min_conversions)
    rep = compare(verdicts, results, args.metric, args.panel_score or DEFAULT_SCORE[args.metric])
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render(rep, dropped))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=1)
    for track, t in rep["tracks"].items():
        print("%s: %d items with results, spearman %s, pairwise %s; %s" % (
            track, t["items_with_results"], t["spearman"], t["pairwise_agreement"], t["advice"]))
    print("report written to %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
