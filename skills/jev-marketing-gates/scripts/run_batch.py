#!/usr/bin/env python3
"""Run a batch of items through typed questions and write log.csv.

Python 3 standard library only. The one network call is a POST to the vendor
endpoint (default https://api.typesafe.ai/v1/systemone). The API key is read
only from the environment (TYPESAFE_API_KEY, or the variable named by --key-env).

Request and response shapes follow the vendor docs as of 2026-11-15 and passed
a live check that day (Noul, Score and Choice on jev-1.14.0, direct endpoint).
Run with --smoke and your own key before your first real batch.

Examples:
  python3 run_batch.py sample_items.csv --questions questions_example.py --dry-run
  python3 run_batch.py items.csv --questions my_questions.py --smoke --data-handling-confirmed
  python3 run_batch.py items.csv --questions my_questions.py --max-usd 1 --data-handling-confirmed
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
import types
from urllib import error, request

DEFAULT_BASE_URL = "https://api.typesafe.ai"
ENDPOINT_PATH = "/v1/systemone"
ENV_KEY = "TYPESAFE_API_KEY"
# Price from docs.typesafe.ai/models.md, checked 2026-11-15: $42 per billion
# input tokens, output tokens free. Override with --price-per-million.
DEFAULT_PRICE_PER_MILLION = 0.042
RETRY_STATUS = {429, 529}
QUESTION_TYPES = {"noul", "choice", "score"}
LOG_COLUMNS = [
    "item_id", "question_id", "question_type", "answer", "probabilities",
    "confidence", "routed_outcome", "route_reason", "human_outcome",
    "model", "source", "input_tokens",
]


class ApiError(Exception):
    """Request failed. The message never contains the API key."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class ResponseShapeError(Exception):
    """Response did not match the documented shape."""


# ---------------------------------------------------------------- inputs

def load_items(path, id_field="id"):
    items = []
    if path.lower().endswith((".jsonl", ".ndjson")):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    items.append(json.loads(line))
    else:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            items = list(csv.DictReader(fh))
    for index, item in enumerate(items, start=1):
        item_id = item.get(id_field)
        item["_id"] = str(item_id) if item_id not in (None, "") else str(index)
    return items


def validate_questions(questions):
    if not isinstance(questions, dict) or not questions:
        raise ValueError("QUESTIONS must be a non-empty dict")
    for qid, q in questions.items():
        qtype = q.get("type")
        if qtype not in QUESTION_TYPES:
            raise ValueError("%s: type must be one of %s (box needs images and is not supported here)"
                             % (qid, sorted(QUESTION_TYPES)))
        crit = q.get("criteria")
        if qtype == "choice":
            if not isinstance(crit, dict) or not 1 <= len(crit) <= 255:
                raise ValueError("%s: choice criteria must be a dict of 1 to 255 options" % qid)
        elif qtype == "score":
            if not isinstance(crit, list) or not 2 <= len(crit) <= 10:
                raise ValueError("%s: score criteria must be an ordered list of 2 to 10 levels" % qid)
        elif crit is not None:
            if not isinstance(crit, dict) or not set(crit) <= {"true", "false"}:
                raise ValueError("%s: noul criteria may only have the keys true and false" % qid)


def load_questions_module(path):
    ns = runpy.run_path(path)
    for needed in ("QUESTIONS", "route"):
        if needed not in ns:
            raise ValueError("%s must define %s" % (path, needed))
    if "build_state" not in ns and "STATE_FIELDS" not in ns:
        raise ValueError("%s must define build_state or STATE_FIELDS" % path)
    validate_questions(ns["QUESTIONS"])
    return types.SimpleNamespace(
        MODEL=ns.get("MODEL", "jev-1.14.0"),
        QUESTIONS=ns["QUESTIONS"],
        STATE_FIELDS=ns.get("STATE_FIELDS"),
        build_state=ns.get("build_state"),
        route=ns["route"],
        raw=ns,
    )


def build_state(mod, item):
    if mod.build_state:
        return mod.build_state(item)
    missing = [f for f in mod.STATE_FIELDS if f not in item]
    if missing:
        raise KeyError("item %s is missing state fields %s" % (item["_id"], missing))
    return {f: item[f] for f in mod.STATE_FIELDS}


# --------------------------------------------------------------- requests

def build_request(model, state, questions):
    """Body for POST /v1/systemone: model, state, questions keyed by your names."""
    return {"model": model, "state": state, "questions": questions}


def chunk_questions(questions, per_request):
    ids = list(questions)
    if per_request <= 0 or len(ids) <= per_request:
        return [dict(questions)]
    return [{q: questions[q] for q in ids[i:i + per_request]} for i in range(0, len(ids), per_request)]


def estimate_input_tokens(body):
    """Rough guess (characters divided by 4) used only for the spend guard."""
    return max(1, math.ceil(len(json.dumps(body, ensure_ascii=False)) / 4))


def post_json(url, key, body, timeout=60):
    """Return (status, payload_or_None, headers). Raises URLError on network failure."""
    data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, method="POST", headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "User-Agent": "jev-marketing-gates/0.9",
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
    """Retry 429, 529 and network errors with exponential backoff.

    The docs say to retry 429 and 529 with backoff and that the SDKs follow a
    retry-after header when present; this honours a numeric Retry-After.
    """
    last = "no attempt made"
    for attempt in range(retries + 1):
        status, payload, headers = None, None, {}
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


# --------------------------------------------------------------- responses

def _prob_map(value, where):
    if not isinstance(value, dict) or not value:
        raise ResponseShapeError("%s: probabilities missing" % where)
    out = {}
    for k, v in value.items():
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1:
            raise ResponseShapeError("%s: probability out of range" % where)
        out[str(k)] = float(v)
    return out


def parse_response(resp, questions):
    """Check the documented shape and return (normalized answers, usage, model).

    normalized[qid] = {"type", "value", "probs", "confidence"}
      noul:   value = probability of yes, probs = {"yes": p, "no": 1 - p}, confidence None
      choice: value = chosen option, probs per option, confidence 0 to 1
      score:  value = score (probability weighted, can be fractional), probs per level
              (keys are level numbers as strings), confidence 0 to 1
    """
    if not isinstance(resp, dict) or not isinstance(resp.get("answers"), dict):
        raise ResponseShapeError("no answers object")
    usage = resp.get("usage") if isinstance(resp.get("usage"), dict) else {}
    norm = {}
    for qid, q in questions.items():
        ans = resp["answers"].get(qid)
        if not isinstance(ans, dict):
            raise ResponseShapeError("%s: answer missing" % qid)
        if ans.get("type") != q["type"]:
            raise ResponseShapeError("%s: answer type %r does not match question" % (qid, ans.get("type")))
        if q["type"] == "noul":
            p = ans.get("noul")
            if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0 <= p <= 1:
                raise ResponseShapeError("%s: noul must be a number from 0 to 1" % qid)
            norm[qid] = {"type": "noul", "value": float(p), "probs": {"yes": float(p), "no": 1.0 - float(p)},
                         "confidence": None}
            continue
        conf = ans.get("confidence")
        if not isinstance(conf, (int, float)) or isinstance(conf, bool) or not 0 <= conf <= 1:
            raise ResponseShapeError("%s: confidence must be a number from 0 to 1" % qid)
        probs = _prob_map(ans.get("probabilities"), qid)
        if q["type"] == "choice":
            choice = ans.get("choice")
            if choice not in q["criteria"]:
                raise ResponseShapeError("%s: choice %r is not one of the options" % (qid, choice))
            norm[qid] = {"type": "choice", "value": choice, "probs": probs, "confidence": float(conf)}
        else:
            score = ans.get("score")
            if not isinstance(score, (int, float)) or isinstance(score, bool):
                raise ResponseShapeError("%s: score must be a number" % qid)
            norm[qid] = {"type": "score", "value": float(score), "probs": probs, "confidence": float(conf)}
    return norm, {"input_tokens": int(usage.get("input_tokens") or 0),
                  "output_tokens": int(usage.get("output_tokens") or 0)}, resp.get("model")


# -------------------------------------------------------------- offline mock

def mock_response(body):
    """Deterministic offline stand-in shaped like the documented response.

    The numbers are meaningless. They exist so the pipeline, log and report can
    be tried with no network and no key.
    """
    state_text = json.dumps(body["state"], sort_keys=True, ensure_ascii=False)
    answers = {}
    for qid, q in body["questions"].items():
        seed = int(hashlib.sha256((state_text + "|" + qid).encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        if q["type"] == "noul":
            answers[qid] = {"type": "noul", "noul": round(rng.random(), 3)}
            continue
        names = list(q["criteria"]) if q["type"] == "choice" else [str(i) for i in range(len(q["criteria"]))]
        weights = [(rng.random() + 0.02) ** 3 for _ in names]
        total = sum(weights)
        probs = {n: w / total for n, w in zip(names, weights)}
        n = len(names)
        top = max(probs, key=probs.get)
        if q["type"] == "choice":
            conf = (probs[top] - 1.0 / n) / (1.0 - 1.0 / n)
            answers[qid] = {"type": "choice", "choice": top, "confidence": round(max(conf, 0.0), 3),
                            "probabilities": probs}
        else:
            mode = int(top)
            spread = sum(probs[str(i)] * abs(i - mode) for i in range(n))
            even = sum(abs(i - mode) for i in range(n)) / n
            conf = 1.0 - spread / even if even else 1.0
            answers[qid] = {"type": "score", "score": sum(i * probs[str(i)] for i in range(n)),
                            "confidence": round(max(conf, 0.0), 3),
                            "legend": {str(i): d for i, d in enumerate(q["criteria"])},
                            "probabilities": probs}
    return {"model": body["model"], "answers": answers,
            "usage": {"input_tokens": estimate_input_tokens(body), "output_tokens": 4 * len(answers)}}


def mock_post(url, key, body, timeout=60):
    return 200, mock_response(body), {}


# ---------------------------------------------------------------- the run

def answer_cell(norm_answer):
    if norm_answer["type"] == "noul":
        return "yes" if norm_answer["value"] >= 0.5 else "no"
    if norm_answer["type"] == "score":
        return "%.4f" % norm_answer["value"]
    return norm_answer["value"]


def run_items(items, mod, post, writer, *, base_url=DEFAULT_BASE_URL, key="", model=None, retries=4,
              max_usd=1.0, price=DEFAULT_PRICE_PER_MILLION, per_request=0, source="live",
              sleep=time.sleep, log=print):
    """Send one request per item (all its questions together) and write log rows."""
    model = model or mod.MODEL
    url = base_url.rstrip("/") + ENDPOINT_PATH
    summary = {"items": 0, "ok": 0, "errors": 0, "skipped_by_guard": 0, "requests": 0,
               "input_tokens": 0, "output_tokens": 0, "outcomes": {}, "first_response_ok": None}
    spent = 0.0
    for index, item in enumerate(items):
        state = build_state(mod, item)
        chunks = chunk_questions(mod.QUESTIONS, per_request)
        bodies = [build_request(model, state, c) for c in chunks]
        projected = sum(estimate_input_tokens(b) for b in bodies) * price / 1e6
        if spent + projected > max_usd:
            summary["skipped_by_guard"] = len(items) - index
            log("spend guard: stopped before item %s (spent %.6f, next about %.6f, limit %.2f USD)"
                % (item["_id"], spent, projected, max_usd))
            break
        summary["items"] += 1
        norm, failed, used_model, item_tokens = {}, {}, model, 0
        for chunk, body in zip(chunks, bodies):
            summary["requests"] += 1
            try:
                payload = call_with_retry(post, url, key, body, retries=retries, sleep=sleep)
                part, usage, answered = parse_response(payload, chunk)
            except (ApiError, ResponseShapeError) as exc:
                for qid in chunk:
                    failed[qid] = str(exc)
                if summary["first_response_ok"] is None:
                    summary["first_response_ok"] = False
                continue
            if summary["first_response_ok"] is None:
                summary["first_response_ok"] = True
            norm.update(part)
            used_model = answered or used_model
            item_tokens += usage["input_tokens"]
            summary["input_tokens"] += usage["input_tokens"]
            summary["output_tokens"] += usage["output_tokens"]
            spent += usage["input_tokens"] * price / 1e6
        if failed:
            outcome, reason = "error", "; ".join(sorted(set(failed.values())))[:200]
            summary["errors"] += 1
        else:
            try:
                outcome, reason = mod.route(norm)
            except Exception as exc:  # a broken router must never look like a pass
                outcome, reason = "error", "route failed: %s" % type(exc).__name__
            summary["ok"] += 1 if outcome != "error" else 0
            summary["errors"] += 1 if outcome == "error" else 0
        summary["outcomes"][outcome] = summary["outcomes"].get(outcome, 0) + 1
        first = True
        for qid, q in mod.QUESTIONS.items():
            a = norm.get(qid)
            writer.writerow({
                "item_id": item["_id"], "question_id": qid, "question_type": q["type"],
                "answer": answer_cell(a) if a else "ERROR",
                "probabilities": json.dumps(a["probs"], sort_keys=True) if a else "",
                "confidence": "" if not a or a["confidence"] is None else "%.4f" % a["confidence"],
                "routed_outcome": outcome, "route_reason": reason, "human_outcome": "",
                "model": used_model, "source": source, "input_tokens": item_tokens if first else "",
            })
            first = False
    summary["estimated_usd"] = summary["input_tokens"] * price / 1e6
    return summary


def print_summary(summary, price, source):
    print("items sent: %d, ok: %d, errors: %d, skipped by spend guard: %d, requests: %d"
          % (summary["items"], summary["ok"], summary["errors"], summary["skipped_by_guard"], summary["requests"]))
    label = "mock input tokens (estimated, not billed)" if source == "mock" else "input tokens (as reported by the API)"
    print("%s: %d, output tokens: %d" % (label, summary["input_tokens"], summary["output_tokens"]))
    print("estimated cost: %.6f USD at %.4f USD per million input tokens%s"
          % (summary["estimated_usd"], price, " (mock, nothing was billed)" if source == "mock" else
             "; check your vendor console for the real bill"))
    print("routed outcomes: %s" % (json.dumps(summary["outcomes"], sort_keys=True)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", help="CSV or JSONL file, one item per row")
    ap.add_argument("--questions", required=True, help="path to a questions module such as questions_example.py")
    ap.add_argument("--out", default="log.csv", help="log file to write (default log.csv)")
    ap.add_argument("--id-field", default="id", help="item column or key holding the id (default id)")
    ap.add_argument("--model", help="override the model id from the questions module")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="override for a gateway; the path %s is appended. Vercel AI Gateway documents "
                         "https://ai-gateway.vercel.sh/typesafe with model typesafe-ai/jev and key variable "
                         "AI_GATEWAY_API_KEY (see references/jev-api-notes.md; not tested live)" % ENDPOINT_PATH)
    ap.add_argument("--key-env", default=ENV_KEY,
                    help="name of the environment variable that holds the key (default %s). Only the name is "
                         "given here, never the key itself" % ENV_KEY)
    ap.add_argument("--questions-per-request", type=int, default=0,
                    help="split questions into several requests per item (default 0: all in one request)")
    ap.add_argument("--dry-run", action="store_true", help="offline deterministic mock, no network, no key")
    ap.add_argument("--smoke", action="store_true", help="live check on the first 3 items and a shape report")
    ap.add_argument("--max-items", type=int, default=0, help="process only the first N items")
    ap.add_argument("--max-usd", type=float, default=1.0, help="stop before the estimated spend would pass this (default 1.00)")
    ap.add_argument("--price-per-million", type=float, default=DEFAULT_PRICE_PER_MILLION,
                    help="USD per million input tokens (default 0.042, docs checked 2026-11-15)")
    ap.add_argument("--retries", type=int, default=4)
    ap.add_argument("--data-handling-confirmed", action="store_true",
                    help="required for live runs: the data owner decided that these items may be sent to the vendor")
    args = ap.parse_args(argv)

    if not args.base_url.lower().startswith("https://"):
        print("refusing a base URL that is not https", file=sys.stderr)
        return 2
    mod = load_questions_module(args.questions)
    items = load_items(args.items, args.id_field)
    limit = 3 if args.smoke else args.max_items
    if limit:
        items = items[:limit]
    if not items:
        print("no items to run", file=sys.stderr)
        return 2

    key, source = "", "mock"
    post = mock_post
    if not args.dry_run:
        key = os.environ.get(args.key_env, "")
        if not key:
            print("set %s in the environment, or use --dry-run" % args.key_env, file=sys.stderr)
            return 2
        if not args.data_handling_confirmed:
            print("live run refused: items may hold personal or private data. Decide data handling first, "
                  "then pass --data-handling-confirmed (see SKILL.md hard rules).", file=sys.stderr)
            return 2
        post, source = post_json, "live"
    else:
        print("DRY RUN: offline mock answers, no network, no key. The numbers are meaningless.")

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LOG_COLUMNS)
        writer.writeheader()
        summary = run_items(items, mod, post, writer, base_url=args.base_url, key=key, model=args.model,
                            retries=args.retries, max_usd=args.max_usd, price=args.price_per_million,
                            per_request=args.questions_per_request, source=source)
    print("log written to %s" % args.out)
    print_summary(summary, args.price_per_million, source)
    if args.smoke:
        ok = summary["errors"] == 0 and summary["ok"] > 0
        print("SMOKE %s%s: responses %s the documented shape for all %d items."
              % ("PASSED" if ok else "FAILED", " (mock, proves nothing about the API)" if source == "mock" else "",
                 "matched" if ok else "did not all match", summary["items"]))
        return 0 if ok else 1
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
