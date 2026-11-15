#!/usr/bin/env python3
"""Offline tests. No key and no network required."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

import audience_panel as panel


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.spec = panel.default_cohort()

    def test_selftest_cli(self):
        env = dict(os.environ)
        env.pop("TYPESAFE_API_KEY", None)
        result = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("audience_panel.py")), "selftest"],
            env=env, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Offline selftest passed.", result.stdout)

    def test_grid_and_descriptions(self):
        cells = panel.grid(self.spec)
        self.assertEqual(len(cells), 1044)
        self.assertEqual(len({panel.sentence(p, self.spec) for p in cells}), 1044)
        controls = [p for p in cells if panel.is_control(p, self.spec)]
        self.assertEqual(len(controls), 36)
        self.assertTrue(all("stage" not in p and "urgency" not in p for p in controls))
        self.assertTrue(all("moment" in p and "attention" not in p for p in cells))

    def test_seed_and_size(self):
        a = panel.build_people(self.spec)
        self.assertEqual(a, panel.build_people(self.spec))
        self.spec["seed"] += 1
        self.assertNotEqual(a, panel.build_people(self.spec))
        self.spec["size"] = 1044
        self.assertEqual(len(panel.build_people(self.spec)), 1044)
        self.spec["size"] = 1045
        with self.assertRaises(ValueError):
            panel.build_people(self.spec)

    def test_rotation(self):
        keys = list(panel.BARRIERS)
        seen = set()
        for index in range(len(keys) - 1):
            rotated = list(panel.rotate(panel.BARRIERS, index))
            self.assertEqual(rotated[-1], keys[-1])
            self.assertEqual(set(rotated), set(keys))
            seen.add(rotated[0])
        self.assertEqual(seen, set(keys[:-1]))

    def test_chunk_coverage(self):
        people = panel.build_people(self.spec)
        for size in (125, 60):
            parts = list(panel.chunks(people, size))
            flat = [p["id"] for part in parts for p in part]
            self.assertEqual(flat, [p["id"] for p in people])
            self.assertEqual(len(set(flat)), len(people))
            self.assertTrue(all(0 < len(part) <= size for part in parts))
        asked = [p for p in people if not panel.is_control(p, self.spec)][::4]
        flat = [p for part in panel.chunks(asked, 60) for p in part]
        self.assertEqual(flat, asked)

    def test_malformed_inputs(self):
        with self.assertRaises(ValueError):
            panel.probabilities({"0": .2, "1": .2}, ["0", "1"])
        with self.assertRaises(ValueError):
            panel.probabilities({"0": float("nan"), "1": 1}, ["0", "1"])
        with self.assertRaises(ValueError):
            panel.validate_ads([{"id": "A", "text": "a"}, {"id": "A", "text": "b"}])
        bad = self.spec["mixes"]["cold"]
        bad["fit"]["core"] = -1
        with self.assertRaises(ValueError):
            panel.validate_mix(bad, self.spec)

    def test_custom_cohort(self):
        spec = {
            "factors": {
                "fit": {"core": "needs help with this task", "outside": "has no need for this task"},
                "moment": {"rushed": "has little time", "browsing": "has time to explore"},
            },
            "control": {"factor": "fit", "option": "outside"},
            "target_only": [],
            "mixes": {"cold": {
                "fit": {"core": .5, "outside": .5},
                "moment": {"rushed": .5, "browsing": .5},
            }},
            "size": 4,
            "seed": 7,
        }
        people = panel.build_people(spec)
        w, marginals = panel.weights(people, spec, spec["mixes"]["cold"])
        self.assertAlmostEqual(sum(w), 1)
        self.assertEqual(marginals, spec["mixes"]["cold"])

    def test_zero_weight_control_is_explicit(self):
        people = panel.build_people(self.spec)
        mix = self.spec["mixes"]["cold"]
        mix["fit"] = {"core": .5, "adjacent": .5, "outside": 0}
        weights, _ = panel.weights(people, self.spec, mix)
        self.assertTrue(all(w == 0 for p, w in zip(people, weights)
                            if panel.is_control(p, self.spec)))


if __name__ == "__main__":
    unittest.main()
