#!/usr/bin/env python3
"""Turn labelled examples plus a run_batch.py log into report.md.

Python 3 standard library only, no network, no key.

labels.csv columns: item_id, question_id, label
  noul label: yes or no (also true/false/1/0)
  choice label: an option name from the question
  score label: a level number (0 is the first level, as in the docs)

Example:
  python3 calibrate.py --log log.csv --labels sample_labels.csv --questions questions_example.py --out report.md

Small samples are noisy. Treat every suggestion as a starting point and re-run
when you have more labels. Nothing here proves a threshold is safe.
"""
import argparse
import csv
import json
import runpy
import sys

DEFAULT_PRICE_PER_MILLION = 0.042  # docs.typesafe.ai/models.md, checked 2026-11-15
MIN_FOR_SUGGESTION = 5
GRID = [round(0.5 + 0.05 * i, 2) for i in range(10)]  # 0.50 to 0.95


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def parse_yes(text):
    t = str(text).strip().lower()
    if t in ("yes", "true", "1", "y"):
        return True
    if t in ("no", "false", "0", "n"):
        return False
    raise ValueError("cannot read noul label %r (use yes or no)" % text)


def rebuild_answers(log_rows):
    """item_id -> question_id -> normalized answer, from log rows. Skips error rows."""
    items = {}
    for row in log_rows:
        if row["answer"] == "ERROR":
            items.setdefault(row["item_id"], {})
            continue
        probs = json.loads(row["probabilities"]) if row["probabilities"] else {}
        qtype = row["question_type"]
        if qtype == "noul":
            value = probs.get("yes", 1.0 if row["answer"] == "yes" else 0.0)
        elif qtype == "score":
            value = float(row["answer"])
        else:
            value = row["answer"]
        conf = float(row["confidence"]) if row["confidence"] not in ("", None) else None
        items.setdefault(row["item_id"], {})[row["question_id"]] = {
            "type": qtype, "value": value, "probs": probs, "confidence": conf}
    return items


def pct(n, d):
    return "n/a" if d == 0 else "%.0f%%" % (100.0 * n / d)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def noul_section(qid, pairs, thresholds, target):
    """pairs: list of (p_yes, is_yes)."""
    lines = []
    n = len(pairs)
    rows = []
    for b in range(10):
        lo, hi = b / 10.0, (b + 1) / 10.0
        sel = [y for p, y in pairs if lo <= p < hi or (b == 9 and p == 1.0)]
        yes = sum(1 for y in sel if y)
        if not sel:
            rows.append(["%.1f to %.1f" % (lo, hi), 0, "", "", ""])
            continue
        lean_yes = lo >= 0.5
        acc = yes if lean_yes else len(sel) - yes
        rows.append(["%.1f to %.1f" % (lo, hi), len(sel), yes, pct(yes, len(sel)), pct(acc, len(sel))])
    lines += md_table(["yes probability", "n", "labelled yes", "share yes", "accuracy of the leaning answer"], rows)
    tp = sum(1 for p, y in pairs if p >= 0.5 and y)
    fp = sum(1 for p, y in pairs if p >= 0.5 and not y)
    fn = sum(1 for p, y in pairs if p < 0.5 and y)
    tn = sum(1 for p, y in pairs if p < 0.5 and not y)
    lines += ["", "Confusion at 0.5: true yes %d, false yes %d, false no %d, true no %d." % (tp, fp, fn, tn)]
    low, high = thresholds.get("low"), thresholds.get("high")
    if low is not None and high is not None:
        yes_called = [y for p, y in pairs if p >= high]
        no_called = [y for p, y in pairs if p <= low]
        band = [1 for p, y in pairs if low < p < high]
        lines += ["", "At the current thresholds (no at or below %.2f, yes at or above %.2f):" % (low, high),
                  "- called yes: %d, labelled yes among them %s" % (len(yes_called), pct(sum(yes_called), len(yes_called))),
                  "- called no: %d, labelled no among them %s" % (len(no_called), pct(len(no_called) - sum(no_called), len(no_called))),
                  "- in the review band: %d of %d (%s)" % (len(band), n, pct(len(band), n))]
    hi_s = next((t for t in GRID if sum(1 for p, y in pairs if p >= t) >= MIN_FOR_SUGGESTION and
                 sum(1 for p, y in pairs if p >= t and y) / float(sum(1 for p, y in pairs if p >= t)) >= target), None)
    lo_s = next((round(1 - t, 2) for t in GRID if sum(1 for p, y in pairs if p <= 1 - t) >= MIN_FOR_SUGGESTION and
                 sum(1 for p, y in pairs if p <= 1 - t and not y) / float(sum(1 for p, y in pairs if p <= 1 - t)) >= target), None)
    lines += ["", "Suggestion for a precision target of %.0f%% (needs at least %d items on a side):" % (100 * target, MIN_FOR_SUGGESTION)]
    lines.append("- yes at or above %.2f" % hi_s if hi_s is not None else "- no yes threshold reaches the target on this sample; rewrite the question or add labels")
    lines.append("- no at or below %.2f" % lo_s if lo_s is not None else "- no no threshold reaches the target on this sample; rewrite the question or add labels")
    return lines


def choice_section(qid, rows_, thresholds, target, option_order):
    """rows_: list of (top_option, top_prob, label)."""
    lines = []
    n = len(rows_)
    correct = sum(1 for top, p, lab in rows_ if top == lab)
    lines.append("Top option accuracy: %d of %d (%s)." % (correct, n, pct(correct, n)))
    table = []
    for b in range(10):
        lo, hi = b / 10.0, (b + 1) / 10.0
        sel = [(top, lab) for top, p, lab in rows_ if lo <= p < hi or (b == 9 and p == 1.0)]
        table.append(["%.1f to %.1f" % (lo, hi), len(sel), sum(1 for t, l in sel if t == l),
                      pct(sum(1 for t, l in sel if t == l), len(sel))])
    lines += [""] + md_table(["top probability", "n", "correct", "accuracy"], table)
    labels = sorted({lab for _, _, lab in rows_} | {top for top, _, _ in rows_})
    conf = [["label \\ predicted"] + labels]
    for lab in labels:
        conf.append([lab] + [sum(1 for t, _, l in rows_ if l == lab and t == pred) for pred in labels])
    lines += ["", "Confusion counts (rows are labels, columns are predictions):"] + md_table(conf[0], conf[1:])
    if option_order:
        first = option_order[0]
        lines += ["", "First option check (the docs list a lean toward the first option): option %r is the label in %s of items "
                  "and the prediction in %s. A prediction share well above the label share is a warning; reorder the options and re-run."
                  % (first, pct(sum(1 for _, _, l in rows_ if l == first), n), pct(sum(1 for t, _, _ in rows_ if t == first), n))]
    cur = thresholds.get("min_prob")
    if cur is not None:
        acted = [(t, l) for t, p, l in rows_ if p >= cur]
        lines += ["", "At the current minimum probability %.2f: acted on %d of %d, accuracy among them %s." %
                  (cur, len(acted), n, pct(sum(1 for t, l in acted if t == l), len(acted)))]
    sug = next((t for t in GRID if sum(1 for top, p, lab in rows_ if p >= t) >= MIN_FOR_SUGGESTION and
                sum(1 for top, p, lab in rows_ if p >= t and top == lab) / float(sum(1 for top, p, lab in rows_ if p >= t)) >= target), None)
    lines += ["", "Suggestion for an accuracy target of %.0f%%: %s" % (
        100 * target, "act when the top probability is at least %.2f" % sug if sug is not None else
        "no threshold reaches the target on this sample; rewrite the question, split it, or add labels")]
    return lines


def score_section(qid, rows_, target):
    """rows_: list of (predicted_level, score, confidence, label_level)."""
    lines = []
    n = len(rows_)
    exact = sum(1 for pl, s, c, lab in rows_ if pl == lab)
    mae = sum(abs(s - lab) for pl, s, c, lab in rows_) / float(n)
    lines.append("Most likely level equals the label: %d of %d (%s). Mean absolute error of the score: %.2f levels."
                 % (exact, n, pct(exact, n), mae))
    table = []
    for b in range(10):
        lo, hi = b / 10.0, (b + 1) / 10.0
        sel = [(pl, lab) for pl, s, c, lab in rows_ if c is not None and (lo <= c < hi or (b == 9 and c == 1.0))]
        table.append(["%.1f to %.1f" % (lo, hi), len(sel), sum(1 for p, l in sel if p == l), pct(sum(1 for p, l in sel if p == l), len(sel))])
    lines += [""] + md_table(["confidence", "n", "level correct", "accuracy"], table)
    levels = sorted({lab for *_, lab in rows_} | {pl for pl, *_ in rows_})
    conf = [["label \\ predicted"] + [str(x) for x in levels]]
    for lab in levels:
        conf.append([str(lab)] + [sum(1 for pl, _, _, l in rows_ if l == lab and pl == pred) for pred in levels])
    lines += ["", "Confusion counts (rows are labels, columns are most likely levels):"] + md_table(conf[0], conf[1:])
    sug = next((t for t in GRID if sum(1 for pl, s, c, lab in rows_ if c is not None and c >= t) >= MIN_FOR_SUGGESTION and
                sum(1 for pl, s, c, lab in rows_ if c is not None and c >= t and pl == lab) /
                float(sum(1 for pl, s, c, lab in rows_ if c is not None and c >= t)) >= target), None)
    lines += ["", "Suggestion for a level accuracy target of %.0f%%: %s" % (
        100 * target, "trust the level when confidence is at least %.2f" % sug if sug is not None else
        "no confidence floor reaches the target on this sample")]
    return lines


def build_report(log_rows, label_rows, questions, route, thresholds_by_q, target, price, option_orders):
    answers = rebuild_answers(log_rows)
    labels = {}
    for row in label_rows:
        labels[(row["item_id"], row["question_id"])] = row["label"]
    out = ["# Calibration report", "",
           "Source: %d logged items, %d labelled answers. Generated by calibrate.py from your own data; "
           "no vendor benchmark is used." % (len(answers), len(labels)), ""]
    sources = sorted({r["source"] for r in log_rows})
    if "mock" in sources:
        out += ["WARNING: the log contains mock rows from --dry-run. Their numbers are meaningless.", ""]
    for qid, q in questions.items():
        out += ["## %s (%s)" % (qid, q["type"]), ""]
        used, skipped = [], 0
        for item_id, norm in answers.items():
            lab = labels.get((item_id, qid))
            if lab is None:
                continue
            if qid not in norm:
                skipped += 1
                continue
            a = norm[qid]
            try:
                if q["type"] == "noul":
                    used.append((a["value"], parse_yes(lab)))
                elif q["type"] == "choice":
                    if lab not in q["criteria"]:
                        raise ValueError("label %r is not an option of %s" % (lab, qid))
                    used.append((a["value"], a["probs"].get(a["value"], 0.0), lab))
                else:
                    pred = int(max(a["probs"], key=a["probs"].get))
                    used.append((pred, a["value"], a["confidence"], int(lab)))
            except ValueError as exc:
                out += ["Label problem for item %s: %s" % (item_id, exc), ""]
        out.append("Labelled items used: %d. Labelled items with an error answer: %d." % (len(used), skipped))
        if len(used) < 50:
            out.append("")
            out.append("Sample is small (under 50). Read the tables as a rough view, not a measurement.")
        out.append("")
        if not used:
            out += ["No labelled items for this question.", ""]
            continue
        if q["type"] == "noul":
            out += noul_section(qid, used, thresholds_by_q.get(qid, {}), target)
        elif q["type"] == "choice":
            out += choice_section(qid, used, thresholds_by_q.get(qid, {}), target, option_orders.get(qid))
        else:
            out += score_section(qid, used, target)
        out.append("")
    # routing at the thresholds in the questions module now
    out += ["## Routing at the current thresholds", ""]
    counts, errors = {}, 0
    for item_id, norm in answers.items():
        if len(norm) != len(questions):
            errors += 1
            continue
        try:
            outcome = route(norm)[0]
        except Exception:
            outcome = "error"
        counts[outcome] = counts.get(outcome, 0) + 1
    total = sum(counts.values())
    out += md_table(["outcome", "items", "share"], [[k, v, pct(v, total)] for k, v in sorted(counts.items())])
    out += ["", "Items with an API error, not routed: %d." % errors,
            "Share sent to review: %s. This re-runs your route() on the logged answers, so it reflects edits to the "
            "thresholds made after the run." % pct(counts.get("review", 0), total)]
    decided = [r for r in log_rows if r["human_outcome"]]
    if decided:
        seen, agree = set(), 0
        for r in decided:
            if r["item_id"] in seen:
                continue
            seen.add(r["item_id"])
            agree += 1 if r["human_outcome"] == r["routed_outcome"] else 0
        out += ["", "Human outcome filled for %d items; it matches the logged routed outcome for %d (%s)."
                % (len(seen), agree, pct(agree, len(seen)))]
    tokens = sum(int(r["input_tokens"]) for r in log_rows if r["input_tokens"] not in ("", None))
    out += ["", "## Cost", "",
            "Input tokens in the log: %d. At %.4f USD per million input tokens that is %.6f USD "
            "(output tokens were free in the docs checked 2026-11-15). Check your vendor console for the real bill."
            % (tokens, price, tokens * price / 1e6), ""]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--questions", required=True, help="the same questions module used for the run")
    ap.add_argument("--out", default="report.md")
    ap.add_argument("--target-precision", type=float, default=0.9,
                    help="precision or accuracy you want at the threshold (default 0.9, your decision)")
    ap.add_argument("--price-per-million", type=float, default=DEFAULT_PRICE_PER_MILLION)
    args = ap.parse_args(argv)
    ns = runpy.run_path(args.questions)
    questions = ns["QUESTIONS"]
    raw = ns.get("THRESHOLDS", {})
    thresholds_by_q = ns.get("CALIBRATION_THRESHOLDS")
    if thresholds_by_q is None:
        thresholds_by_q = {q: {"low": raw.get("hazard_low"), "high": raw.get("hazard_high")}
                           for q in ns.get("HAZARDS", [])}
    option_orders = {q: list(v["criteria"]) for q, v in questions.items() if v["type"] == "choice"}
    report = build_report(read_csv(args.log), read_csv(args.labels), questions, ns["route"],
                          thresholds_by_q, args.target_precision, args.price_per_million, option_orders)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(report)
    print("report written to %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
