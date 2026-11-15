"""Video track: Jev question set, state builder and code-computed features.

Same contract as questions_static.py. The video file never goes to Jev: Claude
writes the first three seconds, on-screen text, format notes and end card from
sampled frames, a local speech-to-text run gives the transcript, and code
computes duration and pacing from the cut times. Pacing is reported as numbers
by code, not judged by the model (the vendor lists numbers as a weak spot).
"""

TRACK = "video"
MODEL = "jev-1.14.0"
TAXONOMY_VERSION = "video-1.0"

# Starting values from the vendor guardrails cookbook and confidence page,
# not tested on your market: tag at 0.70 or more, a person reviews 0.35 to 0.70,
# below 0.35 a Choice stays untagged and a yes/no counts as no. Calibrate on
# about 100 of your own labelled ads before you trust the shares.
THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

QUESTIONS = {
    "hook_type": {
        "type": "choice",
        "instructions": "Which kind of hook do the first three seconds in `first_3s` use?",
        "criteria": {
            "problem_callout": "Names a pain the viewer has.",
            "bold_claim": "A strong promise or a surprising claim.",
            "question": "A direct question to the viewer.",
            "pattern_interrupt": "An unexpected image, action or sound.",
            "demo_first": "Starts with the product in use.",
            "story_opener": "Starts a personal story.",
            "social_proof": "Starts with numbers or other people's results.",
            "other": "A different kind of hook.",
        },
    },
    "hook_type_fits": {
        "type": "noul",
        "instructions": "`first_3s` is clearly one of these hook types: a problem callout, a bold claim, "
                        "a question, a pattern interrupt, a product demo, a story opener, or social proof.",
    },
    "hook_channel": {
        "type": "choice",
        "instructions": "What mainly carries the hook in `first_3s`?",
        "criteria": {
            "spoken_line": "A spoken sentence.",
            "on_screen_text": "Text on the screen.",
            "visual_action": "What is shown happening.",
            "sound": "Music or a sound effect.",
            "other": "Something else.",
        },
    },
    "hook_channel_fits": {
        "type": "noul",
        "instructions": "The hook in `first_3s` is carried mainly by speech, on-screen text, an action shown, "
                        "or a sound.",
    },
    "angle": {
        "type": "choice",
        "instructions": "What is the main reason to choose the product that `transcript` leads with?",
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
        "instructions": "The main reason given in `transcript` is clearly one of these: saving time, feeling "
                        "better, a concrete result, saving money, belonging or status, or fear of missing out.",
    },
    "video_format": {
        "type": "choice",
        "instructions": "Which production format is the ad, judging by `format_notes`?",
        "criteria": {
            "ugc_talking_head": "A person speaks to the camera with a phone look.",
            "screen_recording": "Mostly a recording of the app screen.",
            "motion_graphics": "Animated text, shapes or illustration.",
            "voiceover_broll": "A voice over footage or stock clips.",
            "split_screen_reaction": "Two panels, one person reacting.",
            "skit_dramatized": "A scripted scene with actors.",
            "slideshow_static": "Still images with text.",
            "other": "A different format.",
        },
    },
    "video_format_fits": {
        "type": "noul",
        "instructions": "`format_notes` clearly describes one of these: a talking head, a screen recording, "
                        "motion graphics, voice over footage, a split-screen reaction, a scripted skit, "
                        "or a slideshow.",
    },
    "structure": {
        "type": "choice",
        "instructions": "Which structure does the whole `transcript` follow?",
        "criteria": {
            "problem_solution": "A problem, then the product solves it.",
            "demo_walkthrough": "Step by step product use.",
            "testimonial_story": "A person tells their result.",
            "listicle_tips": "A list of tips or reasons.",
            "before_after": "A starting state, then a result.",
            "challenge_trend": "Follows a trend or challenge format.",
            "other": "A different structure.",
        },
    },
    "structure_fits": {
        "type": "noul",
        "instructions": "`transcript` clearly follows one of these structures: problem then solution, a "
                        "walkthrough, a testimonial story, a list of tips, before and after, or a trend format.",
    },
    "creator_type": {
        "type": "choice",
        "instructions": "Who appears or speaks, according to `format_notes`?",
        "criteria": {
            "everyday_person": "Someone who looks like an ordinary user.",
            "expert_authority": "A doctor, coach or other professional.",
            "influencer": "A creator presented as well known.",
            "faceless": "Nobody appears, voice or text only.",
            "other": "Someone else.",
        },
    },
    "creator_type_fits": {
        "type": "noul",
        "instructions": "The person in `format_notes` is clearly an ordinary user, a professional, a known "
                        "creator, or nobody appears.",
    },
    "offer_type": {
        "type": "choice",
        "instructions": "What offer does `end_card` or `transcript` make?",
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
        "instructions": "The offer in `end_card` is clearly one of these: a free trial, a discount, a free "
                        "download, a stated price, or no offer at all.",
    },
    "product_in_first_3s": {
        "type": "noul",
        "instructions": "The app or product is shown or named in `first_3s`.",
    },
    "cta_in_end": {
        "type": "noul",
        "instructions": "`end_card` asks the viewer to do one specific thing.",
    },
    "social_proof": {
        "type": "noul",
        "instructions": "The ad cites ratings, user numbers or other people's results.",
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
        "instructions": "`transcript` addresses a personal condition of the viewer directly, for example "
                        "'your insomnia'.",
    },
    "hook_specificity": {
        "type": "score",
        "instructions": "How specific is `first_3s` about who it is for and what it promises?",
        "criteria": [
            "It fits almost any app.",
            "It names the audience or the promise, not both.",
            "It names the audience and a concrete promise.",
            "It names the audience, a promise and a number or a timeframe.",
        ],
    },
}

CHOICE_COMPANION = {
    "hook_type": "hook_type_fits",
    "hook_channel": "hook_channel_fits",
    "angle": "angle_fits",
    "video_format": "video_format_fits",
    "structure": "structure_fits",
    "creator_type": "creator_type_fits",
    "offer_type": "offer_type_fits",
}
FLAGS = ["product_in_first_3s", "cta_in_end", "social_proof", "urgency", "risky_claim", "personal_attribute"]
SCORES = ["hook_specificity"]


def build_state(d):
    """Only what a person judging the video would look at. No advertiser, no ids."""
    return {
        "first_3s": d.get("first_3s", ""),
        "hook_spoken": d.get("hook_spoken") or "(nothing spoken)",
        "on_screen_text": d.get("on_screen_text", []),
        "format_notes": d.get("format_notes", ""),
        "transcript": (d.get("transcript") or "")[:1500],
        "end_card": d.get("end_card") or "(no end card)",
    }


def code_features(d):
    """Duration and pacing from cut times (Claude's frame notes or a local scene-detection run)."""
    duration = float(d.get("duration_s") or 0)
    cuts = sorted(float(t) for t in d.get("cut_times_s", []) if 0 < float(t) < duration) if duration else []
    shots = len(cuts) + 1 if duration else 0
    return {
        "duration_s": round(duration, 1) if duration else None,
        "cuts": len(cuts) if duration else None,
        "cuts_per_10s": round(len(cuts) / duration * 10, 2) if duration else None,
        "avg_shot_s": round(duration / shots, 2) if shots else None,
        "captions": d.get("captions"),
        "has_transcript": bool((d.get("transcript") or "").strip()),
    }
