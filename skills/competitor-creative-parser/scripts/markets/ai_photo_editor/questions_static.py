"""Static track, market taxonomy: AI photo editor apps (Meta, US, November 2026).

Drafted by Claude from a first read of the captured descriptions, so every
option is something this market really runs. The state is the text Claude
wrote from the image; images never go to Jev.
"""
import re

TRACK = "static"
MODEL = "jev-1.14.0"
TAXONOMY_VERSION = "ai-photo-static-1.1"
THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

QUESTIONS = {
    "use_case": {
        "type": "choice",
        "instructions": "What does the app in this ad do with the viewer's photo?",
        "criteria": {
            "pro_headshot": "Turns selfies into professional headshots or business portraits.",
            "ai_photoshoot": "Creates a photo shoot of the person or a couple in new outfits or settings, "
                             "for example studio fashion shots, a birthday set or a vintage style portrait.",
            "fantasy_scene": "Puts the person into an aspirational or cinematic scene, for example a luxury car, "
                             "a film scene or a stage.",
            "funny_animation": "Animates a photo of a pet or a person into a funny clip.",
            "photo_restoration": "Repairs, sharpens or colours an old or damaged photo.",
            "beauty_makeover": "Changes makeup, hair or face features, or enhances a selfie.",
            "retouch_tool": "A photo editing, retouching or collage tool that the user operates.",
            "art_style_portrait": "Turns a person or a pet into an art style portrait, for example watercolor "
                                  "or cartoon.",
            "try_on": "Shows clothes or products on the person.",
            "other": "Something else, or it is not clear.",
        },
    },
    "use_case_fits": {
        "type": "noul",
        "instructions": "The ad makes clear what the app does with a photo, and it is one of these: professional "
                        "headshots, a photo shoot in new outfits or settings, an aspirational or cinematic scene, "
                        "a funny animated clip, restoring an old photo, a makeup or hair makeover, an editing or "
                        "collage tool, an art style portrait, or trying on clothes.",
    },
    "layout": {
        "type": "choice",
        "instructions": "Which layout does the image use, going by `layout` and `visual`?",
        "criteria": {
            "small_to_large": "A small starting photo with an arrow or a label pointing to a larger result.",
            "split_before_after": "Two halves or panels of similar size, before and after.",
            "stages_strip": "Three or more stages of the same photo in a row.",
            "single_result": "One large result image with text.",
            "detail_zoom": "A result image with a magnified detail.",
            "collage": "Several different result images together.",
            "text_card": "A designed card where text, a quote or a price comparison carries the message and "
                         "the photo is secondary.",
            "other": "A different layout.",
        },
    },
    "layout_fits": {
        "type": "noul",
        "instructions": "The image clearly uses one of these layouts: a small starting photo pointing to a larger "
                        "result, two before and after panels of similar size, three or more stages in a row, "
                        "one large result image, a result with a magnified detail, a collage of results, or a text-led card.",
    },
    "headline_type": {
        "type": "choice",
        "instructions": "Which kind of message is the main on-image headline in `headline`?",
        "criteria": {
            "outcome_promise": "Promises how the viewer or their photo will look.",
            "emotional_appeal": "Speaks about a loved one or a feeling.",
            "product_claim": "States what the product is, or that it is the best or the most realistic.",
            "challenge": "Dares the viewer to check the quality, for example to zoom in.",
            "feature_name": "Names a feature, a preset or a mode.",
            "price_or_offer": "Leads with a price, a saving or a free offer.",
            "other": "A different kind of headline.",
        },
    },
    "headline_type_fits": {
        "type": "noul",
        "instructions": "`headline` is clearly one of these: a promise about how the viewer or their photo will "
                        "look, an appeal about a loved one or a feeling, a claim about what the product is or how "
                        "good it is, a dare to check the quality, the name of a feature, or a price or a free offer.",
    },
    "angle": {
        "type": "choice",
        "instructions": "What is the main reason to try the app that the ad leads with?",
        "criteria": {
            "status_career": "Look professional or successful to other people.",
            "fantasy_fun": "Fun or fantasy: the result is entertaining or aspirational to look at and share.",
            "loved_ones": "For family, loved ones or pets: a memory or a gift.",
            "look_better": "Look more attractive.",
            "speed_ease": "It is fast or easy: one photo, a few seconds, no skills.",
            "save_money": "It costs less than the usual way, for example a photographer.",
            "realism_quality": "The result looks real or high quality.",
            "trend": "Join a trend that other people are doing.",
            "other": "A different reason, or none is given.",
        },
    },
    "angle_fits": {
        "type": "noul",
        "instructions": "The ad leads with one clear reason to try the app, and it is one of these: looking "
                        "professional or successful, fun or fantasy, family, loved ones or pets, looking more "
                        "attractive, speed or ease, a lower cost, realistic quality, or joining a trend.",
    },
    "offer_type": {
        "type": "choice",
        "instructions": "Which offer does the ad state in its text or on the image?",
        "criteria": {
            "free_preview": "See the results for free and pay only to keep or download them.",
            "free_trial": "A free trial for a set time.",
            "free_start": "A free download, free sign-up, free credits or a free gift.",
            "discount": "A discount or a sale price.",
            "price_stated": "A price with no discount.",
            "other": "No offer is stated, or a different kind of offer.",
        },
    },
    "offer_type_fits": {
        "type": "noul",
        "instructions": "The ad states an offer: a free preview, a free trial, a free download, free sign-up, "
                        "free credits or a free gift, a discount, or a price.",
    },
    "source_photo_shown": {
        "type": "noul",
        "instructions": "The original photo that the user uploads is visible in the image.",
    },
    "one_photo_claim": {
        "type": "noul",
        "instructions": "The ad says that selfies, or one photo, are all it takes.",
    },
    "ai_named": {
        "type": "noul",
        "instructions": "The ad text or the on-image text uses the word AI.",
    },
    "says_free": {
        "type": "noul",
        "instructions": "The ad text or the on-image text says free, in any language.",
    },
    "known_likeness": {
        "type": "noul",
        "instructions": "The image shows a famous person, a known character or a luxury brand.",
    },
    "price_shown": {
        "type": "noul",
        "instructions": "A price in money is shown in the ad text or in the creative.",
    },
    "social_proof": {
        "type": "noul",
        "instructions": "The ad cites ratings, user numbers, awards or other people's results.",
    },
    "urgency": {
        "type": "noul",
        "instructions": "The ad sets a deadline, a countdown or limited supply.",
    },
    "headline_specificity": {
        "type": "score",
        "instructions": "How specific is `headline` about the result and who it is for?",
        "criteria": [
            "It fits almost any app.",
            "It names the result or the audience, not both.",
            "It names the result and who it is for or where it is used.",
            "It names the result, who it is for and a concrete proof or number.",
        ],
    },
}

CHOICE_COMPANION = {
    "use_case": "use_case_fits",
    "layout": "layout_fits",
    "headline_type": "headline_type_fits",
    "angle": "angle_fits",
    "offer_type": "offer_type_fits",
}
FLAGS = ["source_photo_shown", "one_photo_claim", "ai_named", "says_free", "known_likeness",
         "price_shown", "social_proof", "urgency"]
SCORES = ["headline_specificity"]

PRICE_RE = re.compile(r"(\$|USD|EUR|€|£)\s?\d|\d+([.,]\d{2})?\s?(\$|USD|EUR|€|£)"
                      r"|\b\d+\s?%\s?off\b|\bper (month|week|year)\b|/(mo|month|wk|week|yr|year)\b", re.I)


def _blocks_text(d):
    return " ".join(b.get("text", "") for b in d.get("text_blocks", []))


def build_state(d):
    """What a person judging the ad would look at. No advertiser, no ids."""
    return {
        "headline": d.get("headline", ""),
        "ad_text": (d.get("copy") or "")[:800],
        "link_headline": d.get("link_headline") or "",
        "link_description": d.get("link_description") or "",
        "cta_label": d.get("cta_label") or "(no button)",
        "offer_line": d.get("offer_line") or "(none stated)",
        "text_blocks": [{"role": b.get("role", ""), "text": b.get("text", ""), "position": b.get("position", "")}
                        for b in d.get("text_blocks", [])],
        "layout": d.get("layout", ""),
        "visual": d.get("visual", ""),
    }


def code_features(d):
    on_image = _blocks_text(d)
    everything = " ".join([d.get("headline", ""), d.get("copy", ""), d.get("offer_line", ""), on_image])
    return {
        "words_on_image": len(on_image.split()),
        "text_blocks": len(d.get("text_blocks", [])),
        "has_price": bool(PRICE_RE.search(everything)),
        "aspect_ratios": sorted(d.get("aspect_ratios", [])),
        "cta_label": (d.get("cta_label") or "(no button)").strip(),
        "lang": d.get("lang") or "en",
    }
