#!/usr/bin/env python3
"""Generate the MicroPython-safe configuration module from canonical JSON.

This script is a development-time tool. The ESP32 does not parse the JSON
files at runtime; `main.py` imports the generated `lib/generated_config.py`
module instead.

Usage:
    python tools/generate_config.py          # print generated content
    python tools/generate_config.py --write  # update lib/generated_config.py
    python tools/generate_config.py --check  # fail if generated file is stale
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "config" / "hardware.json"
RUNTIME_PATH = ROOT / "config" / "runtime.json"
OUTPUT_PATH = ROOT / "lib" / "generated_config.py"


def load_config() -> tuple[dict, dict]:
    with HARDWARE_PATH.open(encoding="utf-8") as handle:
        hardware = json.load(handle)
    with RUNTIME_PATH.open(encoding="utf-8") as handle:
        runtime = json.load(handle)
    return hardware, runtime


def build_constants(hardware: dict, runtime: dict) -> list[tuple[str, object]]:
    components = hardware["components"]
    buses = hardware["buses"]
    displays = components["displays"]

    blue_leds = components["blinking_leds"]
    oled0 = displays["oled0_cpu"]
    oled1 = displays["oled1_ram"]

    constants: list[tuple[str, object]] = []

    for index, led in enumerate(blue_leds, start=1):
        constants.append((f"BLUE_LED_{index}_PIN", led["gpio"]))

    constants.extend(
        [
            ("GREEN_LED_PIN", components["green_led"]["gpio"]),
            ("BUTTON_PIN", components["buttons"]["main"]["gpio"]),
            (
                "DECREASE_SPEED_BUTTON_PIN",
                components["buttons"]["decrease_interval"]["gpio"],
            ),
            (
                "INCREASE_SPEED_BUTTON_PIN",
                components["buttons"]["increase_interval"]["gpio"],
            ),
            ("BUS_IDLE_LED_PIN", components["status_leds"]["bus_idle"]["gpio"]),
            (
                "SCHEDULER_IDLE_LED_PIN",
                components["status_leds"]["scheduler_activity"]["gpio"],
            ),
            ("OLED0_I2C_BUS_ID", buses["oled0_i2c"]["micropython_bus_id"]),
            ("OLED0_SCL_PIN", buses["oled0_i2c"]["scl"]["gpio"]),
            ("OLED0_SDA_PIN", buses["oled0_i2c"]["sda"]["gpio"]),
            ("OLED1_I2C_BUS_ID", buses["oled1_i2c"]["micropython_bus_id"]),
            ("OLED1_SCL_PIN", buses["oled1_i2c"]["scl"]["gpio"]),
            ("OLED1_SDA_PIN", buses["oled1_i2c"]["sda"]["gpio"]),
            ("OLED_I2C_FREQUENCY_HZ", buses["oled0_i2c"]["frequency_hz"]),
            ("OLED_WIDTH", oled0["resolution"]["width_px"]),
            ("OLED_HEIGHT", oled0["resolution"]["height_px"]),
            ("OLED_I2C_ADDRESS", int(oled0["address_hex"], 16)),
            ("TFT_SPI_BUS_ID", buses["tft_spi"]["micropython_bus_id"]),
            ("TFT_SPI_BAUDRATE_HZ", buses["tft_spi"]["baudrate_hz"]),
            ("TFT_SCK_PIN", buses["tft_spi"]["sck"]["gpio"]),
            ("TFT_MOSI_PIN", buses["tft_spi"]["mosi"]["gpio"]),
            ("TFT_CS_PIN", buses["tft_spi"]["cs"]["gpio"]),
            ("TFT_DC_PIN", buses["tft_spi"]["dc"]["gpio"]),
            ("TFT_RST_PIN", buses["tft_spi"]["rst"]["gpio"]),
            ("FLASH_MODE_SWITCH_PIN", components["flash_mode_switch"]["gpio"]),
        ]
    )

    base_interval = runtime["blinking_leds"]["shared_base_interval_ms"]
    for index in range(1, len(blue_leds) + 1):
        constants.append((f"BLUE_LED_{index}_BLINK_INTERVAL_MS", base_interval))

    speed = runtime["blinking_leds"]["speed_control"]
    buttons = runtime["buttons"]
    graphs = runtime["resource_graphs"]
    serial = runtime["serial_status"]
    console = runtime["console"]
    colors = console["colors_rgb565"]

    constants.extend(
        [
            ("BLINK_SPEED_SCALE_BASE", speed["scale_base"]),
            ("BLINK_SPEED_INITIAL_STEP", speed["initial_step"]),
            ("BLINK_SPEED_STEP_MIN", speed["step_min"]),
            ("BLINK_SPEED_STEP_MAX", speed["step_max"]),
            ("BUTTON_SAMPLE_INTERVAL_MS", buttons["sample_interval_ms"]),
            ("BUTTON_DEBOUNCE_MS", buttons["debounce_ms"]),
            ("CPU_GRAPH_SAMPLE_INTERVAL_MS", graphs["cpu_sample_interval_ms"]),
            ("RAM_GRAPH_SAMPLE_INTERVAL_MS", graphs["ram_sample_interval_ms"]),
            ("PRINT_STATUS_INTERVAL_MS", serial["print_interval_ms"]),
            ("CONSOLE_LOG_THROTTLE", console["log_throttle"]),
            ("CONSOLE_BLUE", int(colors["blinking_leds_blue"], 16)),
            ("CONSOLE_ORANGE", int(colors["bus_activity_orange"], 16)),
            ("CONSOLE_YELLOW", int(colors["scheduler_activity_yellow"], 16)),
            ("CONSOLE_GREEN", int(colors["main_button_green"], 16)),
            ("CONSOLE_RED", int(colors["cpu_graph_red"], 16)),
            ("CONSOLE_PURPLE", int(colors["ram_graph_purple"], 16)),
            ("CONSOLE_WHITE", int(colors["default_white"], 16)),
            ("CONSOLE_BACKGROUND", int(colors["background_black"], 16)),
        ]
    )

    return constants


def python_literal(name: str, value: object) -> str:
    hex_names = {
        "OLED_I2C_ADDRESS",
        "CONSOLE_BLUE",
        "CONSOLE_ORANGE",
        "CONSOLE_YELLOW",
        "CONSOLE_GREEN",
        "CONSOLE_RED",
        "CONSOLE_PURPLE",
        "CONSOLE_WHITE",
        "CONSOLE_BACKGROUND",
    }
    if name in hex_names and isinstance(value, int):
        width = 2 if name == "OLED_I2C_ADDRESS" else 4
        return f"0x{value:0{width}X}"
    return repr(value)


def render_generated_config(hardware: dict | None = None, runtime: dict | None = None) -> str:
    if hardware is None or runtime is None:
        hardware, runtime = load_config()

    lines = [
        '"""Generated configuration for esp32-asyncio.',
        "",
        "DO NOT EDIT THIS FILE DIRECTLY.",
        "Sources:",
        "  - config/hardware.json",
        "  - config/runtime.json",
        "",
        "Regenerate with: python tools/generate_config.py --write",
        '"""',
        "",
        f'HARDWARE_SCHEMA_VERSION = {json.dumps(hardware["schema_version"])}',
        f'RUNTIME_SCHEMA_VERSION = {json.dumps(runtime["schema_version"])}',
        "",
    ]

    for name, value in build_constants(hardware, runtime):
        lines.append(f"{name} = {python_literal(name, value)}")

    lines.extend(
        [
            "",
            "BLUE_LED_PINS = (",
            "    BLUE_LED_1_PIN,",
            "    BLUE_LED_2_PIN,",
            "    BLUE_LED_3_PIN,",
            "    BLUE_LED_4_PIN,",
            "    BLUE_LED_5_PIN,",
            "    BLUE_LED_6_PIN,",
            ")",
            "",
            "BASE_BLINK_INTERVALS_MS = (",
            "    BLUE_LED_1_BLINK_INTERVAL_MS,",
            "    BLUE_LED_2_BLINK_INTERVAL_MS,",
            "    BLUE_LED_3_BLINK_INTERVAL_MS,",
            "    BLUE_LED_4_BLINK_INTERVAL_MS,",
            "    BLUE_LED_5_BLINK_INTERVAL_MS,",
            "    BLUE_LED_6_BLINK_INTERVAL_MS,",
            ")",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="write generated file")
    group.add_argument("--check", action="store_true", help="check generated file")
    args = parser.parse_args()

    expected = render_generated_config()

    if args.write:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(expected, encoding="utf-8")
        print(f"Updated {OUTPUT_PATH.relative_to(ROOT)}")
        return 0

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"Missing generated file: {OUTPUT_PATH.relative_to(ROOT)}")
            return 1
        actual = OUTPUT_PATH.read_text(encoding="utf-8")
        if actual != expected:
            print(
                f"Generated file is stale: {OUTPUT_PATH.relative_to(ROOT)}\n"
                "Run: python tools/generate_config.py --write"
            )
            return 1
        print("Generated configuration is up to date.")
        return 0

    print(expected, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
