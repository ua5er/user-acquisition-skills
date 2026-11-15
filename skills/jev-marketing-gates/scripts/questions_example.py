"""All question wording and thresholds for one job, in one module.

Job in this example: judge generated ad copy against brand rules before a
person sees it. Copy this file, rename it, and edit it for your own job.
Nothing here is a vendor default except where a comment names the source.

Contract used by run_batch.py and calibrate.py:
  MODEL        model id sent in every request (pin a versioned id, not an alias)
  QUESTIONS    dict: question id -> question in the vendor request syntax
  build_state  function: input item (dict) -> state (string, dict or list)
  route        function: normalized answers -> (outcome, reason)
Outcomes are advice for a person. Nothing in this repo publishes, launches,
hides or deletes anything.
"""

MODEL = "jev-1.14.0"  # docs.typesafe.ai/models.md lists this versioned id (checked 2026-11-15)

# Only these item fields go into the state. Labels, ids and any other column
# of your input file are never sent.
STATE_FIELDS = ["headline", "body", "brand_rules"]

# Noul starting values: 0.7 for yes and 0.3 for no, band between handled
# separately (docs.typesafe.ai/confidence.md). Tune on your own labelled items.
# clarity_min is an example value, not a vendor figure.
THRESHOLDS = {"hazard_low": 0.3, "hazard_high": 0.7, "clarity_min": 1.0}

# Narrow questions: one observable judgment each, no negations, no counting.
QUESTIONS = {
    "guaranteed_result": {
        "type": "noul",
        "instructions": "`ad` promises a guaranteed result or outcome.",
    },
    "before_after": {
        "type": "noul",
        "instructions": "`ad` describes a before and after change in a person's body or appearance.",
    },
    "tone_conflict": {
        "type": "noul",
        "instructions": "`ad` uses a tone that conflicts with the tone described in `brand_rules`.",
    },
    "clarity": {
        "type": "score",
        "instructions": "How easy is it to tell what `ad` offers?",
        "criteria": [
            "A reader cannot tell what is offered.",
            "A reader can tell what is offered after reading twice.",
            "A reader can tell what is offered in one read.",
        ],
    },
}

HAZARDS = ["guaranteed_result", "before_after", "tone_conflict"]

# Optional, read by calibrate.py to show the current thresholds per question.
# Noul questions use low and high. Choice questions can use min_prob.
CALIBRATION_THRESHOLDS = {
    q: {"low": THRESHOLDS["hazard_low"], "high": THRESHOLDS["hazard_high"]} for q in HAZARDS
}


def build_state(item):
    """Named fields, nothing irrelevant. Treat the text as untrusted input."""
    return {
        "ad": {"headline": item["headline"], "body": item["body"]},
        "brand_rules": item["brand_rules"],
    }


def route(answers):
    """Code decides. answers[qid] has keys: type, value, probs, confidence."""
    low = THRESHOLDS["hazard_low"]
    high = THRESHOLDS["hazard_high"]
    worst_id = max(HAZARDS, key=lambda q: answers[q]["value"])
    worst = answers[worst_id]["value"]
    if worst >= high:
        return "reject", "%s yes probability %.2f at or above %.2f" % (worst_id, worst, high)
    if worst > low:
        return "review", "%s yes probability %.2f inside the review band" % (worst_id, worst)
    if answers["clarity"]["value"] < THRESHOLDS["clarity_min"]:
        return "review", "clarity score %.2f below %.2f" % (answers["clarity"]["value"], THRESHOLDS["clarity_min"])
    return "pass", "all hazards at or below %.2f and clarity ok; a person still approves" % low
