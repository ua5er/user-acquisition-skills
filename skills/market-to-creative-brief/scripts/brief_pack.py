#!/usr/bin/env python3
"""Check a decisions file against the market snapshot and assemble the brief pack.

Claude writes decisions.json (decisions, static briefs, motion briefs). This
script refuses to render numbers that the snapshot does not support:

  - every evidence line is re-read from snapshot.json and must match
  - every referenced ad id must exist in the snapshot's creative index
  - "enter_gap" needs a value with zero (or one advertiser's) creatives,
    "out_execute" needs a value the snapshot marks crowded
  - own performance may be cited only when the team supplied it
  - low-sample tracks are marked on every decision that uses them
  - concepts are checked against the test budget with the kill rule of
    meta-creative-testing (a creative needs about 2x target CPA of spend
    before it can be killed)
  - brief fields the template requires are listed as blocking when missing
  - motion beats must start at 0, run without gaps, and the hook must end by 3 s

Writes the pack as Markdown and, on request, a CSV of copy lines for
jev-marketing-gates and a concepts file for creative-preflight-panel.
Standard library only, no network.

  python3 brief_pack.py --decisions decisions.json --snapshot snapshot.json --out brief-pack.md \\
      --gates-csv copy-check.csv --panel-concepts concepts.jsonl

After the pre-flight panel, render again with its verdicts:

  python3 brief_pack.py --decisions decisions.json --snapshot snapshot.json --out brief-pack.md \\
      --panel-verdicts verdicts.json
"""
import argparse
import csv
import json
import math
import sys

MOVES = {"enter_gap", "out_execute", "avoid", "iterate_own"}
METRICS = {"creatives", "share", "advertisers", "advertiser_share"}
FLAG_METRICS = {"flag_yes", "flag_share", "flag_review"}
STATIC_REQUIRED = ["concept_id", "decision_id", "concept", "angle", "hook", "layout", "copy", "offer", "sizes",
                   "variants", "references", "avoid", "claims_notes", "acceptance"]
MOTION_REQUIRED = ["concept_id", "decision_id", "concept", "hooks", "beats", "voice_or_captions", "format",
                   "aspect_ratios", "durations_s", "pacing_sound", "end_card", "variants", "references", "avoid",
                   "claims_notes", "acceptance"]


def _close(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= 0.005 if isinstance(b, float) or isinstance(a, float) else a == b
    return a == b


def lookup(snap, ev):
    """Return the snapshot value for one evidence line, or raise KeyError."""
    t = snap["tracks"][ev["track"]]
    m = ev["metric"]
    if m in FLAG_METRICS:
        f = t["flags"][ev["dimension"]]
        return {"flag_yes": f["yes"], "flag_share": f["share"], "flag_review": f["review"]}[m]
    if m == "unresolved":
        return t["dimensions"][ev["dimension"]]["unresolved"]
    if m == "score_mean":
        return t["scores"][ev["dimension"]]["mean"]
    if m == "fact":
        node = t["facts"]
        for k in ev["dimension"].split("."):
            node = node[k]
        return node
    if m not in METRICS:
        raise KeyError("unknown metric %s" % m)
    for row in t["dimensions"][ev["dimension"]]["rows"]:
        if row["value"] == ev["value"]:
            return row[m]
    raise KeyError("value %s not in %s" % (ev["value"], ev["dimension"]))


def check(dec, snap):
    errors, warnings, blocking, low = [], [], [], {}
    ids = {c["creative_id"]: tr for tr, t in snap["tracks"].items() for c in t["creatives"]}
    own = (dec.get("constraints") or {}).get("own_performance")
    for d in dec.get("decisions", []):
        did = d.get("id", "?")
        if d.get("move") not in MOVES:
            errors.append("%s: move must be one of %s" % (did, sorted(MOVES)))
        if d.get("track") not in snap["tracks"]:
            errors.append("%s: track %s is not in the snapshot" % (did, d.get("track")))
            continue
        t = snap["tracks"][d["track"]]
        d["_low_sample"] = t["low_sample"]
        for ev in d.get("evidence", []):
            try:
                actual = lookup(snap, ev)
            except (KeyError, TypeError) as exc:
                errors.append("%s: evidence %s cannot be found in the snapshot (%s)" % (did, ev, exc))
                continue
            if not _close(actual, ev.get("expected")):
                errors.append("%s: evidence %s %s %s says %s, snapshot has %s" % (
                    did, ev["track"], ev["dimension"], ev.get("value", ""), ev.get("expected"), actual))
        if not d.get("evidence"):
            errors.append("%s: no evidence from the snapshot" % did)
        for ref in d.get("refs", []):
            if ref not in ids:
                errors.append("%s: ad id %s is not in the snapshot" % (did, ref))
        dim, val = d.get("dimension"), d.get("value")
        if d.get("move") in ("enter_gap", "out_execute") and dim in t["dimensions"]:
            row = next((r for r in t["dimensions"][dim]["rows"] if r["value"] == val), None)
            if row is None:
                errors.append("%s: %s has no value %s" % (did, dim, val))
            elif d["move"] == "enter_gap" and row["creatives"] > 0 and row["advertisers"] > 1:
                errors.append("%s: %s %s is used by %d advertisers, it is not a gap" % (did, dim, val, row["advertisers"]))
            elif d["move"] == "enter_gap":
                gap = next((g for g in t["gaps"] if g["dimension"] == dim and g["value"] == val), None)
                if gap and not gap["firm"]:
                    warnings.append("%s: %s %s is only a possible gap (many unresolved items)" % (did, dim, val))
            elif d["move"] == "out_execute" and not any(c["dimension"] == dim and c["value"] == val for c in t["crowded"]):
                errors.append("%s: %s %s is not marked crowded in the snapshot" % (did, dim, val))
        if d.get("cites_own_performance") and not own:
            errors.append("%s: cites own performance but the team supplied none; remove the claim" % did)
        if t["low_sample"]:
            low.setdefault(d["track"], []).append(did)
    for tr, dids in low.items():
        t = snap["tracks"][tr]
        warnings.append("track %s has %d creatives, under %d: decisions %s are directional only" % (
            tr, t["n"], t["min_n"], ", ".join(dids)))
    dec_ids = {d.get("id") for d in dec.get("decisions", [])}
    for kind, req in (("static_briefs", STATIC_REQUIRED), ("motion_briefs", MOTION_REQUIRED)):
        for b in dec.get(kind, []):
            cid = b.get("concept_id", "?")
            missing = [f for f in req if b.get(f) in (None, "", [], {})]
            if missing:
                blocking.append("%s: missing %s" % (cid, ", ".join(missing)))
            if b.get("decision_id") not in dec_ids:
                errors.append("%s: decision %s does not exist" % (cid, b.get("decision_id")))
            for r in b.get("references", []):
                if r.get("id") not in ids:
                    errors.append("%s: reference %s is not in the snapshot" % (cid, r.get("id")))
            if kind == "motion_briefs":
                errors += ["%s: %s" % (cid, e) for e in check_beats(b)]
                if len(b.get("hooks", [])) != 3:
                    blocking.append("%s: needs exactly three hook variants for seconds 0 to 3" % cid)
    budget = (dec.get("constraints") or {}).get("test_budget") or {}
    plan = budget_check(dec, budget)
    if plan.get("over"):
        warnings.append("%d creatives planned, the budget gives a kill read on about %d" % (plan["creatives"], plan["kill_reads"]))
    return errors, warnings, blocking, plan


def check_beats(b):
    errs = []
    beats = b.get("beats", [])
    if not beats:
        return errs
    prev = 0.0
    for i, beat in enumerate(beats):
        try:
            start, end = (float(x) for x in str(beat["t"]).split("-"))
        except (KeyError, ValueError):
            errs.append("beat %d: t must look like '3-8'" % (i + 1))
            return errs
        if abs(start - prev) > 1e-6:
            errs.append("beat %d starts at %s, expected %s" % (i + 1, start, prev))
        if end <= start:
            errs.append("beat %d ends before it starts" % (i + 1))
        prev = end
    first_end = float(str(beats[0]["t"]).split("-")[1])
    if first_end > 3:
        errs.append("the hook beat must end by 3 s, it ends at %s" % first_end)
    longest = max((float(x) for x in b.get("durations_s", [prev])), default=prev)
    if prev > longest + 1e-6:
        errs.append("beats run to %s s, longer than the longest duration %s s" % (prev, longest))
    return errs


def creative_count(dec):
    n = 0
    for b in dec.get("static_briefs", []):
        n += max(1, len(b.get("variants", [])))
    for b in dec.get("motion_briefs", []):
        n += max(1, len(b.get("hooks", [])))
    return n


def budget_check(dec, budget):
    n = creative_count(dec)
    amount, cpa = budget.get("amount"), budget.get("target_cpa")
    if not amount or not cpa:
        return {"creatives": n, "kill_reads": None, "over": False, "note": "no test budget or target CPA given"}
    reads = int(math.floor(amount / (2.0 * cpa)))
    return {"creatives": n, "kill_reads": reads, "over": n > reads, "amount": amount, "target_cpa": cpa,
            "currency": budget.get("currency", ""), "label": budget.get("label", "")}


# ------------------------------------------------------------------ render

def bullet(items):
    return ["- %s" % x for x in items] if items else ["- (none)"]


def ev_text(ev):
    m = ev["metric"]
    v = ev["expected"]
    shown = "%d%%" % round(100 * v) if m in ("share", "advertiser_share", "flag_share") else v
    parts = [ev["track"], ev["dimension"], ev.get("value", ""), m]
    return "%s = %s" % (" ".join(p for p in parts if p), shown)


def render(dec, snap, errors, warnings, blocking, plan, panel=None):
    out = ["# Creative brief pack: %s" % dec.get("market", snap.get("market", "")), ""]
    if dec.get("notice"):
        out += ["> %s" % dec["notice"], ""]
    out += ["Snapshot built %s. %s A person approves this pack before any production or spend." % (
        snap.get("built"), snap.get("caveat", "")), ""]
    for tr, t in snap["tracks"].items():
        out.append("- %s track: %d creatives from %d advertisers%s." % (
            tr, t["n"], len(t["advertisers"]), ", LOW SAMPLE, directional only" if t["low_sample"] else ""))
    out.append("")
    if errors or blocking:
        out += ["## Not ready", ""] + bullet(errors + blocking) + [""]
    if warnings:
        out += ["## Warnings", ""] + bullet(warnings) + [""]
    c = dec.get("constraints") or {}
    out += ["## Team constraints", "",
            "- Brand rules: %s" % c.get("brand_rules", "(not given)"),
            "- Offers allowed: %s" % c.get("offers", "(not given)"),
            "- Can produce: %s" % c.get("can_produce", "(not given)"),
            "- Own performance data: %s" % ("supplied" if c.get("own_performance") else "none supplied, nothing is cited")]
    if plan.get("kill_reads") is not None:
        out.append("- Test budget %s %s at target CPA %s%s: about %d creatives can reach a kill read (spend of 2x target "
                   "CPA each, rule from meta-creative-testing); this pack plans %d." % (
                       plan["amount"], plan["currency"], plan["target_cpa"],
                       " (%s)" % plan["label"] if plan.get("label") else "", plan["kill_reads"], plan["creatives"]))
    out += ["", "## Decisions", "", "| Id | Track | Move | What | Concepts | Evidence | Ads |", "|---|---|---|---|---|---|---|"]
    for d in dec.get("decisions", []):
        out.append("| %s | %s | %s | %s %s | %s | %s | %s |" % (
            d["id"], d["track"] + (" (low sample)" if d.get("_low_sample") else ""), d["move"], d.get("dimension", ""),
            d.get("value", ""), d.get("concepts", 0), "; ".join(ev_text(e) for e in d.get("evidence", [])),
            ", ".join(d.get("refs", []))))
    out.append("")
    for d in dec.get("decisions", []):
        out += ["**%s.** %s" % (d["id"], d.get("rationale", "")), ""]
        if d.get("hypothesis"):
            out += ["Hypothesis for the test: %s" % d["hypothesis"], ""]
    if panel:
        out += render_panel(panel)
    for b in dec.get("static_briefs", []):
        out += render_static(b)
    for b in dec.get("motion_briefs", []):
        out += render_motion(b)
    out += render_test_plan(dec, panel)
    return "\n".join(out) + "\n"


def refs_lines(b):
    return ["- %s: take %s; do not take %s" % (r["id"], r.get("take", ""), r.get("leave", "the execution"))
            for r in b.get("references", [])]


def render_static(b):
    cp = b.get("copy") or {}
    out = ["## Static brief %s: %s" % (b.get("concept_id"), b.get("concept", "")), "",
           "For: designers. Decision: %s." % b.get("decision_id"), "",
           "- Angle: %s" % b.get("angle", "MISSING"),
           "- Hook (headline, verbatim): %s" % b.get("hook", "MISSING"),
           "- Layout: %s" % b.get("layout", "MISSING"),
           "- Visual: %s" % b.get("visual", "(designer's choice within the brand rules)"),
           "- Copy blocks: headline \"%s\"; primary text \"%s\"; CTA button \"%s\"" % (
               cp.get("headline", "MISSING"), cp.get("primary_text", "MISSING"), cp.get("cta", "MISSING")),
           "- Offer and its placement: %s" % b.get("offer", "MISSING"),
           "- Offer line as the viewer reads it: %s" % b.get("offer_line", "(as in the copy)"),
           "- Sizes: %s" % ", ".join(b.get("sizes", [])),
           "", "Variants (one variable each):", ""]
    out += bullet(b.get("variants", []))
    out += ["", "References by ad id (patterns, not copies):", ""] + (refs_lines(b) or ["- (none)"])
    out += ["", "Avoid:", ""] + bullet(b.get("avoid", []))
    out += ["", "Claim and policy notes:", ""] + bullet(b.get("claims_notes", []))
    out += ["", "Acceptance checklist:", ""] + ["- [ ] %s" % x for x in b.get("acceptance", [])] + [""]
    return out


def render_motion(b):
    out = ["## Motion brief %s: %s" % (b.get("concept_id"), b.get("concept", "")), "",
           "For: motion design or video team. Decision: %s." % b.get("decision_id"), "",
           "- Format: %s" % b.get("format", "MISSING"),
           "- Aspect ratios: %s; durations: %s s" % (", ".join(b.get("aspect_ratios", [])),
                                                    ", ".join(str(x) for x in b.get("durations_s", []))),
           "- Voice-over or captions: %s" % b.get("voice_or_captions", "MISSING"),
           "- Pacing and sound: %s" % b.get("pacing_sound", "MISSING"),
           "", "Hook, seconds 0 to 3, three variants (only these seconds change between them):", "",
           "| Variant | Spoken | On screen | Visual | Sound |", "|---|---|---|---|---|"]
    for h in b.get("hooks", []):
        out.append("| %s | %s | %s | %s | %s |" % (h.get("id"), h.get("spoken", ""), h.get("on_screen", ""),
                                                  h.get("visual", ""), h.get("sound", "")))
    out += ["", "Beat sheet:", "", "| Time (s) | Visual | Spoken | On screen | Motion | Sound |", "|---|---|---|---|---|---|"]
    for bt in b.get("beats", []):
        out.append("| %s | %s | %s | %s | %s | %s |" % (bt.get("t"), bt.get("visual", ""), bt.get("spoken", ""),
                                                       bt.get("on_screen", ""), bt.get("motion", ""), bt.get("sound", "")))
    out += ["", "- End card: %s" % b.get("end_card", "MISSING"), "", "Variants for testing:", ""]
    out += bullet(b.get("variants", []))
    out += ["", "References by ad id (patterns, not copies):", ""] + (refs_lines(b) or ["- (none)"])
    out += ["", "Avoid:", ""] + bullet(b.get("avoid", []))
    out += ["", "Claim and policy notes:", ""] + bullet(b.get("claims_notes", []))
    out += ["", "Acceptance checklist:", ""] + ["- [ ] %s" % x for x in b.get("acceptance", [])] + [""]
    return out


def ad_names(dec):
    """(panel item id, ad name) per creative: one per static variant, one per motion hook."""
    project = dec.get("project", "PROJECT")
    test = dec.get("test_name", "TEST")
    rows = []
    for b in dec.get("static_briefs", []):
        for i, _ in enumerate(b.get("variants", []) or [""], start=1):
            rows.append((b["concept_id"], "%s | %s | Static | %s v%d | src: market %s" % (
                project, test, b["concept_id"], i, "+".join(r["id"] for r in b.get("references", [])))))
    for b in dec.get("motion_briefs", []):
        for h in b.get("hooks", []):
            rows.append(("%s-%s" % (b["concept_id"], h.get("id")), "%s | %s | Video | %s hook %s | src: market %s" % (
                project, test, b["concept_id"], h.get("id"), "+".join(r["id"] for r in b.get("references", [])))))
    return rows


def panel_item_verdicts(panel):
    return {s["item_id"]: s["verdict"] for s in (panel or {}).get("items", [])}


def render_panel(panel):
    out = ["## Pre-flight panel (creative-preflight-panel)", "",
           "> %s" % panel.get("notice", "A panel score is a signal, not proof of performance."), "",
           "| Concept | Track | Verdict | Best item | Items | Reasons |", "|---|---|---|---|---|---|"]
    for c in panel.get("concepts", []):
        out.append("| %s | %s | %s | %s | %s | %s |" % (
            c["concept_id"], c["track"], c["verdict"], c["best_item"],
            ", ".join("%s %s" % kv for kv in sorted(c.get("items", {}).items())), "; ".join(c.get("reasons", []))))
    out.append("")
    return out


def render_test_plan(dec, panel=None):
    verdicts = panel_item_verdicts(panel)
    names = ad_names(dec)
    keep = ["`%s`%s" % (n, " (panel: rework before production)" if verdicts.get(item) == "rework" else "")
            for item, n in names if verdicts.get(item, "go") in ("go", "rework")]
    held = [(item, n) for item, n in names if verdicts.get(item, "go") not in ("go", "rework")]
    out = ["## Hand-off: test plan for meta-creative-testing", "",
           "Ad names in the format `PROJECT | TEST | Format | Concept | src`:", ""]
    out += ["- %s" % n for n in keep]
    if held:
        out += ["", "Held back by the pre-flight panel (a person may override; rework items enter after the fix):", ""]
        out += ["- `%s` (%s)" % (n, verdicts[item]) for item, n in held]
    out += ["", "Run it with meta-creative-testing: one broad ad set by default, its kill, winner and fatigue "
            "criteria, a control that stays live, judged on the primary metric only after the spend gate. "
            "Optional before production: creative-preflight-panel on the concepts file. Optional before launch: "
            "the copy lines through jev-marketing-gates. Nothing in this pack is published or launched by the skill.", ""]
    return out


# ------------------------------------------------------------ side outputs

def gates_rows(dec):
    rules = (dec.get("constraints") or {}).get("brand_rules", "")
    rows = []
    for b in dec.get("static_briefs", []):
        cp = b.get("copy") or {}
        rows.append({"id": b["concept_id"], "headline": cp.get("headline", ""), "body": cp.get("primary_text", ""),
                     "brand_rules": rules})
    for b in dec.get("motion_briefs", []):
        for h in b.get("hooks", []):
            body = " ".join(bt.get("spoken", "") for bt in b.get("beats", [])[1:])
            rows.append({"id": "%s-%s" % (b["concept_id"], h.get("id")), "headline": h.get("spoken") or h.get("on_screen", ""),
                         "body": (body + " " + b.get("end_card", "")).strip(), "brand_rules": rules})
    return rows


def panel_concepts(dec):
    out = []
    for b in dec.get("static_briefs", []):
        cp = b.get("copy") or {}
        out.append({"concept_id": b["concept_id"], "track": "static", "decision_id": b["decision_id"],
                    "headline": cp.get("headline", ""), "primary_text": cp.get("primary_text", ""),
                    "cta": cp.get("cta", ""), "offer": b.get("offer", ""), "offer_line": b.get("offer_line", ""),
                    "layout": b.get("layout", ""),
                    "visual": b.get("visual", "")})
    for b in dec.get("motion_briefs", []):
        out.append({"concept_id": b["concept_id"], "track": "video", "decision_id": b["decision_id"],
                    "hooks": [{"id": h.get("id"), "spoken": h.get("spoken", ""), "on_screen": h.get("on_screen", ""),
                               "visual": h.get("visual", "")} for h in b.get("hooks", [])],
                    "beats": [{"t": bt.get("t"), "visual": bt.get("visual", ""), "spoken": bt.get("spoken", ""),
                               "on_screen": bt.get("on_screen", "")} for bt in b.get("beats", [])],
                    "end_card": b.get("end_card", ""), "format": b.get("format", "")})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", default="brief-pack.md")
    ap.add_argument("--gates-csv", help="write copy lines for jev-marketing-gates (id, headline, body, brand_rules)")
    ap.add_argument("--panel-concepts", help="write concepts.jsonl for creative-preflight-panel")
    ap.add_argument("--panel-verdicts", help="verdicts.json from creative-preflight-panel: adds the go, rework, "
                    "drop table and holds dropped items out of the test plan")
    ap.add_argument("--allow-errors", action="store_true", help="render even when evidence does not match")
    args = ap.parse_args(argv)
    with open(args.decisions, encoding="utf-8") as fh:
        dec = json.load(fh)
    with open(args.snapshot, encoding="utf-8") as fh:
        snap = json.load(fh)
    panel = None
    if args.panel_verdicts:
        with open(args.panel_verdicts, encoding="utf-8") as fh:
            panel = json.load(fh)
    errors, warnings, blocking, plan = check(dec, snap)
    for e in errors:
        print("ERROR " + e)
    for b in blocking:
        print("BLOCKING " + b)
    for w in warnings:
        print("warning " + w)
    if errors and not args.allow_errors:
        print("not rendered: fix the evidence or pass --allow-errors to see a draft marked Not ready")
        return 1
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render(dec, snap, errors, warnings, blocking, plan, panel))
    if args.gates_csv:
        with open(args.gates_csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["id", "headline", "body", "brand_rules"])
            w.writeheader()
            w.writerows(gates_rows(dec))
    if args.panel_concepts:
        with open(args.panel_concepts, "w", encoding="utf-8") as fh:
            for c in panel_concepts(dec):
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("pack written to %s: %d decisions, %d static briefs, %d motion briefs, %d creatives planned%s"
          % (args.out, len(dec.get("decisions", [])), len(dec.get("static_briefs", [])),
             len(dec.get("motion_briefs", [])), plan["creatives"], "; BLOCKING items open" if blocking else ""))
    return 1 if errors or blocking else 0


if __name__ == "__main__":
    sys.exit(main())
