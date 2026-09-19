"""Host-side automated tests for canonical configuration generation."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import generate_config  # noqa: E402


class GeneratedConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hardware = json.loads(
            (ROOT / "config" / "hardware.json").read_text(encoding="utf-8")
        )
        self.runtime = json.loads(
            (ROOT / "config" / "runtime.json").read_text(encoding="utf-8")
        )

    def test_committed_generated_module_is_exact(self) -> None:
        expected = generate_config.render_generated_config(
            self.hardware, self.runtime
        )
        actual = (ROOT / "lib" / "generated_config.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(actual, expected)

    def test_generated_constant_names_are_unique(self) -> None:
        constants = generate_config.build_constants(
            self.hardware, self.runtime
        )
        names = [name for name, _ in constants]
        self.assertEqual(len(names), len(set(names)))

    def test_blink_speed_policy_is_coherent(self) -> None:
        speed = self.runtime["blinking_leds"]["speed_control"]
        self.assertGreater(speed["scale_base"], 1)
        self.assertLessEqual(speed["step_min"], speed["initial_step"])
        self.assertLessEqual(speed["initial_step"], speed["step_max"])

    def test_six_blinking_leds_are_declared(self) -> None:
        leds = self.hardware["components"]["blinking_leds"]
        self.assertEqual(len(leds), 6)
        self.assertEqual(
            [led["id"] for led in leds],
            [f"blue-led-{index}" for index in range(1, 7)],
        )


if __name__ == "__main__":
    unittest.main()
