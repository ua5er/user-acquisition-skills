#!/usr/bin/env python3
"""Offline tests for the pre-flight panel scripts. No network, no key.

The results used in the calibration tests are synthetic test fixtures, not
measurements of anything.

  python3 test_offline.py
"""
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_matrix  # noqa: E402
import panel_vs_results  # noqa: E402
import run_panel  # noqa: E402

SAMPLE = os.path.join(HERE, "sample_panel")


def quiet(fn, *a, **k):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def qs(track):
    return run_panel.load_question_set(os.path.join(HERE, "questions_%s.py" % track))


def answer(scroll, stop, click, fit, hook=0.9, offer=0.9, distrust=0.1):
    probs = {"scroll": scroll, "stop": stop, "click": click}
    top = max(probs, key=probs.get)
    return {"action": {"type": "choice", "choice": top, "probabilities": probs, "confidence": 0.5},
            "hook_about_problem": {"type": "noul", "p_yes": hook}, "offer_clear": {"type": "noul", "p_yes": offer},
            "distrust_claim": {"type": "noul", "p_yes": distrust},
            "fit": {"type": "score", "score": fit, "probabilities": {}, "confidence": 0.5}}


def rows_for(item, answers, track="static", concept=None):
    return [{"item_id": item, "concept_id": concept or item.split("-")[0], "profile_id": "p%02d" % (i + 1),
             "track": track, "status": "ok", "answers": a} for i, a in enumerate(answers)]


class QuestionSetTest(unittest.TestCase):
    def test_both_sets_load(self):
        for t in ("static", "video"):
            ns = qs(t)
            self.assertEqual(ns["TRACK"], t)
            self.assertEqual(list(ns["QUESTIONS"]["action"]["criteria"]), ["scroll", "stop", "click"])

    def test_video_items_per_hook(self):
        concepts = run_panel.load_jsonl(os.path.join(SAMPLE, "concepts.jsonl"))
        m1 = next(c for c in concepts if c["concept_id"] == "M1")
        items = qs("video")["build_items"](m1)
        self.assertEqual([i for i, _ in items], ["M1-A", "M1-B", "M1-C"])
        self.assertIn("first_3s", items[0][1])
        self.assertNotIn("hook variant", items[0][1]["rest_of_video"])

    def test_state_has_only_profile_fields(self):
        profiles = run_panel.load_jsonl(os.path.join(SAMPLE, "profiles.jsonl"))
        st = qs("static")["build_state"](profiles[0], {"headline": "x"})
        self.assertEqual(set(st["buyer"]), {"situation", "goal", "objections", "stops_scrolling_for"})
        self.assertNotIn("label", json.dumps(st))

    def test_rotation_keeps_options(self):
        q = qs("static")["QUESTIONS"]["action"]
        seen = set()
        for k in range(30):
            rq, off = run_panel.rotated_choice(q, "S1|p%02d" % k)
            self.assertEqual(set(rq["criteria"]), {"scroll", "stop", "click"})
            seen.add(tuple(rq["criteria"]))
        self.assertGreater(len(seen), 1)
        rev, off = run_panel.rotated_choice(q, "x", reverse=True)
        self.assertEqual(list(rev["criteria"]), ["click", "stop", "scroll"])

    def test_profiles_validation(self):
        with self.assertRaises(ValueError):
            run_panel.validate_profiles([{"profile_id": "a", "situation": "s", "goal": "g", "objections": "o"}])
        with self.assertRaises(ValueError):
            good = {"situation": "s", "goal": "g", "objections": "o", "stops_scrolling_for": "x"}
            run_panel.validate_profiles([dict(good, profile_id="a"), dict(good, profile_id="a")])


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.concepts = os.path.join(SAMPLE, "concepts.jsonl")
        self.profiles = os.path.join(SAMPLE, "profiles.jsonl")

    def test_dry_run_both_tracks(self):
        for track, items in (("static", 3), ("video", 9)):
            rc = quiet(run_panel.main, ["--concepts", self.concepts, "--profiles", self.profiles, "--track", track,
                                        "--dry-run", "--order-check", "2", "--out-dir", self.tmp])
            self.assertEqual(rc, 0)
            summary = json.load(open(os.path.join(self.tmp, "run-%s.json" % track)))
            self.assertEqual(summary["items"], items)
            self.assertEqual(summary["pairs"], items * 12)
            self.assertEqual(summary["requests"], items * 12 + 2)
            self.assertEqual(summary["source"], "mock")

    def test_live_needs_key_and_confirmation(self):
        env = os.environ.pop("TYPESAFE_API_KEY", None)
        try:
            rc = quiet(run_panel.main, ["--concepts", self.concepts, "--profiles", self.profiles, "--track", "static"])
            self.assertEqual(rc, 2)
            os.environ["PANEL_TEST_KEY"] = "not-a-real-key"
            rc = quiet(run_panel.main, ["--concepts", self.concepts, "--profiles", self.profiles, "--track", "static",
                                        "--key-env", "PANEL_TEST_KEY"])
            self.assertEqual(rc, 2)
        finally:
            os.environ.pop("PANEL_TEST_KEY", None)
            if env is not None:
                os.environ["TYPESAFE_API_KEY"] = env

    def test_refuses_http(self):
        rc = quiet(run_panel.main, ["--concepts", self.concepts, "--profiles", self.profiles, "--track", "static",
                                    "--dry-run", "--base-url", "http://example.com"])
        self.assertEqual(rc, 2)

    def test_spend_guard(self):
        ns = qs("static")
        pairs = run_panel.build_pairs(run_panel.load_jsonl(self.concepts), run_panel.load_jsonl(self.profiles), ns)
        recs, summary, _ = run_panel.run(pairs, ns, run_panel.mock_post, max_usd=0.00003, source="mock", log=lambda *_: None)
        self.assertGreater(summary["skipped_by_guard"], 0)
        self.assertLess(summary["pairs"], len(pairs))

    def test_errors_never_become_answers(self):
        ns = qs("static")
        pairs = run_panel.build_pairs(run_panel.load_jsonl(self.concepts), run_panel.load_jsonl(self.profiles), ns)[:3]

        def bad(url, key, body, timeout=60):
            return 400, {"detail": "bad request"}, {}

        recs, summary, _ = run_panel.run(pairs, ns, bad, source="mock")
        self.assertEqual(summary["errors"], 3)
        self.assertTrue(all(r["status"] == "error" and not r["answers"] for r in recs))
        result = panel_matrix.build(recs, [])
        self.assertEqual(result["items"][0]["verdict"], "no verdict")

    def test_shape_error(self):
        ns = qs("static")
        with self.assertRaises(run_panel.ResponseShapeError):
            run_panel.parse_response({"answers": {"action": {"type": "choice", "choice": "maybe",
                                                             "probabilities": {"x": 1}, "confidence": 1}}},
                                     ns["QUESTIONS"])

    def test_retry_then_success(self):
        calls = []

        def flaky(url, key, body, timeout=60):
            calls.append(1)
            return (429, {}, {"Retry-After": "0"}) if len(calls) < 3 else (200, {"answers": {}}, {})

        out = run_panel.call_with_retry(flaky, "u", "k", {}, sleep=lambda s: None, rng=lambda: 0)
        self.assertEqual(out, {"answers": {}})
        self.assertEqual(len(calls), 3)


class MatrixTest(unittest.TestCase):
    def test_go_rework_drop(self):
        go = rows_for("S1", [answer(0.05, 0.15, 0.8, 2.6)] * 12)
        rework = rows_for("S2", [answer(0.05, 0.15, 0.8, 2.6, distrust=0.9)] * 12)
        drop = rows_for("S3", [answer(0.9, 0.05, 0.05, 0.5)] * 12)
        res = panel_matrix.build(go + rework + drop, [])
        v = {s["item_id"]: s["verdict"] for s in res["items"]}
        self.assertEqual(v, {"S1": "go", "S2": "rework", "S3": "drop"})
        s3 = next(s for s in res["items"] if s["item_id"] == "S3")
        self.assertEqual(len(s3["loses"]), 12)

    def test_thin_lead_names_no_winner(self):
        a = rows_for("S1", [answer(0.3, 0.4, 0.3, 2.5)] * 12)
        b = rows_for("S2", [answer(0.35, 0.35, 0.3, 2.5)] * 12)
        res = panel_matrix.build(a + b, [])
        self.assertTrue(res["tracks"]["static"]["ranking_note"].startswith("no leader"))

    def test_clear_lead(self):
        a = rows_for("S1", [answer(0.1, 0.4, 0.5, 2.5)] * 12)
        b = rows_for("S2", [answer(0.6, 0.2, 0.2, 2.5)] * 12)
        res = panel_matrix.build(a + b, [])
        self.assertTrue(res["tracks"]["static"]["ranking_note"].startswith("leader S1"))

    def test_low_sample_no_ranking(self):
        a = rows_for("S1", [answer(0.1, 0.4, 0.5, 2.5)] * 6)
        b = rows_for("S2", [answer(0.6, 0.2, 0.2, 2.5)] * 6)
        res = panel_matrix.build(a + b, [])
        self.assertTrue(res["tracks"]["static"]["low_sample"])
        self.assertIsNone(res["items"][0]["rank"])
        self.assertTrue(any("directional" in r for r in res["items"][0]["reasons"]))
        panel_matrix.MIN_PROFILES = 12

    def test_uncertain_blocks_go(self):
        rows = rows_for("S1", [answer(0.45, 0.3, 0.25, 2.6)] * 12)  # stop or click 0.55: in the band
        res = panel_matrix.build(rows, [])
        self.assertEqual(res["items"][0]["verdict"], "rework")
        self.assertTrue(any("review band" in r for r in res["items"][0]["reasons"]))

    def test_video_rollup_best_hook(self):
        a = rows_for("M1-A", [answer(0.9, 0.05, 0.05, 0.5)] * 12, track="video")
        b = rows_for("M1-B", [answer(0.05, 0.15, 0.8, 2.6)] * 12, track="video")
        res = panel_matrix.build(a + b, [])
        c = res["concepts"][0]
        self.assertEqual((c["concept_id"], c["verdict"], c["best_item"]), ("M1", "go", "M1-B"))
        self.assertEqual(c["items"], {"M1-A": "drop", "M1-B": "go"})

    def test_trailing_hook_reworked(self):
        a = rows_for("M1-A", [answer(0.05, 0.15, 0.8, 2.6)] * 12, track="video")
        b = rows_for("M1-B", [answer(0.2, 0.7, 0.1, 2.6)] * 12, track="video")
        res = panel_matrix.build(a + b, [])
        v = {s["item_id"]: s for s in res["items"]}
        self.assertEqual(v["M1-A"]["verdict"], "go")
        self.assertEqual(v["M1-B"]["verdict"], "rework")
        self.assertTrue(v["M1-B"]["reasons"][0].startswith("trails hook M1-A"))

    def test_outputs_and_no_dashes(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "answers-static.jsonl")
        with open(path, "w") as fh:
            for r in rows_for("S1", [answer(0.05, 0.15, 0.8, 2.6)] * 12):
                fh.write(json.dumps(r) + "\n")
        rc = quiet(panel_matrix.main, ["--answers", path, "--profiles", os.path.join(SAMPLE, "profiles.jsonl"),
                                       "--out-dir", tmp])
        self.assertEqual(rc, 0)
        md = open(os.path.join(tmp, "matrix.md"), encoding="utf-8").read()
        self.assertIn("not proof of performance", md)
        self.assertNotIn("\u2014", md)
        self.assertNotIn("\u2013", md)
        with open(os.path.join(tmp, "matrix-static.csv")) as fh:
            rows = list(csv.reader(fh))
        self.assertEqual(rows[0][:3], ["item_id", "concept_id", "engage_mean"])
        self.assertEqual(len(rows[0]), 3 + 12)


class CalibrationTest(unittest.TestCase):
    """Synthetic fixtures only: these numbers measure nothing."""

    def verdicts(self, scores):
        return {"items": [{"item_id": k, "track": "static", "verdict": v, "engage": e, "click": e / 2, "fit": 2,
                           "profiles_answered": 12} for k, (e, v) in scores.items()]}

    def write(self, rows):
        path = os.path.join(tempfile.mkdtemp(), "results.csv")
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["item_id", "impressions", "clicks", "conversions", "spend"])
            w.writeheader()
            w.writerows(rows)
        return path

    def test_spearman(self):
        self.assertEqual(panel_vs_results.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertEqual(panel_vs_results.spearman([1, 2, 3, 4], [40, 30, 20, 10]), -1.0)
        self.assertEqual(panel_vs_results.ranks([5, 5, 1]), [1.5, 1.5, 3.0])

    def test_agreeing_panel(self):
        scores = {"S%d" % i: (0.1 * i, "go" if i > 4 else "rework") for i in range(1, 9)}
        rows = [{"item_id": "S%d" % i, "impressions": 5000, "clicks": 20 * i, "conversions": i, "spend": 100}
                for i in range(1, 9)]
        res, dropped = panel_vs_results.load_results(self.write(rows), "ctr", 1000, 5)
        rep = panel_vs_results.compare(self.verdicts(scores), res, "ctr", "engage")
        t = rep["tracks"]["static"]
        self.assertEqual(t["spearman"], 1.0)
        self.assertEqual(t["pairwise_agreement"], 1.0)
        self.assertIn("keep it as a pre-filter", t["advice"])
        self.assertEqual(t["misses"], [])

    def test_misses_and_cpa_direction(self):
        scores = {"S1": (0.9, "go"), "S2": (0.5, "rework"), "S3": (0.2, "rework")}
        rows = [{"item_id": "S1", "impressions": 5000, "clicks": 100, "conversions": 5, "spend": 500},
                {"item_id": "S2", "impressions": 5000, "clicks": 100, "conversions": 10, "spend": 200},
                {"item_id": "S3", "impressions": 5000, "clicks": 100, "conversions": 10, "spend": 100}]
        res, _ = panel_vs_results.load_results(self.write(rows), "cpa", 1000, 5)
        self.assertEqual(res["S1"], 100.0)
        rep = panel_vs_results.compare(self.verdicts(scores), res, "cpa", "engage")
        t = rep["tracks"]["static"]
        self.assertEqual(t["spearman"], -1.0)
        notes = {m["item_id"]: m["panel"] for m in t["misses"]}
        self.assertEqual(notes, {"S1": "go", "S3": "rework"})
        self.assertIn("too few items", t["advice"])

    def test_sample_floor(self):
        rows = [{"item_id": "S1", "impressions": 200, "clicks": 5, "conversions": 0, "spend": 10}]
        res, dropped = panel_vs_results.load_results(self.write(rows), "ctr", 1000, 5)
        self.assertEqual(res, {})
        self.assertIn("under 1000", dropped[0][1])


if __name__ == "__main__":
    unittest.main()
