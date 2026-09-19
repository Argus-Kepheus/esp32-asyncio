#!/usr/bin/env python3
"""Validate canonical configuration against derived and operational artifacts.

Wave 2 deliberately performs static consistency checks only. It does not
claim that a passing result proves correct behavior in Wokwi or on hardware.

Usage:
    python tools/validate_repository.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from generate_config import (
    HARDWARE_PATH,
    OUTPUT_PATH,
    ROOT,
    RUNTIME_PATH,
    build_constants,
    render_generated_config,
)

MAIN_PATH = ROOT / "main.py"
DIAGRAM_PATH = ROOT / "diagram.json"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        fail(f"Cannot parse {path.relative_to(ROOT)}: {exc}")
        return {}


def check_generated_file(hardware: dict, runtime: dict) -> None:
    expected = render_generated_config(hardware, runtime)
    if not OUTPUT_PATH.exists():
        fail(f"Missing generated file: {OUTPUT_PATH.relative_to(ROOT)}")
        return

    actual = OUTPUT_PATH.read_text(encoding="utf-8")
    if actual != expected:
        fail(
            f"{OUTPUT_PATH.relative_to(ROOT)} is stale; run "
            "python tools/generate_config.py --write"
        )


def normalize_resistance(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None

    text = value.strip().lower().replace("ohm", "").replace("Ω", "")
    try:
        if text.endswith("k"):
            return int(float(text[:-1]) * 1000)
        return int(float(text))
    except ValueError:
        return None


def collect_expected_part_types(hardware: dict) -> dict[str, str]:
    components = hardware["components"]
    expected: dict[str, str] = {
        hardware["board"]["id"]: hardware["board"]["wokwi_type"],
        components["green_led"]["id"]: components["green_led"]["wokwi_type"],
        components["green_led"]["resistor_id"]: "wokwi-resistor",
        components["status_leds"]["bus_idle"]["id"]:
            components["status_leds"]["bus_idle"]["wokwi_type"],
        components["status_leds"]["bus_idle"]["resistor_id"]: "wokwi-resistor",
        components["status_leds"]["scheduler_activity"]["id"]:
            components["status_leds"]["scheduler_activity"]["wokwi_type"],
        components["status_leds"]["scheduler_activity"]["resistor_id"]:
            "wokwi-resistor",
        components["flash_mode_switch"]["id"]:
            components["flash_mode_switch"]["wokwi_type"],
    }

    for led in components["blinking_leds"]:
        expected[led["id"]] = led["wokwi_type"]
        expected[led["resistor_id"]] = "wokwi-resistor"

    for button in components["buttons"].values():
        expected[button["id"]] = button["wokwi_type"]
        pull = button["pull"]
        if pull["type"] == "external":
            expected[pull["resistor_id"]] = "wokwi-resistor"

    for display in components["displays"].values():
        expected[display["id"]] = display["wokwi_type"]

    return expected


def collect_gpio_roles(hardware: dict) -> dict[int, list[str]]:
    components = hardware["components"]
    buses = hardware["buses"]
    roles: dict[int, list[str]] = {}

    def add(gpio: int, role: str) -> None:
        roles.setdefault(gpio, []).append(role)

    for led in components["blinking_leds"]:
        add(led["gpio"], led["id"])

    add(components["green_led"]["gpio"], components["green_led"]["id"])

    for name, led in components["status_leds"].items():
        add(led["gpio"], f"status_led:{name}")

    for name, button in components["buttons"].items():
        add(button["gpio"], f"button:{name}")

    for bus_name in ("oled0_i2c", "oled1_i2c"):
        bus = buses[bus_name]
        add(bus["scl"]["gpio"], f"{bus_name}:scl")
        add(bus["sda"]["gpio"], f"{bus_name}:sda")

    spi = buses["tft_spi"]
    for signal in ("sck", "mosi", "cs", "dc", "rst"):
        add(spi[signal]["gpio"], f"tft_spi:{signal}")

    add(
        components["flash_mode_switch"]["gpio"],
        components["flash_mode_switch"]["id"],
    )
    return roles


def check_hardware_internal_consistency(hardware: dict) -> None:
    if hardware.get("schema_version") != "1.0":
        fail("Unsupported config/hardware.json schema_version")

    expected_parts = collect_expected_part_types(hardware)

    components = hardware["components"]
    canonical_ids = [
        hardware["board"]["id"],
        components["green_led"]["id"],
        components["green_led"]["resistor_id"],
        components["status_leds"]["bus_idle"]["id"],
        components["status_leds"]["bus_idle"]["resistor_id"],
        components["status_leds"]["scheduler_activity"]["id"],
        components["status_leds"]["scheduler_activity"]["resistor_id"],
        components["flash_mode_switch"]["id"],
    ]
    for led in components["blinking_leds"]:
        canonical_ids.extend([led["id"], led["resistor_id"]])
    for button in components["buttons"].values():
        canonical_ids.append(button["id"])
        pull = button["pull"]
        if pull["type"] == "external":
            canonical_ids.append(pull["resistor_id"])
    for display in components["displays"].values():
        canonical_ids.append(display["id"])

    duplicate_ids = sorted(
        {item for item in canonical_ids if canonical_ids.count(item) > 1}
    )
    if duplicate_ids:
        fail(f"Duplicate canonical component IDs detected: {duplicate_ids}")

    roles = collect_gpio_roles(hardware)
    duplicates = {gpio: names for gpio, names in roles.items() if len(names) > 1}
    if duplicates:
        for gpio, names in sorted(duplicates.items()):
            fail(f"GPIO {gpio} has conflicting canonical roles: {', '.join(names)}")

    constraints = hardware["gpio_constraints"]["input_only"]
    input_only = set(constraints["esp32_silicon"])

    components = hardware["components"]
    buses = hardware["buses"]
    output_gpios = {
        *(led["gpio"] for led in components["blinking_leds"]),
        components["green_led"]["gpio"],
        components["status_leds"]["bus_idle"]["gpio"],
        components["status_leds"]["scheduler_activity"]["gpio"],
        buses["oled0_i2c"]["scl"]["gpio"],
        buses["oled0_i2c"]["sda"]["gpio"],
        buses["oled1_i2c"]["scl"]["gpio"],
        buses["oled1_i2c"]["sda"]["gpio"],
        buses["tft_spi"]["sck"]["gpio"],
        buses["tft_spi"]["mosi"]["gpio"],
        buses["tft_spi"]["cs"]["gpio"],
        buses["tft_spi"]["dc"]["gpio"],
        buses["tft_spi"]["rst"]["gpio"],
    }

    invalid_outputs = sorted(output_gpios & input_only)
    if invalid_outputs:
        fail(f"Output/bus signals use input-only GPIOs: {invalid_outputs}")

    used_input_only = {
        button["gpio"]
        for button in components["buttons"].values()
        if button["gpio"] in input_only
    }
    declared = set(constraints["used_by_project"])
    if used_input_only != declared:
        fail(
            "gpio_constraints.input_only.used_by_project is out of sync: "
            f"declared={sorted(declared)}, actual={sorted(used_input_only)}"
        )

    oled0_bus = buses["oled0_i2c"]
    oled1_bus = buses["oled1_i2c"]
    if oled0_bus["frequency_hz"] != oled1_bus["frequency_hz"]:
        fail(
            "Current generated_config.py assumes one OLED I2C frequency, "
            "but canonical buses differ"
        )

    displays = components["displays"]
    oled0 = displays["oled0_cpu"]
    oled1 = displays["oled1_ram"]
    if oled0["resolution"] != oled1["resolution"]:
        fail(
            "Current generated_config.py assumes equal OLED dimensions, "
            "but canonical displays differ"
        )
    if oled0["address_hex"].lower() != oled1["address_hex"].lower():
        fail(
            "Current generated_config.py assumes one OLED address, "
            "but canonical displays differ"
        )


def parse_main_numeric_constants(text: str) -> dict[str, int]:
    constants: dict[str, int] = {}
    pattern = re.compile(
        r"^([A-Z][A-Z0-9_]*)\s*=\s*"
        r"(0x[0-9A-Fa-f]+|-?\d[\d_]*)\s*(?:#.*)?$",
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        raw = match.group(2).replace("_", "")
        constants[match.group(1)] = int(raw, 0)
    return constants


def check_main_sync(hardware: dict, runtime: dict) -> None:
    text = MAIN_PATH.read_text(encoding="utf-8")
    actual = parse_main_numeric_constants(text)
    expected = dict(build_constants(hardware, runtime))

    required = [
        *(f"BLUE_LED_{index}_PIN" for index in range(1, 7)),
        "GREEN_LED_PIN",
        "BUTTON_PIN",
        "DECREASE_SPEED_BUTTON_PIN",
        "INCREASE_SPEED_BUTTON_PIN",
        "BUS_IDLE_LED_PIN",
        "SCHEDULER_IDLE_LED_PIN",
        "OLED0_SCL_PIN",
        "OLED0_SDA_PIN",
        "OLED1_SCL_PIN",
        "OLED1_SDA_PIN",
        "OLED_I2C_FREQUENCY_HZ",
        "OLED_WIDTH",
        "OLED_HEIGHT",
        "OLED_I2C_ADDRESS",
        "TFT_SCK_PIN",
        "TFT_MOSI_PIN",
        "TFT_CS_PIN",
        "TFT_DC_PIN",
        "TFT_RST_PIN",
        *(f"BLUE_LED_{index}_BLINK_INTERVAL_MS" for index in range(1, 7)),
        "BLINK_SPEED_STEP_MIN",
        "BLINK_SPEED_STEP_MAX",
        "BUTTON_SAMPLE_INTERVAL_MS",
        "BUTTON_DEBOUNCE_MS",
        "CPU_GRAPH_SAMPLE_INTERVAL_MS",
        "RAM_GRAPH_SAMPLE_INTERVAL_MS",
        "PRINT_STATUS_INTERVAL_MS",
        "CONSOLE_LOG_THROTTLE",
        "CONSOLE_BLUE",
        "CONSOLE_ORANGE",
        "CONSOLE_YELLOW",
        "CONSOLE_GREEN",
        "CONSOLE_RED",
        "CONSOLE_PURPLE",
        "CONSOLE_WHITE",
        "CONSOLE_BACKGROUND",
    ]

    for name in required:
        if name not in actual:
            fail(f"main.py is missing expected transitional constant: {name}")
            continue
        if actual[name] != expected[name]:
            fail(
                f"main.py drift for {name}: canonical={expected[name]!r}, "
                f"main.py={actual[name]!r}"
            )

    def extract_call(pattern: str, label: str) -> tuple[int, ...] | None:
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            fail(f"Could not locate {label} construction in main.py")
            return None
        return tuple(int(group.replace("_", ""), 0) for group in match.groups())

    oled0 = extract_call(
        r"oled0_i2c\s*=\s*I2C\(\s*(\d+)",
        "OLED0 I2C",
    )
    oled1 = extract_call(
        r"oled1_i2c\s*=\s*I2C\(\s*(\d+)",
        "OLED1 I2C",
    )
    spi = extract_call(
        r"tft_spi\s*=\s*SPI\(\s*(\d+)\s*,\s*"
        r"baudrate\s*=\s*(\d[\d_]*)",
        "TFT SPI",
    )

    if oled0 and oled0[0] != expected["OLED0_I2C_BUS_ID"]:
        fail(
            "main.py OLED0 bus id differs from canonical hardware: "
            f"{oled0[0]} != {expected['OLED0_I2C_BUS_ID']}"
        )
    if oled1 and oled1[0] != expected["OLED1_I2C_BUS_ID"]:
        fail(
            "main.py OLED1 bus id differs from canonical hardware: "
            f"{oled1[0]} != {expected['OLED1_I2C_BUS_ID']}"
        )
    if spi:
        if spi[0] != expected["TFT_SPI_BUS_ID"]:
            fail(
                "main.py TFT SPI bus id differs from canonical hardware: "
                f"{spi[0]} != {expected['TFT_SPI_BUS_ID']}"
            )
        if spi[1] != expected["TFT_SPI_BAUDRATE_HZ"]:
            fail(
                "main.py TFT SPI baudrate differs from canonical hardware: "
                f"{spi[1]} != {expected['TFT_SPI_BAUDRATE_HZ']}"
            )


class NetGraph:
    def __init__(self, connections: list[list[object]]) -> None:
        self.parent: dict[str, str] = {}

        # ESP32 ground header pins are electrically common even though Wokwi
        # represents them with distinct endpoint names.
        self.union("esp32:GND.1", "esp32:GND.2")

        for connection in connections:
            if len(connection) >= 2:
                self.union(str(connection[0]), str(connection[1]))

    def find(self, item: str) -> str:
        self.parent.setdefault(item, item)
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root

    def connected(self, left: str, right: str) -> bool:
        return self.find(left) == self.find(right)


def check_diagram_sync(hardware: dict) -> None:
    diagram = load_json(DIAGRAM_PATH)
    if not diagram:
        return

    parts = {part["id"]: part for part in diagram.get("parts", [])}
    expected_parts = collect_expected_part_types(hardware)

    for part_id, expected_type in expected_parts.items():
        part = parts.get(part_id)
        if part is None:
            fail(f"diagram.json missing canonical component: {part_id}")
            continue
        if part.get("type") != expected_type:
            fail(
                f"diagram.json type drift for {part_id}: "
                f"canonical={expected_type}, diagram={part.get('type')}"
            )

    components = hardware["components"]
    board = hardware["board"]
    buses = hardware["buses"]

    board_part = parts.get(board["id"])
    if board_part and board_part.get("type") != board["wokwi_type"]:
        fail("diagram.json board type differs from canonical board")

    for led in components["blinking_leds"]:
        part = parts.get(led["id"], {})
        if part.get("attrs", {}).get("color", "").lower() != led["color"].lower():
            fail(f"diagram.json LED color drift for {led['id']}")
        resistor = parts.get(led["resistor_id"], {})
        actual_r = normalize_resistance(resistor.get("attrs", {}).get("value"))
        if actual_r != led["resistor_ohm"]:
            fail(f"diagram.json resistor value drift for {led['resistor_id']}")

    for led in [
        components["green_led"],
        components["status_leds"]["bus_idle"],
        components["status_leds"]["scheduler_activity"],
    ]:
        part = parts.get(led["id"], {})
        if str(part.get("attrs", {}).get("color", "")).lower() != str(led["color"]).lower():
            fail(f"diagram.json LED color drift for {led['id']}")
        resistor = parts.get(led["resistor_id"], {})
        actual_r = normalize_resistance(resistor.get("attrs", {}).get("value"))
        if actual_r != led["resistor_ohm"]:
            fail(f"diagram.json resistor value drift for {led['resistor_id']}")

    key_map = {"space": " "}
    for button in components["buttons"].values():
        part = parts.get(button["id"], {})
        expected_key = key_map.get(button["wokwi_key"], button["wokwi_key"])
        actual_key = part.get("attrs", {}).get("key")
        if actual_key != expected_key:
            fail(
                f"diagram.json key binding drift for {button['id']}: "
                f"canonical={button['wokwi_key']!r}, diagram={actual_key!r}"
            )
        pull = button["pull"]
        if pull["type"] == "external":
            resistor = parts.get(pull["resistor_id"], {})
            actual_r = normalize_resistance(resistor.get("attrs", {}).get("value"))
            if actual_r != pull["resistance_ohm"]:
                fail(
                    f"diagram.json pull-down value drift for {pull['resistor_id']}"
                )
            if "naming_note" in pull:
                warn(
                    f"{button['id']}: pull-down component ID is historically "
                    "cross-named in diagram.json; connectivity is validated."
                )

    for display in (
        components["displays"]["oled0_cpu"],
        components["displays"]["oled1_ram"],
    ):
        part = parts.get(display["id"], {})
        actual_address = str(part.get("attrs", {}).get("i2cAddress", "")).lower()
        if actual_address != display["address_hex"].lower():
            fail(f"diagram.json I2C address drift for {display['id']}")

    graph = NetGraph(diagram.get("connections", []))

    def require_net(left: str, right: str, label: str) -> None:
        if not graph.connected(left, right):
            fail(f"diagram.json connectivity drift: {label} ({left} !~ {right})")

    def require_resistor_between(
        resistor_id: str, endpoint_a: str, endpoint_b: str, label: str
    ) -> None:
        r1 = f"{resistor_id}:1"
        r2 = f"{resistor_id}:2"
        normal = graph.connected(r1, endpoint_a) and graph.connected(r2, endpoint_b)
        reversed_ = graph.connected(r2, endpoint_a) and graph.connected(r1, endpoint_b)
        if not (normal or reversed_):
            fail(f"diagram.json resistor connectivity drift: {label}")

    ground = "esp32:GND.1"

    for led in components["blinking_leds"]:
        require_resistor_between(
            led["resistor_id"],
            f"esp32:{led['gpio']}",
            f"{led['id']}:A",
            led["id"],
        )
        require_net(f"{led['id']}:C", ground, f"{led['id']} cathode to GND")

    for led in [
        components["green_led"],
        components["status_leds"]["bus_idle"],
        components["status_leds"]["scheduler_activity"],
    ]:
        require_resistor_between(
            led["resistor_id"],
            f"esp32:{led['gpio']}",
            f"{led['id']}:A",
            led["id"],
        )
        require_net(f"{led['id']}:C", ground, f"{led['id']} cathode to GND")

    for button in components["buttons"].values():
        require_net(
            f"{button['id']}:2.l",
            f"esp32:{button['gpio']}",
            f"{button['id']} signal",
        )
        require_net(
            f"{button['id']}:1.l",
            "esp32:3V3",
            f"{button['id']} supply",
        )
        pull = button["pull"]
        if pull["type"] == "external":
            require_resistor_between(
                pull["resistor_id"],
                f"esp32:{button['gpio']}",
                ground,
                f"{button['id']} pull-down",
            )

    oled0 = components["displays"]["oled0_cpu"]
    require_net(
        f"{oled0['id']}:SCL",
        f"esp32:{buses['oled0_i2c']['scl']['gpio']}",
        "OLED0 SCL",
    )
    require_net(
        f"{oled0['id']}:SDA",
        f"esp32:{buses['oled0_i2c']['sda']['gpio']}",
        "OLED0 SDA",
    )
    require_net(f"{oled0['id']}:VCC", "esp32:3V3", "OLED0 supply")
    require_net(f"{oled0['id']}:GND", ground, "OLED0 ground")

    oled1 = components["displays"]["oled1_ram"]
    require_net(
        f"{oled1['id']}:SCL",
        f"esp32:{buses['oled1_i2c']['scl']['gpio']}",
        "OLED1 SCL",
    )
    require_net(
        f"{oled1['id']}:SDA",
        f"esp32:{buses['oled1_i2c']['sda']['gpio']}",
        "OLED1 SDA",
    )
    require_net(f"{oled1['id']}:VCC", "esp32:3V3", "OLED1 supply")
    require_net(f"{oled1['id']}:GND", ground, "OLED1 ground")

    tft = components["displays"]["tft_log"]
    spi = buses["tft_spi"]
    for signal, pin_name in [
        ("sck", "SCK"),
        ("mosi", "MOSI"),
        ("cs", "CS"),
        ("dc", "D/C"),
        ("rst", "RST"),
    ]:
        require_net(
            f"{tft['id']}:{pin_name}",
            f"esp32:{spi[signal]['gpio']}",
            f"TFT {signal.upper()}",
        )
    require_net(f"{tft['id']}:VCC", "esp32:5V", "TFT supply")
    require_net(f"{tft['id']}:GND", ground, "TFT ground")

    switch = components["flash_mode_switch"]
    require_net(
        f"{switch['id']}:2",
        f"esp32:{switch['gpio']}",
        "flash-mode switch GPIO",
    )
    require_net(f"{switch['id']}:1", ground, "flash-mode switch ground")


def check_runtime_schema(runtime: dict) -> None:
    if runtime.get("schema_version") != "1.0":
        fail("Unsupported config/runtime.json schema_version")

    speed = runtime.get("blinking_leds", {}).get("speed_control", {})
    if speed.get("step_min", 0) > speed.get("step_max", 0):
        fail("runtime blink speed step_min is greater than step_max")

    for label, value in [
        ("base blink interval", runtime.get("blinking_leds", {}).get("shared_base_interval_ms")),
        ("button sample interval", runtime.get("buttons", {}).get("sample_interval_ms")),
        ("button debounce", runtime.get("buttons", {}).get("debounce_ms")),
        ("CPU graph interval", runtime.get("resource_graphs", {}).get("cpu_sample_interval_ms")),
        ("RAM graph interval", runtime.get("resource_graphs", {}).get("ram_sample_interval_ms")),
        ("serial status interval", runtime.get("serial_status", {}).get("print_interval_ms")),
    ]:
        if not isinstance(value, int) or value <= 0:
            fail(f"Invalid positive integer for {label}: {value!r}")


def main() -> int:
    for required in (
        HARDWARE_PATH,
        RUNTIME_PATH,
        MAIN_PATH,
        DIAGRAM_PATH,
        ROOT / "tools" / "generate_config.py",
        OUTPUT_PATH,
    ):
        if not required.exists():
            fail(f"Missing required Wave 2 file: {required.relative_to(ROOT)}")

    hardware = load_json(HARDWARE_PATH)
    runtime = load_json(RUNTIME_PATH)

    if hardware:
        check_hardware_internal_consistency(hardware)
    if runtime:
        check_runtime_schema(runtime)
    if hardware and runtime:
        check_generated_file(hardware, runtime)
        check_main_sync(hardware, runtime)
        check_diagram_sync(hardware)

    print("esp32-asyncio repository validation")
    print(f"Errors: {len(errors)}")
    for item in errors:
        print(f"  ERROR: {item}")

    print(f"Warnings: {len(warnings)}")
    for item in warnings:
        print(f"  WARN: {item}")

    if errors:
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
