"""Host-side automated source-contract tests.

These tests inspect CPython-parseable source without importing MicroPython-only
modules such as machine, framebuf or uasyncio/asyncio firmware internals.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MainSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (ROOT / "main.py").read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_main_imports_generated_configuration(self) -> None:
        imports = [
            node
            for node in ast.walk(self.tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "lib.generated_config"
        ]
        self.assertEqual(len(imports), 1)
        imported = {alias.name for alias in imports[0].names}
        for required in {
            "BUTTON_PIN",
            "OLED0_I2C_BUS_ID",
            "OLED1_I2C_BUS_ID",
            "TFT_SPI_BUS_ID",
            "BLINK_SPEED_SCALE_BASE",
            "BUTTON_DEBOUNCE_MS",
        }:
            self.assertIn(required, imported)

    def test_no_blocking_time_sleep_calls_in_main(self) -> None:
        offenders = []
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "time"
                and func.attr in {"sleep", "sleep_ms", "sleep_us"}
            ):
                offenders.append((func.attr, node.lineno))
        self.assertEqual(offenders, [])

    def test_root_display_driver_import_contract(self) -> None:
        imported_modules = {
            node.module
            for node in ast.walk(self.tree)
            if isinstance(node, ast.ImportFrom)
        }
        self.assertIn("ssd1306", imported_modules)
        self.assertIn("ili9341", imported_modules)

    def test_main_has_async_entrypoint(self) -> None:
        async_functions = {
            node.name
            for node in self.tree.body
            if isinstance(node, ast.AsyncFunctionDef)
        }
        self.assertIn("main", async_functions)


if __name__ == "__main__":
    unittest.main()
