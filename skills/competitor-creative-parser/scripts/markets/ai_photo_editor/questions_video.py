"""Video track, market taxonomy: AI photo editor apps (Meta, US, November 2026).

Drafted by Claude from a first read of the captured descriptions, so every
option is something this market really runs. Built for an ad library capture:
no audio and no transcript, so every question reads fields that exist
(`first_3s`, `on_screen_text`, `format_notes` and the ad text).
"""

TRACK = "video"
MODEL = "jev-1.14.0"
TAXONOMY_VERSION = "ai-photo-video-1.1"
THRESHOLDS = {"tag": 0.70, "review_low": 0.35}

QUESTIONS = {
    "use_case": {
        "type": "choice",
        "instructions": "What does the app in this ad do with the viewer's photo?",
        "criteria": {
            "pro_headshot": "Turns selfies into professional headshots or business portraits.",
            "ai_photoshoot": "Creates a photo shoot of the person or a couple in new outfits or settings, "
                             "for example studio fashion shots, a birthday set or an old money portrait.",
            "fantasy_scene": "Puts the person into an aspirational or cinematic scene, for example a luxury car, "
                             "a film scene or a stage.",
            "funny_animation": "Animates a photo of a pet or a person into a funny clip, for example dancing or singing.",
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
    "hook_type": {
        "type": "choice",
        "instructions": "Which kind of hook do the first three seconds in `first_3s` use?",
        "criteria": {
            "first_person_caption": "A caption written as the user talking about their own result, for example "
                                    "'Me in my dream car' or 'How I pull up'.",
            "result_reveal": "Shows the finished result right away, with no caption.",
            "transformation": "Shows a change happening on screen, from a starting photo or face to a new look.",
            "tool_demo": "Shows the app or software being used.",
            "person_talks": "A person speaks to the camera or reacts to something.",
            "instruction_caption": "A caption that tells the viewer what to do or what they get, for example "
                                   "upload a photo.",
            "question_caption": "A caption that asks the viewer a question or teases how something is done.",
            "other": "A different kind of hook.",
        },
    },
    "hook_type_fits": {
        "type": "noul",
        "instructions": "`first_3s` clearly opens in one of these ways: a caption in the user's own voice, a finished "
                        "result with no caption, a change happening on screen, the app or software in use, a person "
                        "speaking or reacting, a caption that tells the viewer what to do or what they get, or a caption "
                        "that asks a question.",
    },
    "proof_device": {
        "type": "choice",
        "instructions": "How does the video show that the result comes from the viewer's own photo?",
        "criteria": {
            "source_inset": "A small copy of the original photo stays on screen next to or over the result.",
            "before_after": "The original and the result are shown one after the other or side by side at a "
                            "similar size.",
            "app_ui": "The app or software screen is shown doing the edit.",
            "creator_says": "A person says or shows that they made it.",
            "other": "None of these, for example only the finished result is shown.",
        },
    },
    "proof_device_fits": {
        "type": "noul",
        "instructions": "It is clear from the description which of these is true: a small copy of the original photo "
                        "is on screen, the original and the result are both shown at a similar size, the app screen "
                        "is shown doing the edit, or a person says they made it.",
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
    "video_format": {
        "type": "choice",
        "instructions": "Which production format is the video, going by `format_notes` and `first_3s`?",
        "criteria": {
            "ai_generated_clip": "The footage itself is AI generated.",
            "real_footage": "Filmed footage of real people, hands or places, with no one talking to the camera.",
            "screen_recording": "A recording of an app or software screen.",
            "talking_head": "A person talks to the camera.",
            "still_slideshow": "A series of still images with little motion.",
            "other": "A different format.",
        },
    },
    "video_format_fits": {
        "type": "noul",
        "instructions": "The video is clearly one of these: AI generated footage, filmed real footage, a screen "
                        "recording, a person talking to the camera, or a slideshow of still images.",
    },
    "offer_type": {
        "type": "choice",
        "instructions": "Which offer does the ad state in its text or on screen?",
        "criteria": {
            "free_preview": "See the results for free and pay only to keep or download them.",
            "free_trial": "A free trial for a set time.",
            "free_start": "A free download, free sign-up or free credits.",
            "discount": "A discount or a sale price.",
            "price_stated": "A price with no discount.",
            "other": "No offer is stated, or a different kind of offer.",
        },
    },
    "offer_type_fits": {
        "type": "noul",
        "instructions": "The ad states an offer: a free preview, a free trial, a free download, free sign-up or "
                        "free credits, a discount, or a price.",
    },
    "text_in_first_3s": {
        "type": "noul",
        "instructions": "A caption or other text is on screen within the first three seconds, going by `first_3s` "
                        "and `on_screen_text`.",
    },
    "source_photo_shown": {
        "type": "noul",
        "instructions": "The original photo that the user uploads is visible in the video.",
    },
    "one_photo_claim": {
        "type": "noul",
        "instructions": "The ad says or shows in text that one photo or one selfie is enough.",
    },
    "ai_named": {
        "type": "noul",
        "instructions": "The ad text or the on-screen text uses the word AI.",
    },
    "says_free": {
        "type": "noul",
        "instructions": "The ad text or the on-screen text says free, in any language.",
    },
    "known_likeness": {
        "type": "noul",
        "instructions": "The video shows a famous person, a known character or a luxury brand.",
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
    "hook_specificity": {
        "type": "score",
        "instructions": "How clearly do the first three seconds in `first_3s` show what the viewer gets?",
        "criteria": [
            "It could be an ad for almost any app.",
            "It shows a result, but not that it comes from the viewer's own photo.",
            "It shows the result and that it comes from the viewer's own photo.",
            "It shows the result, the viewer's own photo and how little it takes, for example one photo.",
        ],
    },
}

CHOICE_COMPANION = {
    "use_case": "use_case_fits",
    "hook_type": "hook_type_fits",
    "proof_device": "proof_device_fits",
    "angle": "angle_fits",
    "video_format": "video_format_fits",
    "offer_type": "offer_type_fits",
}
FLAGS = ["text_in_first_3s", "source_photo_shown", "one_photo_claim", "ai_named", "says_free",
         "known_likeness", "price_shown", "social_proof", "urgency"]
SCORES = ["hook_specificity"]


def build_state(d):
    """What a person judging the ad from the library page can see. No advertiser, no ids, no audio."""
    return {
        "first_3s": d.get("first_3s", ""),
        "on_screen_text": d.get("on_screen_text", []),
        "format_notes": d.get("format_notes", ""),
        "ad_text": (d.get("copy") or "")[:800],
        "link_headline": d.get("link_headline") or d.get("headline") or "",
        "cta_label": d.get("cta_label") or "(no button)",
        "offer_line": d.get("offer_line") or "(none stated)",
    }


def code_features(d):
    duration = float(d.get("duration_s") or 0)
    cuts = sorted(float(t) for t in d.get("cut_times_s", []) if 0 < float(t) < duration) if duration else []
    shots = len(cuts) + 1 if duration else 0
    return {
        "duration_s": round(duration, 1) if duration else None,
        "cuts": len(cuts) if duration else None,
        "cuts_per_10s": round(len(cuts) / duration * 10, 2) if duration else None,
        "avg_shot_s": round(duration / shots, 2) if shots else None,
        "captions": d.get("captions"),
        "has_transcript": False,
        "cta_label": (d.get("cta_label") or "(no button)").strip(),
        "lang": d.get("lang") or "en",
    }
