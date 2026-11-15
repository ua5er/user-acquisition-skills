"""Static track: Jev question set, state builder and code-computed features.

Every wording, option and threshold for static creatives lives in this one
module, so a change is a reviewable diff. Contract used by tag_creatives.py:

  TRACK, MODEL, TAXONOMY_VERSION
  QUESTIONS        question id -> question in the vendor request syntax
  CHOICE_COMPANION choice id -> id of its companion yes/no question
  FLAGS            yes/no questions reported as flags in the snapshot
  SCORES           score questions reported as averages
  build_state(d)   description record -> state (only the fields a judge needs)
  code_features(d) description record -> facts computed by code, never asked

The state is the text Claude wrote from the image. Images never go to Jev.
"""
import re

TRACK = "static"
MODEL = "jev-1.14.0"  # pinned versioned id (docs.typesafe.ai/models.md, checked 2026-11-15)
TAXONOMY_VERSION = "static-1.0"

# Starting values from the vendor guardrails cookbook and confidence page,
# not tested on your market: tag at 0.70 or more, a person reviews 0.35 to 0.70,
# below 0.35 a Choice stays untagged and a yes/no counts as no. Calibrate on
# about 100 of your own labelled ads before you trust the shares.
THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

# Choice: every option set ends with "other", and each Choice has a companion
# yes/no that asks whether a listed option fits. Option order is rotated per
# creative by tag_creatives.py ("other" stays last) to counter first-option bias.
QUESTIONS = {
    "hook_type": {
        "type": "choice",
        "instructions": "Which kind of hook does `headline` use to stop the scroll?",
        "criteria": {
            "problem_callout": "Names a pain or frustration the viewer has.",
            "outcome_promise": "Promises a result or a change.",
            "question": "Opens with a direct question to the viewer.",
            "social_proof": "Leads with user numbers, a rating, press or a review.",
            "curiosity": "Teases something without saying what it is.",
            "comparison": "Sets the product against an alternative or a competitor.",
            "offer_price": "Leads with a price, a discount or a free trial.",
            "other": "A different kind of hook.",
        },
    },
    "hook_type_fits": {
        "type": "noul",
        "instructions": "`headline` is clearly one of these hook types: a problem callout, an outcome promise, "
                        "a question, social proof, curiosity, a comparison, or a price or trial offer.",
    },
    "angle": {
        "type": "choice",
        "instructions": "What is the main reason to choose the product that `copy` and `visual` lead with?",
        "criteria": {
            "save_time": "Faster or easier, less effort.",
            "feel_better": "An emotional or wellbeing benefit.",
            "get_result": "A concrete outcome the viewer can check.",
            "save_money": "Cheaper than the alternative.",
            "belonging_status": "Being part of a group or looking good to others.",
            "fear_of_missing_out": "Act now or lose something.",
            "other": "A different main reason.",
        },
    },
    "angle_fits": {
        "type": "noul",
        "instructions": "The main reason given in `copy` is clearly one of these: saving time, feeling better, "
                        "a concrete result, saving money, belonging or status, or fear of missing out.",
    },
    "offer_type": {
        "type": "choice",
        "instructions": "What offer does `offer_line` or `copy` make?",
        "criteria": {
            "free_trial": "A free trial or a free start.",
            "discount": "A price cut or a promo price.",
            "freemium_download": "A free download with no price shown.",
            "price_stated": "A specific subscription price.",
            "none": "No offer, brand message only.",
            "other": "A different offer.",
        },
    },
    "offer_type_fits": {
        "type": "noul",
        "instructions": "The offer in `offer_line` is clearly one of these: a free trial, a discount, "
                        "a free download, a stated price, or no offer at all.",
    },
    "visual_format": {
        "type": "choice",
        "instructions": "Which visual type does `visual` describe?",
        "criteria": {
            "ugc_photo": "A phone-style photo of a real-looking person.",
            "app_screenshot": "A screenshot or mock-up of the app screen.",
            "text_card": "Mostly text on a plain or colour background.",
            "before_after": "Two states shown side by side.",
            "testimonial_card": "A quote or review card with a name or stars.",
            "illustration_3d": "An illustration, 3D render or icon art.",
            "meme_native": "A meme or platform-native look.",
            "lifestyle_stock": "A polished lifestyle or stock-style photo.",
            "other": "A different visual type.",
        },
    },
    "visual_format_fits": {
        "type": "noul",
        "instructions": "`visual` is clearly one of these: a phone photo of a person, an app screenshot, "
                        "a text card, a before and after, a testimonial card, an illustration, a meme, "
                        "or a lifestyle photo.",
    },
    "offer_placement": {
        "type": "choice",
        "instructions": "Where does `layout` put the offer or price?",
        "criteria": {
            "headline": "Inside the headline.",
            "badge_sticker": "On a badge, sticker or burst.",
            "cta_button": "On the button.",
            "footer_line": "In a small line near the bottom.",
            "not_shown": "The offer is not on the image.",
            "other": "Somewhere else.",
        },
    },
    "offer_placement_fits": {
        "type": "noul",
        "instructions": "`layout` puts the offer in one of these places: the headline, a badge, the button, "
                        "a bottom line, or nowhere on the image.",
    },
    "social_proof": {
        "type": "noul",
        "instructions": "The ad shows proof from other people, such as a rating, a user count, a review or press.",
    },
    "urgency": {
        "type": "noul",
        "instructions": "The ad sets a deadline, a countdown or limited supply.",
    },
    "risky_claim": {
        "type": "noul",
        "instructions": "The ad states a health result, an income result, a guaranteed result or a before and "
                        "after result that an ad platform may reject.",
    },
    "personal_attribute": {
        "type": "noul",
        "instructions": "`copy` addresses a personal condition of the viewer directly, for example 'your insomnia'.",
    },
    "hook_specificity": {
        "type": "score",
        "instructions": "How specific is `headline` about who it is for and what it promises?",
        "criteria": [
            "It fits almost any app.",
            "It names the audience or the promise, not both.",
            "It names the audience and a concrete promise.",
            "It names the audience, a promise and a number or a timeframe.",
        ],
    },
    "cta_clarity": {
        "type": "score",
        "instructions": "How clear is what happens after the tap, given `cta_label` and `copy`?",
        "criteria": [
            "A viewer cannot tell what happens after the tap.",
            "A viewer can guess the next step.",
            "A viewer sees the next step and what it costs.",
        ],
    },
    "legibility": {
        "type": "score",
        "instructions": "How easy is the main message to read at phone size, given `layout` and `text_blocks`?",
        "criteria": [
            "Small, cluttered or low contrast text.",
            "Readable with effort.",
            "Clear at a glance.",
        ],
    },
}

CHOICE_COMPANION = {
    "hook_type": "hook_type_fits",
    "angle": "angle_fits",
    "offer_type": "offer_type_fits",
    "visual_format": "visual_format_fits",
    "offer_placement": "offer_placement_fits",
}
FLAGS = ["social_proof", "urgency", "risky_claim", "personal_attribute"]
SCORES = ["hook_specificity", "cta_clarity", "legibility"]

PRICE_RE = re.compile(r"(\$|USD|EUR|€|£|zl\b|zł)\s?\d|\d+([.,]\d{2})?\s?(\$|USD|EUR|€|£)"
                      r"|\b\d+\s?%\s?off\b|\bper (month|week|year)\b|/(mo|month|wk|week|yr|year)\b", re.I)


def _blocks_text(d):
    return " ".join(b.get("text", "") for b in d.get("text_blocks", []))


def build_state(d):
    """Only what a person judging the ad would look at. No advertiser, no ids."""
    return {
        "headline": d.get("headline", ""),
        "copy": (d.get("copy") or "")[:800],
        "cta_label": d.get("cta_label") or "(no button)",
        "offer_line": d.get("offer_line") or "(none stated)",
        "text_blocks": [{"role": b.get("role", ""), "text": b.get("text", ""), "position": b.get("position", "")}
                        for b in d.get("text_blocks", [])],
        "layout": d.get("layout", ""),
        "visual": d.get("visual", ""),
    }


def code_features(d):
    """Facts code can compute exactly. Jev is never asked to count."""
    on_image = _blocks_text(d)
    everything = " ".join([d.get("headline", ""), d.get("copy", ""), d.get("offer_line", ""), on_image])
    return {
        "words_on_image": len(on_image.split()),
        "text_blocks": len(d.get("text_blocks", [])),
        "has_price": bool(PRICE_RE.search(everything)),
        "aspect_ratios": sorted(d.get("aspect_ratios", [])),
        "cta_label": (d.get("cta_label") or "(no button)").strip(),
    }
