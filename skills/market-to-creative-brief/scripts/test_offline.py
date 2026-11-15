#!/usr/bin/env python3
"""Offline tests for brief_pack.py. No network, no key.

  python3 test_offline.py
"""
import copy
import csv
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brief_pack  # noqa: E402


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


class SampleTest(unittest.TestCase):
    def setUp(self):
        self.dec = load("sample_decisions.json")
        self.snap = load("sample_snapshot.json")

    def run_check(self, dec=None):
        return brief_pack.check(dec or self.dec, self.snap)

    def test_sample_is_clean(self):
        errors, warnings, blocking, plan = self.run_check()
        self.assertEqual(errors, [])
        self.assertEqual(blocking, [])
        self.assertEqual(plan["creatives"], 15)
        self.assertEqual(plan["kill_reads"], 30)
        self.assertFalse(plan["over"])
        self.assertEqual(len(warnings), 2)  # one low-sample line per track

    def test_wrong_number_is_an_error(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][0]["evidence"][1]["expected"] = 9
        errors = self.run_check(dec)[0]
        self.assertTrue(any("says 9, snapshot has 8" in e for e in errors), errors)

    def test_share_tolerance(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][1]["evidence"][0]["expected"] = 0.67
        self.assertEqual(self.run_check(dec)[0], [])
        dec["decisions"][1]["evidence"][0]["expected"] = 0.70
        self.assertTrue(self.run_check(dec)[0])

    def test_gap_must_be_a_gap(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][0]["value"] = "outcome_promise"
        errors = self.run_check(dec)[0]
        self.assertTrue(any("it is not a gap" in e for e in errors), errors)

    def test_out_execute_needs_crowded(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][1]["value"] = "question"
        errors = self.run_check(dec)[0]
        self.assertTrue(any("not marked crowded" in e for e in errors), errors)

    def test_unknown_ad_id(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][0]["refs"].append("s99")
        dec["static_briefs"][0]["references"].append({"id": "v77", "take": "x"})
        errors = self.run_check(dec)[0]
        self.assertTrue(any("s99" in e for e in errors))
        self.assertTrue(any("v77" in e for e in errors))

    def test_own_performance_never_invented(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][0]["cites_own_performance"] = True
        errors = self.run_check(dec)[0]
        self.assertTrue(any("own performance" in e for e in errors))
        dec["constraints"]["own_performance"] = {"file": "own.csv"}
        self.assertEqual(self.run_check(dec)[0], [])

    def test_no_evidence(self):
        dec = copy.deepcopy(self.dec)
        dec["decisions"][2]["evidence"] = []
        self.assertTrue(any("no evidence" in e for e in self.run_check(dec)[0]))

    def test_missing_brief_field_blocks(self):
        dec = copy.deepcopy(self.dec)
        dec["static_briefs"][0]["acceptance"] = []
        del dec["motion_briefs"][0]["end_card"]
        blocking = self.run_check(dec)[2]
        self.assertTrue(any("S1: missing acceptance" in b for b in blocking))
        self.assertTrue(any("M1: missing end_card" in b for b in blocking))

    def test_three_hooks(self):
        dec = copy.deepcopy(self.dec)
        dec["motion_briefs"][0]["hooks"] = dec["motion_briefs"][0]["hooks"][:2]
        self.assertTrue(any("three hook variants" in b for b in self.run_check(dec)[2]))

    def test_budget_warning(self):
        dec = copy.deepcopy(self.dec)
        dec["constraints"]["test_budget"]["amount"] = 300
        warnings, plan = self.run_check(dec)[1], self.run_check(dec)[3]
        self.assertEqual(plan["kill_reads"], 6)
        self.assertTrue(any("15 creatives planned" in w for w in warnings))

    def test_no_budget(self):
        plan = brief_pack.budget_check(self.dec, {})
        self.assertIsNone(plan["kill_reads"])
        self.assertFalse(plan["over"])


class BeatTest(unittest.TestCase):
    def brief(self, ts, durations=(15,)):
        return {"beats": [{"t": t} for t in ts], "durations_s": list(durations)}

    def test_good(self):
        self.assertEqual(brief_pack.check_beats(self.brief(["0-3", "3-8", "8-15"])), [])

    def test_gap_between_beats(self):
        errs = brief_pack.check_beats(self.brief(["0-3", "4-8", "8-15"]))
        self.assertTrue(any("starts at 4.0" in e for e in errs))

    def test_late_hook(self):
        errs = brief_pack.check_beats(self.brief(["0-4", "4-15"]))
        self.assertTrue(any("must end by 3 s" in e for e in errs))

    def test_not_starting_at_zero(self):
        errs = brief_pack.check_beats(self.brief(["1-3", "3-15"]))
        self.assertTrue(errs)

    def test_too_long(self):
        errs = brief_pack.check_beats(self.brief(["0-3", "3-20"], durations=(15,)))
        self.assertTrue(any("longer than the longest duration" in e for e in errs))

    def test_bad_format(self):
        self.assertTrue(brief_pack.check_beats(self.brief(["start", "3-15"])))


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.dec_path = os.path.join(HERE, "sample_decisions.json")
        self.snap_path = os.path.join(HERE, "sample_snapshot.json")

    def test_main_writes_all_outputs(self):
        out = os.path.join(self.tmp, "pack.md")
        gates = os.path.join(self.tmp, "gates.csv")
        concepts = os.path.join(self.tmp, "concepts.jsonl")
        rc = brief_pack.main(["--decisions", self.dec_path, "--snapshot", self.snap_path, "--out", out,
                              "--gates-csv", gates, "--panel-concepts", concepts])
        self.assertEqual(rc, 0)
        text = open(out, encoding="utf-8").read()
        for needle in ("## Decisions", "## Static brief S1", "## Motion brief M3", "Hook, seconds 0 to 3",
                       "## Hand-off: test plan for meta-creative-testing", "BRANDZ | MKT01 | Video | M1 hook A"):
            self.assertIn(needle, text)
        self.assertNotIn("Not ready", text)
        self.assertNotIn("\u2014", text)
        self.assertNotIn("\u2013", text)
        with open(gates, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 3 + 9)  # one per static brief, one per motion hook
        self.assertEqual(rows[0]["id"], "S1")
        lines = [json.loads(x) for x in open(concepts, encoding="utf-8")]
        self.assertEqual([c["concept_id"] for c in lines], ["S1", "S2", "S3", "M1", "M2", "M3"])
        self.assertEqual(len(lines[3]["hooks"]), 3)
        self.assertEqual(lines[0]["track"], "static")

    def test_panel_verdicts(self):
        panel = {"notice": "signal only", "items": [{"item_id": "S1", "verdict": "go"}, {"item_id": "S2", "verdict": "drop"},
                                                    {"item_id": "M1-B", "verdict": "rework"}],
                 "concepts": [{"concept_id": "S2", "track": "static", "verdict": "drop", "best_item": "S2",
                               "items": {"S2": "drop"}, "reasons": ["holds few profiles"]}]}
        vpath = os.path.join(self.tmp, "verdicts.json")
        with open(vpath, "w", encoding="utf-8") as fh:
            json.dump(panel, fh)
        out = os.path.join(self.tmp, "pack-panel.md")
        rc = brief_pack.main(["--decisions", self.dec_path, "--snapshot", self.snap_path, "--out", out,
                              "--panel-verdicts", vpath])
        self.assertEqual(rc, 0)
        text = open(out, encoding="utf-8").read()
        self.assertIn("## Pre-flight panel", text)
        self.assertIn("Held back by the pre-flight panel", text)
        self.assertIn("`BRANDZ | MKT01 | Static | S2 v1 | src: market s07` (drop)", text)
        self.assertIn("M1 hook B | src: market v06+v12` (panel: rework before production)", text)

    def test_errors_stop_rendering(self):
        dec = load("sample_decisions.json")
        dec["decisions"][0]["evidence"][0]["expected"] = 5
        bad = os.path.join(self.tmp, "bad.json")
        with open(bad, "w", encoding="utf-8") as fh:
            json.dump(dec, fh)
        out = os.path.join(self.tmp, "bad.md")
        self.assertEqual(brief_pack.main(["--decisions", bad, "--snapshot", self.snap_path, "--out", out]), 1)
        self.assertFalse(os.path.exists(out))
        self.assertEqual(brief_pack.main(["--decisions", bad, "--snapshot", self.snap_path, "--out", out,
                                          "--allow-errors"]), 1)
        self.assertIn("## Not ready", open(out, encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
