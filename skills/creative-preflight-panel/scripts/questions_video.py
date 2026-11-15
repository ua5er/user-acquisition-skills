"""Video track: pre-flight panel questions, thresholds and state builder.

Same contract as questions_static.py. A video concept has three hook
variants on one body, so each hook variant is its own panel item
(M1-A, M1-B, M1-C): the matrix then shows which opening holds which buyer.
The state carries the first 3 seconds as written in the motion brief and the
rest of the beat sheet as plain text.
"""

TRACK = "video"
MODEL = "jev-1.14.0"  # pinned versioned id, checked 2026-11-15
PANEL_VERSION = "panel-video-1.0"

THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

ACTION = "action"
ENGAGE_OPTIONS = ("stop", "click")
FIT = "fit"
FLAGS = ["hook_about_problem", "offer_clear", "distrust_claim"]

QUESTIONS = {
    "action": {
        "type": "choice",
        "instructions": "`buyer` sees the first seconds of the video `ad` while scrolling a short-video feed "
                        "on their phone. What does `buyer` most likely do?",
        "criteria": {
            "scroll": "Swipes away within the first 3 seconds.",
            "stop": "Keeps watching past the first 3 seconds, then moves on without tapping.",
            "click": "Watches and taps the ad to learn more or to start.",
        },
    },
    "hook_about_problem": {
        "type": "noul",
        "instructions": "`ad.first_3s` is about a problem or a goal that `buyer` has.",
    },
    "offer_clear": {
        "type": "noul",
        "instructions": "From `ad.first_3s` alone, `buyer` can tell what product the video is about.",
    },
    "distrust_claim": {
        "type": "noul",
        "instructions": "`buyer` would doubt or distrust a claim made in `ad`.",
    },
    "fit": {
        "type": "score",
        "instructions": "How well does `ad` speak to the situation and the goal of `buyer`?",
        "criteria": [
            "It has nothing to do with the buyer's situation.",
            "It touches the buyer's general area but not their situation.",
            "It speaks to the buyer's situation but misses their goal or their main objection.",
            "It speaks to the buyer's situation and goal and answers their main objection.",
        ],
    },
}

PROFILE_FIELDS = ("situation", "goal", "objections", "stops_scrolling_for")


def build_profile_state(profile):
    return {k: profile[k] for k in PROFILE_FIELDS if profile.get(k)}


def _hook_text(h):
    parts = []
    if h.get("visual"):
        parts.append("Seen: %s." % h["visual"].rstrip("."))
    if h.get("on_screen"):
        parts.append("Text on screen: \"%s\"." % h["on_screen"])
    parts.append("Spoken: \"%s\"." % h["spoken"] if h.get("spoken") else "No speech.")
    return " ".join(parts)


def _rest_text(beats):
    lines = []
    for b in beats[1:]:
        bits = [b.get("visual", "")]
        if b.get("spoken"):
            bits.append("says \"%s\"" % b["spoken"])
        if b.get("on_screen"):
            bits.append("text \"%s\"" % b["on_screen"])
        lines.append("%s s: %s" % (b.get("t"), "; ".join(x for x in bits if x)))
    return " | ".join(lines)


def build_items(concept):
    """One panel item per hook variant: <concept_id>-<hook id>."""
    items = []
    rest = _rest_text(concept.get("beats", []))
    for h in concept.get("hooks", []):
        ad = {"format": concept.get("format", ""), "first_3s": _hook_text(h),
              "rest_of_video": rest, "end_card": concept.get("end_card", "")}
        items.append(("%s-%s" % (concept["concept_id"], h.get("id")), {k: v for k, v in ad.items() if v}))
    return items


def build_state(profile, ad_state):
    return {"buyer": build_profile_state(profile), "ad": ad_state}
