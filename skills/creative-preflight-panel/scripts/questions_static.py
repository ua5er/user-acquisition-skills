"""Static track: pre-flight panel questions, thresholds and state builder.

Every wording, option and threshold for static concepts lives in this one
module, so a change is a reviewable diff. Contract used by run_panel.py and
panel_matrix.py:

  TRACK, MODEL, PANEL_VERSION, THRESHOLDS
  QUESTIONS            question id -> question in the vendor request syntax
  ACTION               id of the Choice (scroll, stop, click)
  ENGAGE_OPTIONS       Choice options that count as "the ad held this person"
  FLAGS                yes/no questions reported per concept
  FIT                  id of the Score question
  build_items(concept) concept record -> list of (item_id, ad_state)
  build_state(profile, ad_state) -> the state sent to Jev

The state is text only: one buyer profile written by Claude and the concept
as the brief describes it. No images, no names of real people.
"""

TRACK = "static"
MODEL = "jev-1.14.0"  # pinned versioned id, checked 2026-11-15
PANEL_VERSION = "panel-static-1.0"

# Starting values from the vendor confidence guidance, not tested on your
# market: an answer at 0.70 or more counts, 0.35 to 0.70 is the review band.
THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

ACTION = "action"
ENGAGE_OPTIONS = ("stop", "click")
FIT = "fit"
FLAGS = ["hook_about_problem", "offer_clear", "distrust_claim"]

# The three options are mutually exclusive actions. run_panel.py rotates their
# order per pair to counter first-option bias; --order-check re-asks reversed.
QUESTIONS = {
    "action": {
        "type": "choice",
        "instructions": "`buyer` sees `ad` while scrolling a social feed on their phone. "
                        "What does `buyer` most likely do?",
        "criteria": {
            "scroll": "Keeps scrolling without reading the ad.",
            "stop": "Stops and reads the ad, then moves on without tapping.",
            "click": "Taps the ad to learn more or to start.",
        },
    },
    "hook_about_problem": {
        "type": "noul",
        "instructions": "The headline of `ad` is about a problem or a goal that `buyer` has.",
    },
    "offer_clear": {
        "type": "noul",
        "instructions": "From the headline, the image and the button of `ad` alone, `buyer` can tell "
                        "what is offered and on what terms.",
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


def build_items(concept):
    """One panel item per static concept. The offer line is what the viewer sees."""
    ad = {
        "headline": concept.get("headline", ""),
        "primary_text": concept.get("primary_text", ""),
        "button": concept.get("cta", ""),
        "offer": concept.get("offer_line") or concept.get("offer", ""),
        "image": concept.get("visual") or concept.get("layout", ""),
    }
    return [(concept["concept_id"], {k: v for k, v in ad.items() if v})]


def build_state(profile, ad_state):
    return {"buyer": build_profile_state(profile), "ad": ad_state}
