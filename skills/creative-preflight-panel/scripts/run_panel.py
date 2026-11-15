#!/usr/bin/env python3
"""Show every concept to every buyer profile through Jev and log typed answers.

Inputs: concepts.jsonl (written by market-to-creative-brief's brief_pack.py
with --panel-concepts) and profiles.jsonl (written by Claude from the team's
ICP notes and the snapshot's audience signals). One request per concept and
profile pair, with the track's question set (questions_static.py or
questions_video.py): a Choice (scroll, stop, click) with rotated option order,
three yes/no questions and a fit Score. Writes:

  answers-<track>.jsonl      one row per pair: answers with probabilities,
                             option order, model id, tokens, status
  run-<track>.json           pairs, requests, input tokens reported by the API, cost
  order-check-<track>.json   only with --order-check: the Choice re-asked in
                             reversed order, agreement per item

Then run panel_matrix.py. Python 3 standard library only. The one network
call is a POST to the vendor endpoint (default https://api.typesafe.ai/v1/systemone)
or a gateway you name. The key is read only from the environment
(TYPESAFE_API_KEY, or --key-env). An API or shape error marks the pair as
"error"; errors never count as answers.

Examples:
  python3 run_panel.py --concepts sample_panel/concepts.jsonl --profiles sample_panel/profiles.jsonl \\
      --track static --dry-run --out-dir out
  python3 run_panel.py --concepts concepts.jsonl --profiles profiles.jsonl --track video --smoke \\
      --data-handling-confirmed
  python3 run_panel.py --concepts concepts.jsonl --profiles profiles.jsonl --track video \\
      --order-check 12 --max-usd 0.25 --data-handling-confirmed --out-dir panel
"""
import argparse
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
    for needed in ("TRACK", "QUESTIONS", "ACTION", "ENGAGE_OPTIONS", "FLAGS", "FIT", "THRESHOLDS",
                   "build_items", "build_state"):
        if needed not in ns:
            raise ValueError("%s must define %s" % (path, needed))
    validate_question_set(ns)
    return ns


def validate_question_set(ns):
    qs = ns["QUESTIONS"]
    for qid, q in qs.items():
        if q.get("type") not in QUESTION_TYPES:
            raise ValueError("%s: type must be one of %s" % (qid, sorted(QUESTION_TYPES)))
    action = qs.get(ns["ACTION"], {})
    if action.get("type") != "choice" or not isinstance(action.get("criteria"), dict):
        raise ValueError("ACTION must name a choice question")
    if not set(ns["ENGAGE_OPTIONS"]) < set(action["criteria"]):
        raise ValueError("ENGAGE_OPTIONS must be a strict subset of the action options")
    for qid in ns["FLAGS"]:
        if qs.get(qid, {}).get("type") != "noul":
            raise ValueError("flag %s must be a noul question" % qid)
    fit = qs.get(ns["FIT"], {})
    if fit.get("type") != "score" or not isinstance(fit.get("criteria"), list) or not 2 <= len(fit["criteria"]) <= 10:
        raise ValueError("FIT must name a score question with 2 to 10 levels")
    t = ns["THRESHOLDS"]
    if not 0 < t["review_low"] < t["tag"] <= 1:
        raise ValueError("thresholds need 0 < review_low < tag <= 1")


def validate_profiles(profiles):
    seen = set()
    for p in profiles:
        pid = p.get("profile_id")
        if not pid or pid in seen:
            raise ValueError("every profile needs a unique profile_id (problem at %r)" % pid)
        seen.add(pid)
        for f in ("situation", "goal", "objections", "stops_scrolling_for"):
            if not p.get(f):
                raise ValueError("profile %s: %s is empty" % (pid, f))


# ------------------------------------------------------- option order rotation

def rotated_choice(q, pair_key, reverse=False):
    """Rotate (or reverse) the options of a choice question, deterministic per pair."""
    names = list(q["criteria"])
    if reverse:
        names, offset = names[::-1], "reversed"
    else:
        offset = int(hashlib.sha256(pair_key.encode("utf-8")).hexdigest(), 16) % len(names)
        names = names[offset:] + names[:offset]
    return dict(q, criteria={n: q["criteria"][n] for n in names}), offset


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
        "User-Agent": "creative-preflight-panel/1.0",
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
        names = sorted(q["criteria"]) if q["type"] == "choice" else [str(i) for i in range(len(q["criteria"]))]
        weights = [(rng.random() + 0.02) ** 3 for _ in names]
        probs = {n: w / sum(weights) for n, w in zip(names, weights)}
        top = max(probs, key=probs.get)
        conf = max(0.0, (probs[top] - 1.0 / len(names)) / (1.0 - 1.0 / len(names)))
        if q["type"] == "choice":
            answers[qid] = {"type": "choice", "choice": top, "confidence": round(conf, 3), "probabilities": probs}
        else:
            answers[qid] = {"type": "score", "score": sum(int(k) * v for k, v in probs.items()),
                            "confidence": round(conf, 3), "probabilities": probs}
    return {"model": body["model"], "answers": answers,
            "usage": {"input_tokens": estimate_input_tokens(body), "output_tokens": 0}}


def mock_post(url, key, body, timeout=60):
    return 200, mock_response(body), {}


# --------------------------------------------------------------------- run

def build_pairs(concepts, profiles, qs):
    pairs = []
    for c in concepts:
        if c.get("track") != qs["TRACK"]:
            continue
        for item_id, ad in qs["build_items"](c):
            for p in profiles:
                pairs.append({"item_id": item_id, "concept_id": c["concept_id"], "profile_id": p["profile_id"],
                              "state": qs["build_state"](p, ad)})
    return pairs


def run(pairs, qs, post, *, base_url=DEFAULT_BASE_URL, key="", model=None, max_usd=0.25,
        price=DEFAULT_PRICE_PER_MILLION, order_check=0, source="live", retries=4, sleep=time.sleep, log=print):
    """One request per pair with all questions. Returns (records, summary, order_rows)."""
    model = model or qs.get("MODEL", "jev-1.14.0")
    url = base_url.rstrip("/") + ENDPOINT_PATH
    track, action = qs["TRACK"], qs["ACTION"]
    records, order_rows = [], []
    summary = {"track": track, "source": source, "model_requested": model, "pairs": 0, "answered": 0,
               "errors": 0, "skipped_by_guard": 0, "requests": 0, "input_tokens": 0, "est_usd": 0.0,
               "panel_version": qs.get("PANEL_VERSION"), "thresholds": qs["THRESHOLDS"],
               "items": len({p["item_id"] for p in pairs}), "profiles": len({p["profile_id"] for p in pairs})}
    spent = 0.0

    def send(body):
        nonlocal spent
        summary["requests"] += 1
        payload = call_with_retry(post, url, key, body, retries=retries, sleep=sleep)
        answers, tokens, answered = parse_response(payload, body["questions"])
        summary["input_tokens"] += tokens
        spent += tokens * price / 1e6
        return answers, tokens, answered

    for index, pair in enumerate(pairs):
        pair_key = "%s|%s" % (pair["item_id"], pair["profile_id"])
        questions = dict(qs["QUESTIONS"])
        questions[action], offset = rotated_choice(qs["QUESTIONS"][action], pair_key)
        body = {"model": model, "state": pair["state"], "questions": questions}
        extra = 1 if index < order_check else 0
        projected = estimate_input_tokens(body) * (1 + extra) * price / 1e6
        if spent + projected > max_usd:
            summary["skipped_by_guard"] = len(pairs) - index
            log("spend guard: stopped before %s (spent about %.6f, next about %.6f, limit %.2f USD)"
                % (pair_key, spent, projected, max_usd))
            break
        summary["pairs"] += 1
        rec = {"item_id": pair["item_id"], "concept_id": pair["concept_id"], "profile_id": pair["profile_id"],
               "track": track, "source": source, "model": None, "panel_version": qs.get("PANEL_VERSION"),
               "option_order": offset, "status": "ok", "error": None, "answers": {}, "input_tokens": 0}
        try:
            answers, tokens, answered = send(body)
        except (ApiError, ResponseShapeError) as exc:
            rec.update(status="error", error=str(exc)[:200])
            summary["errors"] += 1
            records.append(rec)
            continue
        rec.update(model=answered or model, answers=answers, input_tokens=tokens)
        summary["answered"] += 1
        records.append(rec)
        if extra:
            rev_q, _ = rotated_choice(qs["QUESTIONS"][action], pair_key, reverse=True)
            try:
                rev, _, _ = send({"model": model, "state": pair["state"], "questions": {action: rev_q}})
            except (ApiError, ResponseShapeError) as exc:
                order_rows.append({"item_id": pair["item_id"], "profile_id": pair["profile_id"],
                                   "error": str(exc)[:200]})
                continue
            order_rows.append({"item_id": pair["item_id"], "profile_id": pair["profile_id"],
                               "rotated_choice": answers[action]["choice"], "reversed_choice": rev[action]["choice"],
                               "same": answers[action]["choice"] == rev[action]["choice"]})
    summary["est_usd"] = round(summary["input_tokens"] * price / 1e6, 6)
    summary["price_per_million"] = price
    return records, summary, order_rows


def order_check_report(order_rows):
    ok = [r for r in order_rows if "same" in r]
    same = sum(1 for r in ok if r["same"])
    return {"note": "The action Choice asked twice for the same pair, options rotated and reversed. "
                    "Low agreement means option order moves the answer: keep those pairs in review "
                    "or rewrite the options.",
            "pairs": len(ok), "same": same, "agreement": round(same / len(ok), 3) if ok else None,
            "rows": order_rows}


def write_outputs(out_dir, track, records, summary, order_rows):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "answers-%s.jsonl" % track), "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(out_dir, "run-%s.json" % track), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    if order_rows:
        with open(os.path.join(out_dir, "order-check-%s.json" % track), "w", encoding="utf-8") as fh:
            json.dump(order_check_report(order_rows), fh, indent=1, sort_keys=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--concepts", required=True, help="concepts.jsonl from brief_pack.py --panel-concepts")
    ap.add_argument("--profiles", required=True, help="profiles.jsonl written by Claude")
    ap.add_argument("--track", required=True, choices=["static", "video"])
    ap.add_argument("--questions", help="question set module (default questions_<track>.py next to this script)")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--model", help="override the pinned model id")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="https base URL; %s is appended. For a gateway, also set --key-env and --model" % ENDPOINT_PATH)
    ap.add_argument("--key-env", default=ENV_KEY, help="name of the environment variable holding the key")
    ap.add_argument("--dry-run", action="store_true", help="offline deterministic mock, no network, no key")
    ap.add_argument("--smoke", action="store_true", help="live run on the first 3 pairs with a shape check")
    ap.add_argument("--max-pairs", type=int, default=0, help="only the first N pairs")
    ap.add_argument("--max-usd", type=float, default=0.25, help="spend guard in USD (default 0.25)")
    ap.add_argument("--price-per-million", type=float, default=DEFAULT_PRICE_PER_MILLION)
    ap.add_argument("--order-check", type=int, default=0,
                    help="re-ask the action Choice in reversed order for the first N pairs")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--data-handling-confirmed", action="store_true",
                    help="required for live runs: the user decided these concepts and profiles may go to the vendor")
    args = ap.parse_args(argv)

    if not args.base_url.lower().startswith("https://"):
        print("refusing a base URL that is not https", file=sys.stderr)
        return 2
    qs = load_question_set(args.questions or os.path.join(HERE, DEFAULT_QUESTIONS[args.track]))
    if qs["TRACK"] != args.track:
        print("question set is for track %s, not %s" % (qs["TRACK"], args.track), file=sys.stderr)
        return 2
    profiles = load_jsonl(args.profiles)
    validate_profiles(profiles)
    pairs = build_pairs(load_jsonl(args.concepts), profiles, qs)
    limit = 3 if args.smoke else args.max_pairs
    if limit:
        pairs = pairs[:limit]
    if not pairs:
        print("no %s concepts found" % args.track, file=sys.stderr)
        return 2

    key, post, source = "", mock_post, "mock"
    if args.dry_run:
        print("DRY RUN: offline mock answers, no network, no key. The answers are meaningless.")
    else:
        key = os.environ.get(args.key_env, "")
        if not key:
            print("set %s in the environment, or use --dry-run" % args.key_env, file=sys.stderr)
            return 2
        if not args.data_handling_confirmed:
            print("live run refused: confirm with the user that these concepts and profiles may be sent to the "
                  "vendor, then pass --data-handling-confirmed", file=sys.stderr)
            return 2
        post, source = post_json, "live"

    records, summary, order_rows = run(pairs, qs, post, base_url=args.base_url, key=key, model=args.model,
                                       max_usd=args.max_usd, price=args.price_per_million,
                                       order_check=args.order_check, source=source, retries=args.retries)
    write_outputs(args.out_dir, args.track, records, summary, order_rows)
    print("track %s: %d items x %d profiles, %d pairs sent, %d answered, %d errors, %d skipped by the spend guard, "
          "%d requests" % (args.track, summary["items"], summary["profiles"], summary["pairs"], summary["answered"],
                           summary["errors"], summary["skipped_by_guard"], summary["requests"]))
    print("%s: %d, cost %.6f USD at %.3f USD per million%s" % (
        "input tokens (mock estimate, nothing billed)" if source == "mock" else "input tokens reported by the API",
        summary["input_tokens"], summary["est_usd"], args.price_per_million,
        "" if source == "mock" else "; the vendor console has the real bill"))
    if order_rows:
        print("order check agreement: %s" % order_check_report(order_rows)["agreement"])
    if args.smoke:
        ok = summary["errors"] == 0 and summary["answered"] > 0
        print("SMOKE %s%s" % ("PASSED" if ok else "FAILED", " (mock, proves nothing about the API)" if source == "mock" else ""))
        return 0 if ok else 1
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
