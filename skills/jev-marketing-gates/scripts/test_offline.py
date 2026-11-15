#!/usr/bin/env python3
"""Offline unit tests. No network, no key. Run: python3 test_offline.py

Mock responses are shaped like the examples in docs.typesafe.ai/api/system-one.md
as read on 2026-11-15. They do not prove the live API behaves the same way.
"""
import csv
import io
import json
import os
import sys
import unittest
from urllib import error

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.pop("TYPESAFE_API_KEY", None)

import calibrate  # noqa: E402
import run_batch  # noqa: E402


def forbid_network(*args, **kwargs):
    raise AssertionError("network call attempted in an offline test")


run_batch.request.urlopen = forbid_network

QUESTIONS = {
    "billing": {"type": "noul", "instructions": "Is this message about billing?"},
    "tone": {"type": "choice", "instructions": "What is the tone?",
             "criteria": {"angry": "a", "calm": "b", "excited": "c"}},
    "urgency": {"type": "score", "instructions": "How urgent?",
                "criteria": ["Can wait", "Needs attention this week", "Needs attention today"]},
}

DOC_RESPONSE = {
    "model": "jev-1.14.0",
    "answers": {
        "billing": {"type": "noul", "noul": 0.98},
        "tone": {"type": "choice", "choice": "calm", "confidence": 0.7,
                 "probabilities": {"angry": 0.15, "calm": 0.8, "excited": 0.05}},
        "urgency": {"type": "score", "score": 1.7, "confidence": 0.55,
                    "legend": {"0": "Can wait", "1": "Needs attention this week", "2": "Needs attention today"},
                    "probabilities": {"0": 0.1, "1": 0.1, "2": 0.8}},
    },
    "usage": {"input_tokens": 120, "output_tokens": 12},
}


class FakeModule:
    MODEL = "jev-1.14.0"
    QUESTIONS = QUESTIONS
    STATE_FIELDS = ["text"]
    build_state = None

    @staticmethod
    def route(answers):
        p = answers["billing"]["value"]
        if p >= 0.7:
            return "act", "billing high"
        if p > 0.3:
            return "review", "band"
        return "pass", "low"


class RequestTests(unittest.TestCase):
    def test_request_shape(self):
        body = run_batch.build_request("jev-1.14.0", {"a": "x"}, QUESTIONS)
        self.assertEqual(set(body), {"model", "state", "questions"})
        self.assertEqual(body["questions"]["urgency"]["criteria"][0], "Can wait")
        json.dumps(body)

    def test_state_uses_only_listed_fields(self):
        item = {"_id": "1", "text": "hello", "label": "secret label"}
        self.assertEqual(run_batch.build_state(FakeModule, item), {"text": "hello"})

    def test_validate_questions(self):
        run_batch.validate_questions(QUESTIONS)
        with self.assertRaises(ValueError):
            run_batch.validate_questions({"q": {"type": "box"}})
        with self.assertRaises(ValueError):
            run_batch.validate_questions({"q": {"type": "choice", "criteria": {}}})
        with self.assertRaises(ValueError):
            run_batch.validate_questions({"q": {"type": "score", "criteria": ["one"]}})
        with self.assertRaises(ValueError):
            run_batch.validate_questions({"q": {"type": "noul", "criteria": {"maybe": "x"}}})

    def test_chunking(self):
        self.assertEqual(len(run_batch.chunk_questions(QUESTIONS, 0)), 1)
        self.assertEqual(len(run_batch.chunk_questions(QUESTIONS, 2)), 2)


class ParseTests(unittest.TestCase):
    def test_documented_response(self):
        norm, usage, model = run_batch.parse_response(DOC_RESPONSE, QUESTIONS)
        self.assertAlmostEqual(norm["billing"]["value"], 0.98)
        self.assertIsNone(norm["billing"]["confidence"])
        self.assertEqual(norm["tone"]["value"], "calm")
        self.assertAlmostEqual(norm["urgency"]["value"], 1.7)
        self.assertEqual(usage["input_tokens"], 120)
        self.assertEqual(model, "jev-1.14.0")

    def test_bad_shapes(self):
        bad = json.loads(json.dumps(DOC_RESPONSE))
        bad["answers"]["billing"]["noul"] = 1.4
        with self.assertRaises(run_batch.ResponseShapeError):
            run_batch.parse_response(bad, QUESTIONS)
        bad = json.loads(json.dumps(DOC_RESPONSE))
        del bad["answers"]["tone"]
        with self.assertRaises(run_batch.ResponseShapeError):
            run_batch.parse_response(bad, QUESTIONS)
        bad = json.loads(json.dumps(DOC_RESPONSE))
        bad["answers"]["tone"]["choice"] = "sad"
        with self.assertRaises(run_batch.ResponseShapeError):
            run_batch.parse_response(bad, QUESTIONS)
        with self.assertRaises(run_batch.ResponseShapeError):
            run_batch.parse_response({"detail": "x"}, QUESTIONS)

    def test_mock_matches_documented_shape(self):
        body = run_batch.build_request("jev-1.14.0", {"a": "x"}, QUESTIONS)
        first = run_batch.mock_response(body)
        self.assertEqual(first, run_batch.mock_response(body))  # deterministic
        norm, usage, _ = run_batch.parse_response(first, QUESTIONS)
        self.assertAlmostEqual(sum(norm["tone"]["probs"].values()), 1.0)
        self.assertEqual(set(norm["urgency"]["probs"]), {"0", "1", "2"})
        self.assertGreater(usage["input_tokens"], 0)


class RetryTests(unittest.TestCase):
    def test_retries_429_then_succeeds_and_honours_retry_after(self):
        calls, waits = [], []

        def post(url, key, body, timeout):
            calls.append(url)
            if len(calls) < 3:
                return 429, {"detail": "slow down"}, {"Retry-After": "7"}
            return 200, DOC_RESPONSE, {}

        out = run_batch.call_with_retry(post, "https://x/v1/systemone", "k", {}, retries=4,
                                        sleep=waits.append, rng=lambda: 0.0)
        self.assertEqual(out, DOC_RESPONSE)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(w >= 7 for w in waits))

    def test_no_retry_on_401(self):
        calls = []

        def post(url, key, body, timeout):
            calls.append(1)
            return 401, {"detail": "bad key"}, {}

        with self.assertRaises(run_batch.ApiError) as ctx:
            run_batch.call_with_retry(post, "u", "SECRETKEY", {}, sleep=lambda s: None)
        self.assertEqual(len(calls), 1)
        self.assertNotIn("SECRETKEY", str(ctx.exception))

    def test_network_error_retried_then_gives_up(self):
        def post(url, key, body, timeout):
            raise error.URLError("down")

        with self.assertRaises(run_batch.ApiError):
            run_batch.call_with_retry(post, "u", "k", {}, retries=2, sleep=lambda s: None)


class RunTests(unittest.TestCase):
    def run_items(self, items, post, **kw):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=run_batch.LOG_COLUMNS)
        writer.writeheader()
        summary = run_batch.run_items(items, FakeModule, post, writer, sleep=lambda s: None,
                                      log=lambda *a: None, **kw)
        return summary, list(csv.DictReader(io.StringIO(buf.getvalue())))

    def test_log_and_routing(self):
        def post(url, key, body, timeout):
            return 200, DOC_RESPONSE, {}

        summary, rows = self.run_items([{"_id": "a", "text": "t"}], post)
        self.assertEqual(len(rows), 3)
        self.assertEqual({r["routed_outcome"] for r in rows}, {"act"})
        self.assertEqual(rows[0]["input_tokens"], "120")
        self.assertEqual(rows[1]["input_tokens"], "")
        self.assertEqual(rows[0]["human_outcome"], "")
        self.assertEqual(rows[1]["confidence"], "0.7000")
        self.assertEqual(summary["input_tokens"], 120)
        self.assertAlmostEqual(summary["estimated_usd"], 120 * 0.042 / 1e6)

    def test_api_failure_is_an_error_never_a_pass(self):
        def post(url, key, body, timeout):
            return 401, {"detail": "bad key"}, {}

        summary, rows = self.run_items([{"_id": "a", "text": "t"}], post)
        self.assertEqual({r["routed_outcome"] for r in rows}, {"error"})
        self.assertEqual({r["answer"] for r in rows}, {"ERROR"})
        self.assertEqual(summary["errors"], 1)

    def test_broken_router_is_an_error(self):
        class Broken(FakeModule):
            @staticmethod
            def route(answers):
                raise RuntimeError("boom")

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=run_batch.LOG_COLUMNS)
        writer.writeheader()
        s = run_batch.run_items([{"_id": "a", "text": "t"}], Broken, lambda *a: (200, DOC_RESPONSE, {}), writer,
                                log=lambda *a: None)
        self.assertEqual(s["outcomes"], {"error": 1})

    def test_spend_guard_stops_before_overspend(self):
        calls = []

        def post(url, key, body, timeout):
            calls.append(1)
            return 200, DOC_RESPONSE, {}

        items = [{"_id": str(i), "text": "t"} for i in range(5)]
        summary, rows = self.run_items(items, post, max_usd=0.0)
        self.assertEqual(calls, [])
        self.assertEqual(summary["skipped_by_guard"], 5)
        self.assertEqual(rows, [])

    def test_dry_run_end_to_end(self):
        items = run_batch.load_items(os.path.join(HERE, "sample_items.csv"))
        mod = run_batch.load_questions_module(os.path.join(HERE, "questions_example.py"))
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=run_batch.LOG_COLUMNS)
        writer.writeheader()
        s = run_batch.run_items(items, mod, run_batch.mock_post, writer, source="mock", log=lambda *a: None)
        self.assertEqual(s["errors"], 0)
        self.assertEqual(s["items"], len(items))
        rows = list(csv.DictReader(io.StringIO(buf.getvalue())))
        self.assertEqual({r["source"] for r in rows}, {"mock"})

    def test_live_run_refused_without_key_or_data_decision(self):
        argv = [os.path.join(HERE, "sample_items.csv"), "--questions", os.path.join(HERE, "questions_example.py"),
                "--out", os.devnull]
        self.assertEqual(run_batch.main(argv), 2)  # no key in the environment
        os.environ["TYPESAFE_API_KEY"] = "test-value"
        try:
            self.assertEqual(run_batch.main(argv), 2)  # key but no data handling decision
        finally:
            os.environ.pop("TYPESAFE_API_KEY", None)

    def test_http_base_url_refused(self):
        argv = [os.path.join(HERE, "sample_items.csv"), "--questions", os.path.join(HERE, "questions_example.py"),
                "--dry-run", "--base-url", "http://example.test"]
        self.assertEqual(run_batch.main(argv), 2)


class CalibrationTests(unittest.TestCase):
    def make_log(self, noul_pairs):
        rows = []
        for i, (p, _) in enumerate(noul_pairs):
            rows.append({"item_id": str(i), "question_id": "billing", "question_type": "noul",
                         "answer": "yes" if p >= 0.5 else "no",
                         "probabilities": json.dumps({"yes": p, "no": 1 - p}), "confidence": "",
                         "routed_outcome": "review" if 0.3 < p < 0.7 else "pass", "route_reason": "",
                         "human_outcome": "", "model": "m", "source": "live",
                         "input_tokens": "100"})
        return rows

    def test_noul_report(self):
        pairs = [(0.95, True)] * 8 + [(0.9, False)] + [(0.05, False)] * 8 + [(0.1, True)] + [(0.5, True)] * 2
        log = self.make_log(pairs)
        labels = [{"item_id": str(i), "question_id": "billing", "label": "yes" if y else "no"}
                  for i, (_, y) in enumerate(pairs)]
        q = {"billing": QUESTIONS["billing"]}
        report = calibrate.build_report(log, labels, q, lambda a: ("pass", ""), {"billing": {"low": 0.3, "high": 0.7}},
                                        0.9, 0.042, {})
        self.assertIn("Confusion at 0.5: true yes 10, false yes 1, false no 1, true no 8.", report)
        self.assertIn("in the review band: 2 of 20 (10%)", report)
        self.assertIn("yes at or above 0.50", report)  # 10 of 11 yes labels at p >= 0.5 is about 91%
        self.assertIn("Input tokens in the log: 2000", report)
        self.assertIn("Sample is small", report)

    def test_choice_and_score_reports_and_first_option_check(self):
        questions = {"tone": QUESTIONS["tone"], "urgency": QUESTIONS["urgency"]}
        log, labels = [], []
        for i in range(12):
            lab = "angry" if i % 2 else "calm"
            log.append({"item_id": str(i), "question_id": "tone", "question_type": "choice", "answer": "angry",
                        "probabilities": json.dumps({"angry": 0.8, "calm": 0.15, "excited": 0.05}),
                        "confidence": "0.7", "routed_outcome": "pass", "route_reason": "", "human_outcome": "",
                        "model": "m", "source": "live", "input_tokens": ""})
            log.append({"item_id": str(i), "question_id": "urgency", "question_type": "score", "answer": "1.7000",
                        "probabilities": json.dumps({"0": 0.1, "1": 0.1, "2": 0.8}), "confidence": "0.55",
                        "routed_outcome": "pass", "route_reason": "", "human_outcome": "", "model": "m",
                        "source": "live", "input_tokens": ""})
            labels.append({"item_id": str(i), "question_id": "tone", "label": lab})
            labels.append({"item_id": str(i), "question_id": "urgency", "label": "2" if i % 3 else "1"})
        report = calibrate.build_report(log, labels, questions, lambda a: ("pass", ""), {}, 0.9, 0.042,
                                        {"tone": ["angry", "calm", "excited"]})
        self.assertIn("Top option accuracy: 6 of 12 (50%).", report)
        self.assertIn("First option check", report)
        self.assertIn("prediction in 100%", report)
        self.assertIn("Most likely level equals the label: 8 of 12", report)

    def test_routing_share_uses_current_route_and_skips_errors(self):
        pairs = [(0.5, True)] * 4
        log = self.make_log(pairs)
        log.append({"item_id": "x", "question_id": "billing", "question_type": "noul", "answer": "ERROR",
                    "probabilities": "", "confidence": "", "routed_outcome": "error", "route_reason": "",
                    "human_outcome": "", "model": "m", "source": "live", "input_tokens": ""})
        q = {"billing": QUESTIONS["billing"]}
        report = calibrate.build_report(log, [], q, lambda a: ("review", ""), {}, 0.9, 0.042, {})
        self.assertIn("Share sent to review: 100%", report)
        self.assertIn("Items with an API error, not routed: 1.", report)

    def test_label_parser(self):
        self.assertTrue(calibrate.parse_yes("True"))
        self.assertFalse(calibrate.parse_yes("0"))
        with self.assertRaises(ValueError):
            calibrate.parse_yes("maybe")


if __name__ == "__main__":
    unittest.main(verbosity=1)
