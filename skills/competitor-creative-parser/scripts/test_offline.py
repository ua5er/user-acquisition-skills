#!/usr/bin/env python3
"""Offline tests for competitor-creative-parser. No network, no key.

Run: python3 test_offline.py
"""
import csv
import json
import os
import shutil
import sys
import tempfile
import unittest
from urllib import error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("TYPESAFE_API_KEY", None)

import market_snapshot  # noqa: E402
import tag_creatives as tc  # noqa: E402


def forbid_network(*args, **kwargs):
    raise AssertionError("network call attempted in an offline test")


tc.request.urlopen = forbid_network
SAMPLE = os.path.join(HERE, "sample_market")
T = {"tag": 0.70, "review_low": 0.35}


def qset(track):
    return tc.load_question_set(os.path.join(HERE, "questions_%s.py" % track))


class QuestionSetTests(unittest.TestCase):
    def test_both_sets_valid(self):
        for track in ("static", "video"):
            qs = qset(track)
            self.assertEqual(qs["TRACK"], track)
            for qid, q in qs["QUESTIONS"].items():
                if q["type"] == "choice":
                    self.assertEqual(list(q["criteria"])[-1], "other")
                    self.assertIn(qid, qs["CHOICE_COMPANION"])
                self.assertNotIn(" or not ", q["instructions"].lower())

    def test_choice_without_other_rejected(self):
        ns = {"QUESTIONS": {"a": {"type": "choice", "instructions": "x", "criteria": {"p": "1", "q": "2"}},
                            "a_fits": {"type": "noul", "instructions": "y"}},
              "CHOICE_COMPANION": {"a": "a_fits"}, "FLAGS": [], "SCORES": []}
        with self.assertRaises(ValueError):
            tc.validate_question_set(ns)

    def test_state_has_no_advertiser_or_id(self):
        descs = tc.load_jsonl(os.path.join(SAMPLE, "descriptions.jsonl"))
        for d in descs:
            qs = qset(d["format"])
            text = json.dumps(qs["build_state"](d))
            self.assertNotIn(d["creative_id"], text)
            self.assertNotIn("described_by", text)

    def test_code_features(self):
        qs = qset("video")
        f = qs["code_features"]({"duration_s": 20, "cut_times_s": [5, 10, 15, 25]})
        self.assertEqual(f["cuts"], 3)
        self.assertEqual(f["cuts_per_10s"], 1.5)
        self.assertEqual(f["avg_shot_s"], 5.0)
        s = qset("static")["code_features"]({"headline": "7 days free, then $59.99 per year", "text_blocks": []})
        self.assertTrue(s["has_price"])


class RotationTests(unittest.TestCase):
    def test_other_stays_last_and_options_kept(self):
        qs = qset("static")
        for cid in ("s01", "s02", "x9"):
            rq, offsets = tc.rotated_questions(qs["QUESTIONS"], cid)
            for qid, q in rq.items():
                if q["type"] == "choice":
                    self.assertEqual(list(q["criteria"])[-1], "other")
                    self.assertEqual(set(q["criteria"]), set(qs["QUESTIONS"][qid]["criteria"]))
        a, _ = tc.rotated_questions(qs["QUESTIONS"], "s01")
        b, _ = tc.rotated_questions(qs["QUESTIONS"], "s01")
        self.assertEqual(json.dumps(a), json.dumps(b))

    def test_reverse(self):
        q = {"c": {"type": "choice", "instructions": "x", "criteria": {"a": "1", "b": "2", "other": "3"}}}
        rq, off = tc.rotated_questions(q, "id", reverse=True)
        self.assertEqual(list(rq["c"]["criteria"]), ["b", "a", "other"])
        self.assertEqual(off["c"], "reversed")


class DecisionTests(unittest.TestCase):
    def choice(self, top, p):
        return {"choice": top, "probabilities": {top: p, "z": 1 - p}}

    def test_choice_rules(self):
        self.assertEqual(tc.decide_choice(self.choice("a", 0.9), 0.9, T)[:2], ("tagged", "a"))
        self.assertEqual(tc.decide_choice(self.choice("a", 0.6), 0.9, T)[0], "review")
        self.assertEqual(tc.decide_choice(self.choice("a", 0.9), 0.5, T)[0], "review")
        self.assertEqual(tc.decide_choice(self.choice("a", 0.9), 0.2, T)[0], "review")  # conflict
        self.assertEqual(tc.decide_choice(self.choice("a", 0.3), 0.9, T)[0], "untagged")
        self.assertEqual(tc.decide_choice(self.choice("other", 0.8), 0.1, T)[:2], ("tagged", "other"))

    def test_flag_rules(self):
        self.assertEqual(tc.decide_flag(0.70, T), "yes")
        self.assertEqual(tc.decide_flag(0.35, T), "no")
        self.assertEqual(tc.decide_flag(0.5, T), "review")


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.descs = tc.load_jsonl(os.path.join(SAMPLE, "descriptions.jsonl"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_dry_run_both_tracks_and_snapshot(self):
        for track in ("static", "video"):
            items = [d for d in self.descs if d["format"] == track]
            self.assertGreaterEqual(len(items), 10)
            recs, queue, summary, order = tc.run(items, qset(track), tc.mock_post, source="mock", order_check=2,
                                                 log=lambda *a: None)
            self.assertEqual(summary["errors"], 0)
            self.assertEqual(summary["tagged_ok"], len(items))
            self.assertEqual(summary["requests"], len(items) + 2)
            tc.write_outputs(self.tmp, track, recs, queue, summary, order)
        snap = market_snapshot.build(tc.load_jsonl(os.path.join(SAMPLE, "creatives.jsonl")),
                                     [os.path.join(self.tmp, "tags-%s.jsonl" % t) for t in ("static", "video")],
                                     "test", 20, "2026-11-15")
        for track in ("static", "video"):
            t = snap["tracks"][track]
            self.assertTrue(t["low_sample"])
            self.assertEqual(t["durability"]["longest"], [])
            for d in t["dimensions"].values():
                tagged = sum(r["creatives"] for r in d["rows"])
                self.assertEqual(tagged + d["unresolved"], t["n"])
        self.assertIn("Low sample", market_snapshot.render_md(snap))
        with open(os.path.join(self.tmp, "review-queue-static.csv"), encoding="utf-8") as fh:
            self.assertEqual(csv.DictReader(fh).fieldnames, tc.QUEUE_COLUMNS)

    def test_errors_never_become_tags(self):
        def bad_post(url, key, body, timeout=60):
            return 400, {"detail": "bad request"}, {}
        items = [d for d in self.descs if d["format"] == "static"][:2]
        recs, queue, summary, _ = tc.run(items, qset("static"), bad_post, source="live", log=lambda *a: None)
        self.assertEqual(summary["errors"], 2)
        for r in recs:
            self.assertEqual(r["status"], "error")
            self.assertEqual(r["tags"], {})
        self.assertTrue(all(q["kind"] == "error" for q in queue))

    def test_wrong_shape_is_error(self):
        def odd_post(url, key, body, timeout=60):
            return 200, {"answers": {}}, {}
        items = [d for d in self.descs if d["format"] == "video"][:1]
        recs, _, summary, _ = tc.run(items, qset("video"), odd_post, source="live", log=lambda *a: None)
        self.assertEqual(recs[0]["status"], "error")

    def test_spend_guard(self):
        items = [d for d in self.descs if d["format"] == "static"]
        _, _, summary, _ = tc.run(items, qset("static"), tc.mock_post, max_usd=0.00015, source="mock",
                                  log=lambda *a: None)
        self.assertGreater(summary["skipped_by_guard"], 0)
        self.assertLess(summary["creatives"], len(items))

    def test_retry_then_success(self):
        calls = []

        def flaky(url, key, body, timeout=60):
            calls.append(1)
            if len(calls) == 1:
                return 529, {"detail": "overloaded"}, {"Retry-After": "0"}
            if len(calls) == 2:
                raise error.URLError("down")
            return 200, tc.mock_response(body), {}
        body = {"model": "jev-1.14.0", "state": {"a": "b"},
                "questions": {"q": {"type": "noul", "instructions": "x"}}}
        out = tc.call_with_retry(flaky, "https://x", "k", body, sleep=lambda s: None)
        self.assertIn("answers", out)
        self.assertEqual(len(calls), 3)

    def test_cli_refuses_live_without_confirmation(self):
        os.environ["TYPESAFE_API_KEY"] = "test-not-a-key"
        try:
            rc = tc.main([os.path.join(SAMPLE, "descriptions.jsonl"), "--track", "static", "--out-dir", self.tmp])
        finally:
            os.environ.pop("TYPESAFE_API_KEY", None)
        self.assertEqual(rc, 2)

    def test_cli_dry_run(self):
        rc = tc.main([os.path.join(SAMPLE, "descriptions.jsonl"), "--track", "video", "--dry-run",
                      "--out-dir", self.tmp, "--max-items", "3"])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "tags-video.jsonl")))


class SampleMarketTests(unittest.TestCase):
    def test_sample_is_labelled_fictional(self):
        for name in ("creatives.jsonl", "descriptions.jsonl"):
            for row in tc.load_jsonl(os.path.join(SAMPLE, name)):
                self.assertIn("FICTIONAL", row["note"])

    def test_live_run_files_parse(self):
        live = os.path.join(SAMPLE, "live-run-2026-11-15")
        if not os.path.isdir(live):
            self.skipTest("no saved live run")
        with open(os.path.join(live, "snapshot.json"), encoding="utf-8") as fh:
            snap = json.load(fh)
        self.assertEqual(set(snap["tracks"]), {"static", "video"})
        self.assertEqual(snap["tracks"]["static"]["sources"], ["live"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
