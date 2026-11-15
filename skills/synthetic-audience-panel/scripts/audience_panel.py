#!/usr/bin/env python3
"""Text-only Jev panel. Standard library only. Only `run` uses the network."""
import argparse
import itertools
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

LABEL = "panel answers, not delivery metrics"
URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.14.0"
FACTORS = {
    "fit": {"core": "is exactly the kind of person described in `audience`",
            "adjacent": "is close to the people in `audience` but not quite one of them",
            "outside": "has no need for a product like the one in `product`"},
    "stage": {"unaware": "has not thought about the problem this product solves",
              "problem": "feels the problem but has not looked for a solution",
              "solution": "is comparing solutions of this kind right now",
              "competitor": "uses a competing product today",
              "lapsed": "tried a product of this kind before and gave up",
              "product": "has heard of this product but has not tried it",
              "most": "has been meaning to try this product and is waiting for a good offer"},
    "urgency": {"soon": "needs this within the next few weeks", "someday": "has no deadline for this"},
    "price": {"tight": "rarely pays for apps or subscriptions",
              "value": "pays when the value is clear", "easy": "pays easily for things that save time"},
    "decision": {"quick": "decides on the spot", "careful": "researches before paying for anything"},
    "trust": {"sceptic": "distrusts advertising claims", "neutral": "is neutral toward ads",
              "open": "often tries things seen in ads"},
    "moment": {"rushed": "is scrolling fast between tasks", "browsing": "is browsing with time to spare"},
}
COMMON = {
    "urgency": {"soon": .25, "someday": .75},
    "price": {"tight": .25, "value": .50, "easy": .25},
    "decision": {"quick": .35, "careful": .65},
    "trust": {"sceptic": .30, "neutral": .50, "open": .20},
    "moment": {"rushed": .65, "browsing": .35},
}
MIXES = {
    "cold": {"fit": dict(core=.30, adjacent=.40, outside=.30),
             "stage": dict(unaware=.35, problem=.28, solution=.14, competitor=.09,
                           lapsed=.06, product=.05, most=.03), **COMMON},
    "warm": {"fit": dict(core=.60, adjacent=.30, outside=.10),
             "stage": dict(unaware=.05, problem=.20, solution=.25, competitor=.12,
                           lapsed=.08, product=.20, most=.10), **COMMON},
    "retargeting": {"fit": dict(core=.75, adjacent=.20, outside=.05),
                    "stage": dict(unaware=0, problem=.05, solution=.15, competitor=.08,
                                  lapsed=.07, product=.40, most=.25), **COMMON},
}
LEVELS = ["Scrolls past without reading it.", "Stops and reads the ad.",
          "Taps the ad to learn more.", "Taps the ad and intends to take the offer."]
BARRIERS = {
    "not_relevant": "The product is not for a person like this.",
    "not_clear": "The ad does not make clear what is offered.",
    "not_believable": "The claims are hard to believe.",
    "too_expensive": "The price or the commitment is too high.",
    "no_urgency": "There is no reason to act now.",
    "nothing": "Nothing holds this person back.",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(x):
    return isinstance(x, str) and bool(x.strip())


def number(x):
    return type(x) in (int, float) and math.isfinite(x)


def unique_object(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, "Duplicate JSON object key.")
        obj[k] = v
    return obj


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ValueError("Cannot read input JSON.") from None


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def default_cohort():
    return json.loads(json.dumps(dict(factors=FACTORS, control=dict(factor="fit", option="outside"),
                                     target_only=["stage", "urgency"], mixes=MIXES, size=1000, seed=7)))


def validate_mix(mix, spec):
    factors = spec["factors"]
    require(isinstance(mix, dict) and set(mix) == set(factors), "Mix must cover every factor.")
    for f, opts in factors.items():
        shares = mix[f]
        require(isinstance(shares, dict) and set(shares) == set(opts), "Mix must cover every option.")
        require(all(number(v) and 0 <= v <= 1 for v in shares.values()), "Invalid mix share.")
        require(abs(sum(shares.values()) - 1) < 1e-8, "Each factor's mix shares must sum to 1.")


def validate_spec(spec):
    require(isinstance(spec, dict), "Cohort must be an object.")
    require(set(spec) == {"factors", "control", "target_only", "mixes", "size", "seed"},
            "Cohort fields: factors, control, target_only, mixes, size, seed.")
    factors = spec["factors"]
    require(isinstance(factors, dict) and bool(factors), "Cohort needs factors.")
    for f, opts in factors.items():
        require(text(f) and f != "id" and f.lower() not in
                {"age", "gender", "income", "ethnicity"}, "Invalid or demographic factor name.")
        require(isinstance(opts, dict) and 2 <= len(opts) <= 7, "Factors need 2 to 7 options.")
        require(all(text(o) and text(v) for o, v in opts.items()), "Options need ids and clauses.")
        require(len(set(opts.values())) == len(opts), "Option clauses must be distinct.")
    c = spec["control"]
    require(isinstance(c, dict) and set(c) == {"factor", "option"}, "Invalid control definition.")
    require(text(c["factor"]) and text(c["option"]) and c["factor"] in factors and
            c["option"] in factors[c["factor"]], "Control must name an existing factor option.")
    target = spec["target_only"]
    require(isinstance(target, list) and all(text(f) for f in target), "Invalid target_only list.")
    require(len(set(target)) == len(target) and set(target) <= set(factors) and
            c["factor"] not in target, "Invalid target-only factors.")
    require(type(spec["size"]) is int and spec["size"] > 0, "Size must be a positive integer.")
    require(type(spec["seed"]) is int, "Seed must be an integer.")
    require(isinstance(spec["mixes"], dict) and bool(spec["mixes"]), "Cohort needs named mixes.")
    for name, mix in spec["mixes"].items():
        require(text(name), "Mix name must be text.")
        validate_mix(mix, spec)


def is_control(p, spec):
    c = spec["control"]
    return p[c["factor"]] == c["option"]


def sentence(p, spec):
    parts = [opts[p[f]] for f, opts in spec["factors"].items() if f in p]
    return "This person " + (", ".join(parts[:-1]) + " and " if len(parts) > 1 else "") + parts[-1] + "."


def grid(spec):
    c, factors = spec["control"], spec["factors"]
    cells = []
    for fit in factors[c["factor"]]:
        active = [f for f in factors if f != c["factor"] and
                  not (fit == c["option"] and f in spec["target_only"])]
        count = math.prod(len(factors[f]) for f in active)
        require(len(cells) + count <= 100000, "Grid too large for this CLI.")
        for values in itertools.product(*(factors[f] for f in active)):
            cells.append({c["factor"]: fit, **dict(zip(active, values))})
    return cells


class Generator:
    """Mulberry32, with explicit unsigned 32-bit operations."""
    def __init__(self, seed):
        self.state = seed & 0xffffffff

    def next(self):
        self.state = (self.state + 0x6d2b79f5) & 0xffffffff
        t = self.state
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xffffffff
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xffffffff)) & 0xffffffff
        return ((t ^ (t >> 14)) & 0xffffffff) / 4294967296


def build_people(spec):
    validate_spec(spec)
    cells = grid(spec)
    require(spec["size"] <= len(cells), "Size exceeds the distinct grid.")
    require(len({sentence(p, spec) for p in cells}) == len(cells), "Descriptions must be distinct.")
    rng = Generator(spec["seed"])
    for i in range(len(cells) - 1, 0, -1):
        j = int(rng.next() * (i + 1))
        cells[i], cells[j] = cells[j], cells[i]
    people = [dict(p, id=f"p{i:04d}") for i, p in enumerate(cells[:spec["size"]])]
    require(any(is_control(p, spec) for p in people) and
            any(not is_control(p, spec) for p in people), "Selected cohort needs controls and targets.")
    return people


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def rotate(options, index):
    keys = list(options)
    head = keys[:-1]
    k = index % len(head)
    return {o: options[o] for o in head[k:] + head[:k] + keys[-1:]}


def validate_scale(levels, barriers):
    require(isinstance(levels, list) and 2 <= len(levels) <= 10 and all(text(v) for v in levels),
            "Levels must be a list of 2 to 10 nonempty texts.")
    require(len(set(levels)) == len(levels), "Levels must be distinct.")
    require(isinstance(barriers, dict) and len(barriers) >= 2 and
            all(text(k) and text(v) for k, v in barriers.items()), "Invalid barriers object.")


def validate_ads(ads):
    require(isinstance(ads, list) and bool(ads), "Ads must be a nonempty list.")
    ids = []
    for ad in ads:
        require(isinstance(ad, dict) and text(ad.get("id")) and len(ad) >= 2 and
                all(text(k) and isinstance(v, str) for k, v in ad.items()) and
                any(text(v) for k, v in ad.items() if k != "id"), "Each variant needs an id and text fields.")
        ids.append(ad["id"])
    require(len(set(ids)) == len(ids), "Variant ids must be unique.")


def probabilities(raw, keys):
    require(isinstance(raw, dict) and set(raw) == set(keys), "Invalid probability keys.")
    vals = [raw[k] for k in keys]
    require(all(number(v) and 0 <= v <= 1 for v in vals), "Invalid probabilities.")
    total = sum(vals)
    require(abs(total - 1) <= .005, "Probabilities must sum to 1.")
    return [v / total for v in vals]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def call_api(state, questions, args, key):
    body = json.dumps(dict(model=args.model, state=state, questions=questions)).encode("utf-8")
    req = urllib.request.Request(args.base_url, data=body, headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    opener = urllib.request.build_opener(NoRedirect())
    for attempt in range(5):
        try:
            with opener.open(req, timeout=90) as response:
                data = json.loads(response.read(), object_pairs_hook=unique_object)
            require(isinstance(data, dict) and isinstance(data.get("answers"), dict),
                    "Malformed API response.")
            require(set(data["answers"]) == set(questions), "API answer ids do not match questions.")
            usage = data.get("usage", {})
            require(isinstance(usage, dict) and type(usage.get("input_tokens")) is int and
                    usage["input_tokens"] >= 0, "Missing API input token usage.")
            return data, attempt
        except urllib.error.HTTPError as exc:
            status = exc.code
            exc.close()
            if attempt == 4 or not (status == 429 or 500 <= status <= 599):
                raise ValueError(f"HTTP {status}") from None
        except (urllib.error.URLError, OSError):
            if attempt == 4:
                raise ValueError("Network request failed.") from None
        except (json.JSONDecodeError, UnicodeError):
            raise ValueError("Malformed API response JSON.") from None
        time.sleep(1.5 * (2 ** attempt))


def run_panel(args):
    key = os.environ.get(args.key_env, "")
    require(bool(key.strip()), "Missing API key environment variable.")
    require(all(32 <= ord(ch) < 127 for ch in key), "Invalid API key environment value.")
    url = urllib.parse.urlsplit(args.base_url)
    require(url.scheme == "https" and bool(url.hostname) and not url.username and
            not url.password and not url.query and not url.fragment, "Base URL must be an HTTPS endpoint.")
    spec = load(args.cohort) if args.cohort else default_cohort()
    people = build_people(spec)
    ads = load(args.ads)
    validate_ads(ads)
    levels = load(args.levels) if args.levels else LEVELS
    barriers = load(args.barriers) if args.barriers else BARRIERS
    validate_scale(levels, barriers)
    require(all(text(v) for v in (args.product, args.audience, args.stimulus_name, args.model)),
            "Product, audience, stimulus name and model must be nonempty.")
    variants, total_tokens, total_requests, total_retries = [], 0, 0, 0
    start = time.perf_counter()
    asked = [p for p in people if not is_control(p, spec)][::4]
    for ad in ads:
        # The measured layout: the stimulus sits in the state under its own name, without the variant id.
        name = args.stimulus_name
        state = {"product": args.product, "audience": args.audience,
                 name: {k: v for k, v in ad.items() if k != "id"}}
        depth = [(p["id"], dict(type="score", instructions=sentence(p, spec) +
                  f" How far does this person go with the {name} in `{name}`?",
                  criteria=levels)) for p in people]
        why = [("why_" + p["id"], dict(type="choice", instructions=sentence(p, spec) +
                f" What is the main thing that holds this person back from acting on the {name} in `{name}`?",
                criteria=rotate(barriers, i))) for i, p in enumerate(asked)]
        jobs = [dict(part) for part in chunks(depth, 125)] + [dict(part) for part in chunks(why, 60)]
        raw, tokens, retries = {}, 0, 0
        t = time.perf_counter()
        with ThreadPoolExecutor(max_workers=6) as pool:
            for data, retried in pool.map(lambda q: call_api(state, q, args, key), jobs):
                raw.update(data["answers"])
                tokens += data["usage"]["input_tokens"]
                retries += retried
        answers = {}
        for p in people:
            entry = raw[p["id"]]
            require(isinstance(entry, dict), "Malformed depth answer.")
            pr = probabilities(entry.get("probabilities"), [str(i) for i in range(len(levels))])
            a = dict(probabilities=pr, score=sum(i * v for i, v in enumerate(pr)))
            if "why_" + p["id"] in raw:
                b = raw["why_" + p["id"]]
                require(isinstance(b, dict) and isinstance(b.get("choice"), str) and
                        b["choice"] in barriers, "Malformed barrier answer.")
                probabilities(b.get("probabilities"), list(barriers))
                a["why"] = b["choice"]
            answers[p["id"]] = a
        variants.append(dict(id=ad["id"], stimulus=ad, answers=answers, accounting=dict(
            input_tokens=tokens, seconds=time.perf_counter() - t, usd=tokens * .042 / 1e6,
            requests=len(jobs), retries=retries)))
        total_tokens += tokens
        total_requests += len(jobs)
        total_retries += retries
    write_json(args.out, dict(label=LABEL, cohort=spec, people=people, levels=levels, barriers=barriers,
        product=args.product, audience=args.audience, stimulus_name=args.stimulus_name,
        model=args.model, variants=variants, accounting_label="API accounting, not panel answers",
        accounting=dict(input_tokens=total_tokens, seconds=time.perf_counter() - start,
                        usd=total_tokens * .042 / 1e6, requests=total_requests, retries=total_retries)))


def weights(people, spec, mix):
    validate_mix(mix, spec)
    groups = {f: {o: [i for i, p in enumerate(people) if p.get(f) == o]
                   for o in opts} for f, opts in spec["factors"].items()}
    w = [1.0] * len(people)
    for f, opts in groups.items():
        total = sum(len(indices) for indices in opts.values())
        for o, indices in opts.items():
            require(bool(indices) or mix[f][o] == 0, "Mix has positive share for an absent option.")
            ratio = mix[f][o] * total / len(indices) if indices else 0
            for i in indices:
                w[i] *= ratio
    require(sum(w) > 0, "Mix removes the entire cohort.")
    w = [v / sum(w) for v in w]
    for _ in range(8):
        for f, opts in groups.items():
            mass = sum(w[i] for indices in opts.values() for i in indices)
            for o, indices in opts.items():
                current, desired = sum(w[i] for i in indices), mass * mix[f][o]
                require(current > 0 or desired == 0, "Mix cannot be supported by this cohort.")
                scale = desired / current if current else 0
                for i in indices:
                    w[i] *= scale
    total = sum(w)
    w = [v / total for v in w]
    marginals = {}
    for f, opts in groups.items():
        mass = sum(w[i] for indices in opts.values() for i in indices)
        marginals[f] = {o: sum(w[i] for i in indices) / mass if mass else None
                        for o, indices in opts.items()}
        require(not mass or all(abs(marginals[f][o] - mix[f][o]) <= .005 for o in opts),
                "Mix did not converge within 8 passes; revise the cohort or mix.")
    return w, marginals


def mean(values, w, indices=None):
    indices = range(len(w)) if indices is None else indices
    indices = list(indices)
    den = sum(w[i] for i in indices)
    return sum(w[i] * values[i] for i in indices) / den if den else None


def divide(a, b):
    return a / b if a is not None and b is not None and b > 0 else None


def scaled(v):
    return 1000 * v if v is not None else None


def build_report(data, mix, sequence=False, complete_from=2):
    spec = data["cohort"]
    people = build_people(spec)
    require(data["people"] == people, "Saved people do not match the cohort.")
    levels, barriers = data["levels"], data["barriers"]
    validate_scale(levels, barriers)
    require(not sequence or 0 <= complete_from < len(levels), "Invalid completion level index.")
    variants = data["variants"]
    require(isinstance(variants, list) and bool(variants), "No saved variants.")
    ids = [v["id"] for v in variants]
    require(all(text(v) for v in ids) and len(set(ids)) == len(ids), "Invalid saved variant ids.")
    w, marginals = weights(people, spec, mix)
    report = dict(label=LABEL, assumptions=mix, achieved_marginals=marginals,
                  weights={p["id"]: wi for p, wi in zip(people, w)}, effective_size=1 / sum(v*v for v in w),
                  control=spec["control"], caveat="Levels are generous. Coverage is not accuracy.",
                  variants=[], comparisons=[], sequence=[])
    panels = []
    for variant in variants:
        raw = variant["answers"]
        require(isinstance(raw, dict) and set(raw) == {p["id"] for p in people}, "Incomplete saved answers.")
        rows, picks = [], []
        for p in people:
            a = raw[p["id"]]
            require(isinstance(a, dict) and isinstance(a.get("probabilities"), list) and
                    len(a["probabilities"]) == len(levels), "Malformed saved depth probabilities.")
            pr = probabilities(dict(zip(map(str, range(len(levels))), a["probabilities"])),
                               list(map(str, range(len(levels)))))
            rows.append(pr)
            pick = a.get("why")
            require(pick is None or (isinstance(pick, str) and pick in barriers and
                    not is_control(p, spec)), "Invalid saved barrier choice.")
            picks.append(pick)
        tails = [[sum(pr[k:]) for pr in rows] for k in range(1, len(levels))]
        scores = [sum(k * v for k, v in enumerate(pr)) for pr in rows]
        funnel = [scaled(mean(t, w)) for t in tails]
        panels.append(dict(tails=tails, scores=scores, funnel=funnel, rows=rows))
        segments = {}
        for f, opts in spec["factors"].items():
            segments[f] = {o: [scaled(mean(t, w, [i for i, p in enumerate(people) if p.get(f) == o]))
                               for t in tails] for o in opts}
        controls = [i for i, p in enumerate(people) if is_control(p, spec)]
        sampled = [i for i, pick in enumerate(picks) if pick is not None]
        objections = {o: mean([float(pick == o) for pick in picks], w, sampled) for o in barriers}
        readings = {}
        compatible = (levels == LEVELS and spec["control"] == dict(factor="fit", option="outside") and
                      all(set(opts) <= set(spec["factors"].get(f, {})) for f, opts in FACTORS.items()))
        if compatible:
            def rate(k, predicate):
                return mean(tails[k-1], w, [i for i, p in enumerate(people) if predicate(p)])
            core = lambda p: p["fit"] == "core"
            target = lambda p: not is_control(p, spec)
            ct = rate(2, core)
            outside = rate(2, lambda p: is_control(p, spec))
            readings = dict(hook_strength=rate(1, lambda p: target(p) and p["moment"] == "rushed"),
                follow_through=divide(rate(3, core), ct), control_check=outside, selectivity=divide(ct, outside),
                sceptic_gap=divide(rate(2, lambda p: target(p) and p["trust"] == "sceptic"),
                                   rate(2, lambda p: target(p) and p["trust"] == "open")),
                price_gap=divide(rate(3, lambda p: target(p) and p["price"] == "tight"),
                                 rate(3, lambda p: target(p) and p["price"] == "easy")),
                cold_pull=divide(rate(2, lambda p: target(p) and p["stage"] in ("unaware", "problem")),
                                 rate(2, lambda p: target(p) and p["stage"] in ("product", "most"))))
        report["variants"].append(dict(id=variant["id"], funnel_per_1000=dict(zip(levels[1:], funnel)),
            control_per_1000=dict(zip(levels[1:], [scaled(mean(t, w, controls)) for t in tails])),
            readings=readings, barrier_shares=objections, by_factor_per_1000=segments))
    if not sequence:
        first = panels[0]
        for variant, panel in zip(variants[1:], panels[1:]):
            gaps = [b-a for a, b in zip(first["funnel"], panel["funnel"])]
            deepest = gaps[-2:]
            agrees = len(deepest) == 2 and (all(g > 0 for g in deepest) or all(g < 0 for g in deepest))
            ahead = agrees and max(abs(g) for g in deepest) >= 10
            better = mean([float(b-a > .05) for a, b in zip(first["scores"], panel["scores"])], w)
            worse = mean([float(a-b > .05) for a, b in zip(first["scores"], panel["scores"])], w)
            report["comparisons"].append(dict(variant=variant["id"], baseline=variants[0]["id"],
                gaps_per_1000=dict(zip(levels[1:], gaps)), share_variant_better=better,
                share_baseline_better=worse, share_about_same=max(0, 1-better-worse),
                verdict="ahead" if ahead else "too close to call",
                leader=(variant["id"] if deepest[-1] > 0 else variants[0]["id"]) if ahead else None))
    else:
        survival = [1.0] * len(people)
        for variant, panel in zip(variants, panels):
            completion = [sum(pr[complete_from:]) for pr in panel["rows"]]
            entry = mean(survival, w)
            after = [s*c for s, c in zip(survival, completion)]
            retained = mean(after, w)
            report["sequence"].append(dict(id=variant["id"], entry_per_1000=scaled(entry),
                completed_per_1000=scaled(retained), hazard=divide(entry-retained, entry)))
            survival = after
    return report


def markdown(report):
    lines = ["# Synthetic audience panel", "", LABEL, "",
             "Levels are generous. Show controls. Coverage is not accuracy.",
             "Mix shares are assumptions. Barrier shares cover sampled targets only.", ""]
    def table(title, headers, rows):
        lines.extend([f"## {title}", "", f"### {LABEL}", ""])
        def cell(value):
            if value is None:
                return "null"
            if isinstance(value, float):
                if abs(value) >= 100:
                    return f"{value:.0f}"
                if abs(value) >= 10:
                    return f"{value:.1f}"
                return f"{value:.3g}"
            return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
        lines.append("| " + " | ".join(map(cell, headers)) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        lines.extend("| " + " | ".join(map(cell, row)) + " |" for row in rows)
        lines.append("")
    table("Mix assumptions", ["factor", "option", "assumed share", "achieved share"],
          [(f, o, v, report["achieved_marginals"][f][o]) for f, opts in report["assumptions"].items()
           for o, v in opts.items()])
    table("Weight diagnostic", ["reading", "value"], [("effective size", report["effective_size"])])
    for v in report["variants"]:
        table(v["id"] + ": funnel", ["level or deeper", "per 1,000", "control per 1,000"],
              [(k, val, v["control_per_1000"][k]) for k, val in v["funnel_per_1000"].items()])
        table(v["id"] + ": readings", ["reading", "value"], v["readings"].items())
        table(v["id"] + ": objections", ["barrier", "share"], v["barrier_shares"].items())
        table(v["id"] + ": factor options", ["factor", "option", *v["funnel_per_1000"]],
              [(f, o, *vals) for f, opts in v["by_factor_per_1000"].items() for o, vals in opts.items()])
    for c in report["comparisons"]:
        table(c["variant"] + " versus " + c["baseline"], ["reading", "value"],
              [*c["gaps_per_1000"].items(), *[(k, v) for k, v in c.items()
                                            if k not in ("variant", "baseline", "gaps_per_1000")]])
    if report["sequence"]:
        table("Ordered flow", ["step", "entry per 1,000", "completed per 1,000", "hazard"],
              [(s["id"], s["entry_per_1000"], s["completed_per_1000"], s["hazard"])
               for s in report["sequence"]])
    lines.extend(["Individual person weights are in the JSON report.", ""])
    return "\n".join(lines)


def selftest():
    spec = default_cohort()
    people = build_people(spec)
    assert len(people) == len({sentence(p, spec) for p in people}) == 1000
    data = dict(cohort=spec, people=people, levels=LEVELS, barriers=BARRIERS, variants=[])
    for name, boost in (("base", 0), ("better", .10), ("near", .001)):
        answers = {}
        for p in people:
            t = .20 if is_control(p, spec) else .55 + .05 * (p["trust"] == "open")
            pr = [1-t-boost, .4*t, .4*t, .2*t+boost]
            answers[p["id"]] = dict(probabilities=pr)
        data["variants"].append(dict(id=name, answers=answers))
    for mix in spec["mixes"].values():
        w, marginals = weights(people, spec, mix)
        assert abs(sum(w)-1) < 1e-10
        assert all(abs(marginals[f][o]-v) <= .005 for f, opts in mix.items() for o, v in opts.items())
        assert all(wi == 0 for p, wi in zip(people, w) if any(mix[f][o] == 0 for f, o in p.items() if f != "id"))
    report = build_report(data, spec["mixes"]["cold"])
    assert report["variants"][0]["readings"]["selectivity"] > 1
    assert report["comparisons"][0]["verdict"] == "ahead"
    assert report["comparisons"][0]["leader"] == "better"
    assert report["comparisons"][1]["verdict"] == "too close to call"
    sequence = build_report(data, spec["mixes"]["cold"], True)["sequence"]
    assert abs(sequence[0]["entry_per_1000"] - 1000) < 1e-8
    assert all(s["completed_per_1000"] <= s["entry_per_1000"] for s in sequence)
    assert LABEL in markdown(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("cohort")
    c.add_argument("--cohort", help="Custom cohort to validate and write")
    c.add_argument("--size", type=int, default=1000)
    c.add_argument("--seed", type=int, default=7)
    c.add_argument("--out", required=True)
    r = sub.add_parser("run")
    for flag in ("ads", "product", "audience", "out"):
        r.add_argument("--" + flag, required=True)
    for flag in ("cohort", "levels", "barriers"):
        r.add_argument("--" + flag)
    r.add_argument("--stimulus-name", default="ad")
    r.add_argument("--key-env", default="TYPESAFE_API_KEY")
    r.add_argument("--base-url", default=URL)
    r.add_argument("--model", default=MODEL)
    p = sub.add_parser("report")
    p.add_argument("--answers", nargs="+", required=True)
    for flag in ("mix", "out-md", "out-json"):
        p.add_argument("--" + flag, required=True)
    p.add_argument("--sequence", action="store_true")
    p.add_argument("--complete-from", type=int, default=2)
    sub.add_parser("selftest")
    args = parser.parse_args()
    try:
        if args.command == "cohort":
            spec = load(args.cohort) if args.cohort else default_cohort()
            require(isinstance(spec, dict), "Cohort must be an object.")
            spec.update(size=args.size, seed=args.seed)
            build_people(spec)
            write_json(args.out, spec)
        elif args.command == "run":
            run_panel(args)
        elif args.command == "report":
            data = load(args.answers[0])
            for path in args.answers[1:]:
                extra = load(path)
                require(all(data[k] == extra[k] for k in
                            ("cohort", "people", "levels", "barriers", "product", "audience")),
                        "Merged runs must share cohort, scale and context.")
                data["variants"].extend(extra["variants"])
            mixes = data["cohort"]["mixes"]
            mix = mixes[args.mix] if args.mix in mixes else load(args.mix)
            report = build_report(data, mix, args.sequence, args.complete_from)
            write_json(args.out_json, report)
            with open(args.out_md, "w", encoding="utf-8") as f:
                f.write(markdown(report))
        else:
            selftest()
            print("Offline selftest passed.")
    except ValueError as exc:
        print("Error: " + str(exc), file=sys.stderr)
        return 1
    except (KeyError, TypeError, IndexError, AttributeError, OverflowError):
        print("Error: malformed input or API response.", file=sys.stderr)
        return 1
    except OSError:
        print("Error: file or network operation failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
