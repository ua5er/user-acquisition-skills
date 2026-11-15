#!/usr/bin/env python3
"""Tag competitor creative descriptions with Jev and write a tagged dataset.

Claude writes one description per creative (descriptions.jsonl). This script
sends each description of one track (static or video) to Jev with that track's
question set, applies the thresholds in code and writes:

  tags-<track>.jsonl          one record per creative: tags, flags, scores,
                              every probability, the model id that answered
  review-queue-<track>.csv    items a person decides (review band, conflicts,
                              untagged), with an empty human_label column
  run-<track>.json            requests, input tokens reported by the API, cost
  order-check-<track>.json    only with --order-check: first-option bias test

Python 3 standard library only. The one network call is a POST to the vendor
endpoint (default https://api.typesafe.ai/v1/systemone) or a gateway you name.
The key is read only from the environment (TYPESAFE_API_KEY, or --key-env).
An API or shape error marks the creative as "error": errors never become tags.

Examples:
  python3 tag_creatives.py sample_market/descriptions.jsonl --track static --dry-run --out-dir out
  python3 tag_creatives.py descriptions.jsonl --track video --smoke --data-handling-confirmed
  python3 tag_creatives.py descriptions.jsonl --track video --questions markets/ai_photo_editor/questions_video.py \\
      --confirm-pass --data-handling-confirmed
  python3 tag_creatives.py descriptions.jsonl --track static --max-usd 0.50 --order-check 6 \\
      --data-handling-confirmed --out-dir parsed-market/2026-11-15-sleep
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import runpy
import sys
import time
from urllib import error, request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BASE_URL = "https://api.typesafe.ai"
ENDPOINT_PATH = "/v1/systemone"
ENV_KEY = "TYPESAFE_API_KEY"
# $42 per billion input tokens, output free (docs.typesafe.ai/models.md, checked 2026-11-15).
DEFAULT_PRICE_PER_MILLION = 0.042
RETRY_STATUS = {429, 529}
QUESTION_TYPES = {"noul", "choice", "score"}
DEFAULT_QUESTIONS = {"static": "questions_static.py", "video": "questions_video.py"}
QUEUE_COLUMNS = ["creative_id", "track", "question_id", "kind", "reason", "model_answer", "probability",
                 "runner_up", "runner_up_probability", "companion_probability", "confirm_probability", "priority",
                 "human_label"]


class ApiError(Exception):
    """Request failed. The message never contains the API key."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class ResponseShapeError(Exception):
    """Response did not match the documented shape."""


# ------------------------------------------------------------------ inputs

def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except ValueError as exc:
                    raise ValueError("%s line %d is not valid JSON: %s" % (path, n, exc))
    return rows


def load_question_set(path):
    ns = runpy.run_path(path)
    for needed in ("TRACK", "QUESTIONS", "CHOICE_COMPANION", "FLAGS", "SCORES", "build_state", "code_features"):
        if needed not in ns:
            raise ValueError("%s must define %s" % (path, needed))
    validate_question_set(ns)
    return ns


def validate_question_set(ns):
    qs = ns["QUESTIONS"]
    if not isinstance(qs, dict) or not qs:
        raise ValueError("QUESTIONS must be a non-empty dict")
    for qid, q in qs.items():
        qtype = q.get("type")
        if qtype not in QUESTION_TYPES:
            raise ValueError("%s: type must be one of %s" % (qid, sorted(QUESTION_TYPES)))
        crit = q.get("criteria")
        if qtype == "choice":
            if not isinstance(crit, dict) or not 2 <= len(crit) <= 255:
                raise ValueError("%s: choice criteria must be a dict of 2 to 255 options" % qid)
            if list(crit)[-1] != "other":
                raise ValueError("%s: the last choice option must be 'other'" % qid)
            if qid not in ns["CHOICE_COMPANION"]:
                raise ValueError("%s: every choice needs a companion yes/no in CHOICE_COMPANION" % qid)
        elif qtype == "score":
            if not isinstance(crit, list) or not 2 <= len(crit) <= 10:
                raise ValueError("%s: score criteria must be an ordered list of 2 to 10 levels" % qid)
        elif crit is not None and (not isinstance(crit, dict) or not set(crit) <= {"true", "false"}):
            raise ValueError("%s: noul criteria may only have the keys true and false" % qid)
    for choice, comp in ns["CHOICE_COMPANION"].items():
        if qs.get(choice, {}).get("type") != "choice" or qs.get(comp, {}).get("type") != "noul":
            raise ValueError("companion pair %s -> %s must be choice -> noul" % (choice, comp))
    for qid in ns["FLAGS"]:
        if qs.get(qid, {}).get("type") != "noul":
            raise ValueError("flag %s must be a noul question" % qid)
    for qid in ns["SCORES"]:
        if qs.get(qid, {}).get("type") != "score":
            raise ValueError("score %s must be a score question" % qid)


def thresholds(ns):
    t = dict({"tag": 0.70, "review_low": 0.35}, **ns.get("THRESHOLDS", {}))
    if not 0 < t["review_low"] < t["tag"] <= 1:
        raise ValueError("thresholds need 0 < review_low < tag <= 1")
    return t


# ------------------------------------------------------- option order rotation

def rotation_offset(creative_id, qid, n_options):
    """Deterministic per creative and question, so a rerun sends the same order."""
    movable = n_options - 1  # "other" never moves
    if movable <= 1:
        return 0
    return int(hashlib.sha256(("%s|%s" % (creative_id, qid)).encode("utf-8")).hexdigest(), 16) % movable


def rotated_questions(questions, creative_id, rotate=True, reverse=False):
    """Copy of the question set with Choice options rotated (or reversed), 'other' kept last."""
    out, offsets = {}, {}
    for qid, q in questions.items():
        if q["type"] != "choice":
            out[qid] = q
            continue
        names = [k for k in q["criteria"] if k != "other"]
        if reverse:
            names = names[::-1]
            offsets[qid] = "reversed"
        elif rotate:
            k = rotation_offset(creative_id, qid, len(q["criteria"]))
            names = names[k:] + names[:k]
            offsets[qid] = k
        else:
            offsets[qid] = 0
        crit = {n: q["criteria"][n] for n in names}
        crit["other"] = q["criteria"]["other"]
        out[qid] = dict(q, criteria=crit)
    return out, offsets


# ------------------------------------------------------------ network calls

def estimate_input_tokens(body):
    """Rough guess (characters divided by 4) used only by the spend guard."""
    return max(1, math.ceil(len(json.dumps(body, ensure_ascii=False)) / 4))


def post_json(url, key, body, timeout=60):
    """Return (status, payload, headers). Raises URLError on a network failure."""
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "User-Agent": "competitor-creative-parser/1.0",
    })
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status, headers = resp.status, dict(resp.headers)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status, headers = exc.code, dict(exc.headers or {})
    try:
        payload = json.loads(raw)
    except ValueError:
        payload = {"detail": raw[:300]}
    return status, payload, headers


def call_with_retry(post, url, key, body, retries=4, sleep=time.sleep, rng=random.random):
    """Retry 429, 529 and network errors with exponential backoff; honour a numeric Retry-After."""
    last = "no attempt made"
    for attempt in range(retries + 1):
        headers = {}
        try:
            status, payload, headers = post(url, key, body, 60)
        except (error.URLError, TimeoutError, OSError) as exc:
            last = "network error: %s" % type(exc).__name__
        else:
            if status == 200:
                return payload
            detail = json.dumps(payload.get("detail", payload))[:200] if isinstance(payload, dict) else ""
            last = "HTTP %s %s" % (status, detail)
            if status not in RETRY_STATUS:
                raise ApiError(last, status)
        if attempt < retries:
            wait = min(30.0, 2.0 ** attempt + rng())
            retry_after = {k.lower(): v for k, v in headers.items()}.get("retry-after")
            try:
                wait = min(60.0, max(wait, float(retry_after)))
            except (TypeError, ValueError):
                pass
            sleep(wait)
    raise ApiError("gave up after %d retries (%s)" % (retries, last))


def _num01(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 1


def parse_response(resp, questions):
    """Check the documented response shape. Returns (answers, input_tokens, model)."""
    if not isinstance(resp, dict) or not isinstance(resp.get("answers"), dict):
        raise ResponseShapeError("no answers object")
    out = {}
    for qid, q in questions.items():
        a = resp["answers"].get(qid)
        if not isinstance(a, dict) or a.get("type") != q["type"]:
            raise ResponseShapeError("%s: answer missing or of the wrong type" % qid)
        if q["type"] == "noul":
            if not _num01(a.get("noul")):
                raise ResponseShapeError("%s: noul must be a number from 0 to 1" % qid)
            out[qid] = {"type": "noul", "p_yes": round(float(a["noul"]), 4)}
            continue
        probs = a.get("probabilities")
        if not _num01(a.get("confidence")) or not isinstance(probs, dict) or not probs \
                or not all(_num01(v) for v in probs.values()):
            raise ResponseShapeError("%s: confidence or probabilities out of shape" % qid)
        probs = {str(k): round(float(v), 4) for k, v in probs.items()}
        if q["type"] == "choice":
            if a.get("choice") not in q["criteria"]:
                raise ResponseShapeError("%s: choice is not one of the options" % qid)
            out[qid] = {"type": "choice", "choice": a["choice"], "probabilities": probs,
                        "confidence": round(float(a["confidence"]), 4)}
        else:
            s = a.get("score")
            if not isinstance(s, (int, float)) or isinstance(s, bool):
                raise ResponseShapeError("%s: score must be a number" % qid)
            out[qid] = {"type": "score", "score": round(float(s), 4), "probabilities": probs,
                        "confidence": round(float(a["confidence"]), 4)}
    usage = resp.get("usage") if isinstance(resp.get("usage"), dict) else {}
    return out, int(usage.get("input_tokens") or 0), resp.get("model")


# ------------------------------------------------------------- offline mock

def mock_response(body):
    """Deterministic stand-in shaped like the documented response. Numbers are meaningless."""
    state = json.dumps(body["state"], sort_keys=True, ensure_ascii=False)
    answers = {}
    for qid, q in body["questions"].items():
        rng = random.Random(int(hashlib.sha256((state + "|" + qid).encode("utf-8")).hexdigest(), 16))
        if q["type"] == "noul":
            answers[qid] = {"type": "noul", "noul": round(rng.random(), 3)}
            continue
        names = list(q["criteria"]) if q["type"] == "choice" else [str(i) for i in range(len(q["criteria"]))]
        weights = [(rng.random() + 0.02) ** 4 for _ in names]
        probs = {n: w / sum(weights) for n, w in zip(names, weights)}
        top = max(probs, key=probs.get)
        conf = max(0.0, (probs[top] - 1.0 / len(names)) / (1.0 - 1.0 / len(names)))
        if q["type"] == "choice":
            answers[qid] = {"type": "choice", "choice": top, "confidence": round(conf, 3), "probabilities": probs}
        else:
            answers[qid] = {"type": "score", "score": sum(int(k) * v for k, v in probs.items()),
                            "confidence": round(conf, 3), "probabilities": probs,
                            "legend": {str(i): d for i, d in enumerate(q["criteria"])}}
    return {"model": body["model"], "answers": answers,
            "usage": {"input_tokens": estimate_input_tokens(body), "output_tokens": 0}}


def mock_post(url, key, body, timeout=60):
    return 200, mock_response(body), {}


# --------------------------------------------------------------- decisions

def decide_choice(answer, companion_p, t, confirm_p=None):
    """Code decides. Returns (status, tag, reason). status: tagged, review, untagged.

    A tag needs two yes votes at or above the tag threshold: the Choice itself and a second
    yes/no. With the confirm pass the second vote is a separate question about the chosen
    option only (confirm_p); without it, the generic companion (companion_p).
    """
    top = answer["choice"]
    p = answer["probabilities"].get(top, 0.0)
    if p < t["review_low"]:
        return "untagged", None, "top option %s at %.2f is below %.2f" % (top, p, t["review_low"])
    if top == "other":
        if p >= t["tag"]:
            return "tagged", "other", "other at %.2f" % p
        return "review", None, "other at %.2f inside the review band" % p
    second, name = (confirm_p, "confirmation") if confirm_p is not None else (companion_p, "companion")
    if second <= t["review_low"]:
        return "review", None, "conflict: picked %s at %.2f but the %s says no (%.2f)" % (top, p, name, second)
    if p >= t["tag"] and second >= t["tag"]:
        return "tagged", top, "%s at %.2f, %s %.2f" % (top, p, name, second)
    return "review", None, "%s at %.2f, %s %.2f, inside the review band" % (top, p, name, second)


def confirm_questions(qs, answers, t):
    """Second pass: one yes/no per Choice about the option the model picked, in that option's own words."""
    out = {}
    for qid in qs["CHOICE_COMPANION"]:
        a = answers[qid]
        top = a["choice"]
        if top == "other" or a["probabilities"].get(top, 0.0) < t["review_low"]:
            continue
        q = qs["QUESTIONS"][qid]
        out["confirm_" + qid] = {
            "type": "noul",
            "instructions": 'Question: "%s" This description fits the ad: "%s"' % (q["instructions"],
                                                                                  q["criteria"][top]),
        }
    return out


def decide_flag(p, t):
    if p >= t["tag"]:
        return "yes"
    if p <= t["review_low"]:
        return "no"
    return "review"


def runner_up(probs, top):
    rest = sorted(((v, k) for k, v in probs.items() if k != top), reverse=True)
    return (rest[0][1], rest[0][0]) if rest else ("", "")


def decide_creative(qs, answers, t):
    """Turn raw answers into tags, flags, scores and review rows."""
    tags, flags, scores, queue = {}, {}, {}, []
    for qid, comp in qs["CHOICE_COMPANION"].items():
        a = answers[qid]
        cp = answers[comp]["p_yes"]
        conf = answers.get("confirm_" + qid, {}).get("p_yes")
        status, tag, reason = decide_choice(a, cp, t, conf)
        tags[qid] = {"status": status, "value": tag, "model_choice": a["choice"],
                     "p": a["probabilities"].get(a["choice"]), "companion_p": cp, "confirm_p": conf,
                     "reason": reason}
        if status != "tagged":
            ru, rp = runner_up(a["probabilities"], a["choice"])
            queue.append({"question_id": qid, "kind": "choice", "reason": reason, "model_answer": a["choice"],
                          "probability": a["probabilities"].get(a["choice"]), "runner_up": ru,
                          "runner_up_probability": rp, "companion_probability": cp, "confirm_probability": conf,
                          "priority": "normal" if status == "review" else "low"})
    for qid in qs["FLAGS"]:
        p = answers[qid]["p_yes"]
        verdict = decide_flag(p, t)
        flags[qid] = {"value": verdict, "p_yes": p}
        if verdict == "review":
            queue.append({"question_id": qid, "kind": "flag", "reason": "yes probability %.2f inside %.2f to %.2f"
                          % (p, t["review_low"], t["tag"]), "model_answer": "yes" if p >= 0.5 else "no",
                          "probability": p, "runner_up": "", "runner_up_probability": "",
                          "companion_probability": "", "priority": "high" if qid == "risky_claim" else "normal"})
    for qid in qs["SCORES"]:
        a = answers[qid]
        levels = qs["QUESTIONS"][qid]["criteria"]
        level = min(len(levels) - 1, max(0, int(round(a["score"]))))
        scores[qid] = {"score": a["score"], "level": level, "level_text": levels[level],
                       "confidence": a["confidence"]}
    return tags, flags, scores, queue


# ------------------------------------------------------------------ the run

def run(descriptions, qs, post, *, base_url=DEFAULT_BASE_URL, key="", model=None, max_usd=0.5,
        price=DEFAULT_PRICE_PER_MILLION, rotate=True, order_check=0, source="live", retries=4,
        sleep=time.sleep, log=print, confirm_pass=False):
    """One request per creative with all questions. Returns (records, queue_rows, summary, order_rows)."""
    t = thresholds(qs)
    model = model or qs.get("MODEL", "jev-1.14.0")
    url = base_url.rstrip("/") + ENDPOINT_PATH
    track = qs["TRACK"]
    records, queue_rows, order_rows = [], [], []
    summary = {"track": track, "source": source, "model_requested": model, "creatives": 0, "tagged_ok": 0,
               "errors": 0, "skipped_by_guard": 0, "requests": 0, "input_tokens": 0, "est_usd": 0.0,
               "thresholds": t, "taxonomy_version": qs.get("TAXONOMY_VERSION"), "rotation": rotate,
               "confirm_pass": confirm_pass, "decisions": 0}
    spent = 0.0

    def send(body):
        nonlocal spent
        summary["requests"] += 1
        payload = call_with_retry(post, url, key, body, retries=retries, sleep=sleep)
        answers, tokens, answered = parse_response(payload, body["questions"])
        summary["input_tokens"] += tokens
        spent += tokens * price / 1e6
        return answers, tokens, answered

    for index, d in enumerate(descriptions):
        cid = str(d.get("creative_id") or "row-%d" % (index + 1))
        state = qs["build_state"](d)
        questions, offsets = rotated_questions(qs["QUESTIONS"], cid, rotate=rotate)
        body = {"model": model, "state": state, "questions": questions}
        extra = (1 if index < order_check else 0) + (1 if confirm_pass else 0)
        projected = estimate_input_tokens(body) * (1 + extra) * price / 1e6
        if spent + projected > max_usd:
            summary["skipped_by_guard"] = len(descriptions) - index
            log("spend guard: stopped before %s (spent about %.6f, next about %.6f, limit %.2f USD)"
                % (cid, spent, projected, max_usd))
            break
        summary["creatives"] += 1
        rec = {"creative_id": cid, "track": track, "source": source, "model": None,
               "taxonomy_version": qs.get("TAXONOMY_VERSION"), "option_order": offsets,
               "features": qs["code_features"](d), "status": "ok", "error": None,
               "tags": {}, "flags": {}, "scores": {}, "answers": {}, "input_tokens": 0}
        try:
            answers, tokens, answered = send(body)
        except (ApiError, ResponseShapeError) as exc:
            rec.update(status="error", error=str(exc)[:200])
            summary["errors"] += 1
            queue_rows.append({"creative_id": cid, "track": track, "question_id": "(all)", "kind": "error",
                               "reason": rec["error"], "model_answer": "", "probability": "", "runner_up": "",
                               "runner_up_probability": "", "companion_probability": "", "priority": "high",
                               "human_label": ""})
            records.append(rec)
            continue
        if confirm_pass:
            cq = confirm_questions(qs, answers, t)
            if cq:
                try:
                    c_answers, c_tokens, _ = send({"model": model, "state": state, "questions": cq})
                    answers.update(c_answers)
                    tokens += c_tokens
                except (ApiError, ResponseShapeError) as exc:
                    log("confirm pass failed for %s (%s): the generic companion decides" % (cid, str(exc)[:80]))
        summary["decisions"] += len(answers)
        rec.update(model=answered or model, answers=answers, input_tokens=tokens)
        rec["tags"], rec["flags"], rec["scores"], queue = decide_creative(qs, answers, t)
        for row in queue:
            row.update(creative_id=cid, track=track, human_label="")
            queue_rows.append(row)
        summary["tagged_ok"] += 1
        records.append(rec)
        if index < order_check:
            rev_q, _ = rotated_questions({k: v for k, v in qs["QUESTIONS"].items() if v["type"] == "choice"},
                                         cid, reverse=True)
            try:
                rev, _, _ = send({"model": model, "state": state, "questions": rev_q})
            except (ApiError, ResponseShapeError) as exc:
                order_rows.append({"creative_id": cid, "error": str(exc)[:200]})
                continue
            for qid in rev_q:
                order_rows.append({"creative_id": cid, "question_id": qid,
                                   "rotated_choice": answers[qid]["choice"], "reversed_choice": rev[qid]["choice"],
                                   "same": answers[qid]["choice"] == rev[qid]["choice"]})
    summary["est_usd"] = round(summary["input_tokens"] * price / 1e6, 6)
    summary["price_per_million"] = price
    summary["review_rows"] = len(queue_rows)
    return records, queue_rows, summary, order_rows


def order_check_report(order_rows):
    by_q = {}
    for r in order_rows:
        if "question_id" in r:
            s = by_q.setdefault(r["question_id"], {"pairs": 0, "same": 0})
            s["pairs"] += 1
            s["same"] += 1 if r["same"] else 0
    for s in by_q.values():
        s["agreement"] = round(s["same"] / s["pairs"], 3) if s["pairs"] else None
    return {"note": "Same creative asked twice with Choice options in a rotated and a reversed order. "
                    "Low agreement means option order moves the answer: rewrite the options or keep "
                    "more of that question in review.", "per_question": by_q, "rows": order_rows}


def write_outputs(out_dir, track, records, queue_rows, summary, order_rows):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "tags-%s.jsonl" % track), "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(out_dir, "review-queue-%s.csv" % track), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=QUEUE_COLUMNS)
        w.writeheader()
        for row in queue_rows:
            w.writerow({k: row.get(k, "") for k in QUEUE_COLUMNS})
    with open(os.path.join(out_dir, "run-%s.json" % track), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    if order_rows:
        with open(os.path.join(out_dir, "order-check-%s.json" % track), "w", encoding="utf-8") as fh:
            json.dump(order_check_report(order_rows), fh, indent=1, sort_keys=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("descriptions", help="descriptions.jsonl written by Claude, one creative per line")
    ap.add_argument("--track", required=True, choices=["static", "video"])
    ap.add_argument("--questions", help="question set module (default questions_<track>.py next to this script)")
    ap.add_argument("--out-dir", default=".", help="folder for tags, review queue and run files")
    ap.add_argument("--model", help="override the pinned model id")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="https base URL; %s is appended. For a gateway, also set --key-env and --model" % ENDPOINT_PATH)
    ap.add_argument("--key-env", default=ENV_KEY, help="name of the environment variable holding the key")
    ap.add_argument("--dry-run", action="store_true", help="offline deterministic mock, no network, no key")
    ap.add_argument("--smoke", action="store_true", help="live run on the first 3 creatives with a shape check")
    ap.add_argument("--max-items", type=int, default=0, help="only the first N creatives of the track")
    ap.add_argument("--max-usd", type=float, default=0.50, help="spend guard in USD (default 0.50)")
    ap.add_argument("--price-per-million", type=float, default=DEFAULT_PRICE_PER_MILLION)
    ap.add_argument("--order-check", type=int, default=0,
                    help="ask the Choice questions again in reversed order for the first N creatives")
    ap.add_argument("--no-rotate", action="store_true", help="send options in the module's order")
    ap.add_argument("--confirm-pass", action="store_true",
                    help="second request per creative: one yes/no about each chosen option; it replaces the "
                         "generic companion as the second vote")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--data-handling-confirmed", action="store_true",
                    help="required for live runs: the user decided these descriptions may go to the vendor")
    args = ap.parse_args(argv)

    if not args.base_url.lower().startswith("https://"):
        print("refusing a base URL that is not https", file=sys.stderr)
        return 2
    qs = load_question_set(args.questions or os.path.join(HERE, DEFAULT_QUESTIONS[args.track]))
    if qs["TRACK"] != args.track:
        print("question set is for track %s, not %s" % (qs["TRACK"], args.track), file=sys.stderr)
        return 2
    items = [d for d in load_jsonl(args.descriptions) if d.get("format") == args.track]
    limit = 3 if args.smoke else args.max_items
    if limit:
        items = items[:limit]
    if not items:
        print("no %s descriptions found" % args.track, file=sys.stderr)
        return 2

    key, post, source = "", mock_post, "mock"
    if args.dry_run:
        print("DRY RUN: offline mock answers, no network, no key. The tags are meaningless.")
    else:
        key = os.environ.get(args.key_env, "")
        if not key:
            print("set %s in the environment, or use --dry-run" % args.key_env, file=sys.stderr)
            return 2
        if not args.data_handling_confirmed:
            print("live run refused: confirm with the user that these descriptions may be sent to the vendor, "
                  "then pass --data-handling-confirmed", file=sys.stderr)
            return 2
        post, source = post_json, "live"

    records, queue_rows, summary, order_rows = run(
        items, qs, post, base_url=args.base_url, key=key, model=args.model, max_usd=args.max_usd,
        price=args.price_per_million, rotate=not args.no_rotate, order_check=args.order_check, confirm_pass=args.confirm_pass,
        source=source, retries=args.retries)
    write_outputs(args.out_dir, args.track, records, queue_rows, summary, order_rows)
    print("track %s: %d creatives sent, %d tagged, %d errors, %d skipped by the spend guard, %d requests"
          % (args.track, summary["creatives"], summary["tagged_ok"], summary["errors"],
             summary["skipped_by_guard"], summary["requests"]))
    print("%s: %d, cost %.6f USD at %.3f USD per million%s" % (
        "input tokens (mock estimate, nothing billed)" if source == "mock" else "input tokens reported by the API",
        summary["input_tokens"], summary["est_usd"], args.price_per_million,
        "" if source == "mock" else "; the vendor console has the real bill"))
    print("review queue rows: %d, written to %s" % (len(queue_rows), args.out_dir))
    if order_rows:
        rep = order_check_report(order_rows)["per_question"]
        print("order check agreement: " + ", ".join("%s %s" % (q, v["agreement"]) for q, v in sorted(rep.items())))
    if args.smoke:
        ok = summary["errors"] == 0 and summary["tagged_ok"] > 0
        print("SMOKE %s%s" % ("PASSED" if ok else "FAILED", " (mock, proves nothing about the API)" if source == "mock" else ""))
        return 0 if ok else 1
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
