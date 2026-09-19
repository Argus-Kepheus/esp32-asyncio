#!/usr/bin/env python3
"""Generate/validate documentation blocks from canonical configuration.

Wave 4 keeps narrative prose hand-maintained, while repetitive technical tables
are derived from config/hardware.json (and, where needed, config/runtime.json).

Usage:
    python tools/generate_docs.py --write
    python tools/generate_docs.py --check
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "config" / "hardware.json"
RUNTIME_PATH = ROOT / "config" / "runtime.json"

TARGET_LANGUAGES = ("EN", "PT")

LABELS = {
    "EN": {
        "component": "Component",
        "wokwi_id": "Wokwi identifier",
        "esp32_pin": "ESP32 pin",
        "board": "Board",
        "blinking_leds": "Six blinking LEDs",
        "green_led": "Green LED",
        "main_button": "Main push-button",
        "speed_buttons": "Two speed buttons",
        "status_leds": "Two status-indicator LEDs",
        "cpu_oled": "CPU OLED0",
        "ram_oled": "RAM OLED1",
        "tft": "TFT log display",
        "property": "Property",
        "definition": "Project definition",
        "manufacturer": "Manufacturer",
        "board_name": "Board name",
        "header_layout": "Header arrangement",
        "mcu_family": "Microcontroller family",
        "physical_module": "Recommended physical module",
        "firmware": "Firmware",
        "logic_voltage": "Logic voltage",
        "function": "Function",
        "python_name": "Python variable/constant",
        "gpio": "GPIO",
        "header_pin": "Header pin",
        "restriction": "Restriction",
        "pins": "Pins",
        "why": "Why",
        "input_only": "Input-only",
        "bootstrapping": "Bootstrapping",
        "primary_uart": "Primary UART",
        "reserved_flash": "Reserved for SPI flash",
        "input_only_why": "Cannot drive outputs; no internal pull-up/pull-down",
        "boot_why": "Sampled at boot; project uses are documented and validated",
        "uart_why": "Used for programming/diagnostic serial; not a project peripheral",
        "flash_why": "Internal flash communication; do not use as project GPIO",
        "flash_switch": "Flash-mode slide switch",
        "supply": "OLED / push-button supply",
        "blue_led_output": "Blinking LED {n} output",
        "green_led_output": "Green LED output",
        "main_button_input": "Push-button input",
        "decrease_button": "Decrease-speed button",
        "increase_button": "Increase-speed button",
        "bus_idle": "Bus-idle LED (orange)",
        "scheduler_idle": "Scheduler-idle LED (yellow)",
        "oled_clock": "{name}, I2C clock",
        "oled_data": "{name}, I2C data",
        "tft_clock": "TFT SPI clock",
        "tft_data": "TFT SPI data out",
        "tft_cs": "TFT chip select",
        "tft_dc": "TFT data/command",
        "tft_rst": "TFT hardware reset",
        "parameter": "Runtime parameter",
        "value": "Configured value",
        "blink_base": "Blinking-LED base interval",
        "speed_steps": "Blink speed step range",
        "button_sample": "Button sample interval",
        "debounce": "Debounce stable window",
        "cpu_sample": "CPU graph sample floor",
        "ram_sample": "RAM graph sample floor",
        "serial_interval": "Serial status interval",
        "console_throttle": "Console log throttle",
    },
    "PT": {
        "component": "Componente",
        "wokwi_id": "Identificador no Wokwi",
        "esp32_pin": "Pino no ESP32",
        "board": "Placa",
        "blinking_leds": "Seis LEDs piscantes",
        "green_led": "LED verde",
        "main_button": "Botão pulsador principal",
        "speed_buttons": "Dois botões de velocidade",
        "status_leds": "Dois LEDs indicadores de estado",
        "cpu_oled": "OLED0 de CPU",
        "ram_oled": "OLED1 de RAM",
        "tft": "TFT de registro",
        "property": "Propriedade",
        "definition": "Definição do projeto",
        "manufacturer": "Fabricante",
        "board_name": "Nome da placa",
        "header_layout": "Disposição dos conectores",
        "mcu_family": "Família do microcontrolador",
        "physical_module": "Módulo físico recomendado",
        "firmware": "Firmware",
        "logic_voltage": "Tensão lógica",
        "function": "Função",
        "python_name": "Variável/constante em Python",
        "gpio": "GPIO",
        "header_pin": "Terminal do conector",
        "restriction": "Restrição",
        "pins": "Terminais",
        "why": "Motivo",
        "input_only": "Somente entrada",
        "bootstrapping": "Configuração de inicialização",
        "primary_uart": "UART principal",
        "reserved_flash": "Reservados para a memória flash SPI",
        "input_only_why": "Não podem acionar saídas e não possuem pull-up/pull-down interno",
        "boot_why": "Amostrados no boot; os usos do projeto são documentados e validados",
        "uart_why": "Usados para programação/serial de diagnóstico; não são periféricos do projeto",
        "flash_why": "Comunicação interna com a flash; não usar como GPIO do projeto",
        "flash_switch": "Chave deslizante de modo de gravação",
        "supply": "Alimentação dos OLEDs e dos botões",
        "blue_led_output": "Saída do LED piscante {n}",
        "green_led_output": "Saída do LED verde",
        "main_button_input": "Entrada do botão principal",
        "decrease_button": "Botão de diminuir intervalo",
        "increase_button": "Botão de aumentar intervalo",
        "bus_idle": "LED de barramento ocioso (laranja)",
        "scheduler_idle": "LED de escalonador ocioso (amarelo)",
        "oled_clock": "Relógio I2C do {name}",
        "oled_data": "Dados I2C do {name}",
        "tft_clock": "Relógio SPI da TFT",
        "tft_data": "Dados de saída SPI da TFT",
        "tft_cs": "Seleção de chip da TFT",
        "tft_dc": "Dado/comando da TFT",
        "tft_rst": "Reset físico da TFT",
        "parameter": "Parâmetro de execução",
        "value": "Valor configurado",
        "blink_base": "Intervalo-base dos LEDs piscantes",
        "speed_steps": "Faixa de passos da velocidade",
        "button_sample": "Intervalo de amostragem dos botões",
        "debounce": "Janela estável de antirrepique",
        "cpu_sample": "Piso de amostragem do gráfico de CPU",
        "ram_sample": "Piso de amostragem do gráfico de RAM",
        "serial_interval": "Intervalo do status serial",
        "console_throttle": "Throttling do registro no console",
    },
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def generated_region(name: str, body: str) -> str:
    return (
        f"<!-- BEGIN GENERATED: {name} -->\n"
        f"{body.rstrip()}\n"
        f"<!-- END GENERATED: {name} -->"
    )


def overview_table(hardware: dict, language: str) -> str:
    l = LABELS[language]
    c = hardware["components"]
    buses = hardware["buses"]
    blue = c["blinking_leds"]

    rows = [
        (f"{l['board']} — {hardware['board']['board_name']}", hardware["board"]["wokwi_type"], "—"),
        (
            f"{l['blinking_leds']} (+ {blue[0]['resistor_ohm']} Ω)",
            f"`{blue[0]['id']}` … `{blue[-1]['id']}`",
            "GPIO " + ", ".join(str(x["gpio"]) for x in blue),
        ),
        (
            f"{l['green_led']} (+ {c['green_led']['resistor_ohm']} Ω)",
            f"`{c['green_led']['id']}`",
            f"GPIO {c['green_led']['gpio']}",
        ),
        (
            l["main_button"],
            f"`{c['buttons']['main']['id']}`",
            f"GPIO {c['buttons']['main']['gpio']}",
        ),
        (
            (
                f"{l['speed_buttons']} (+ external {c['buttons']['decrease_interval']['pull']['resistance_ohm']} Ω pull-down each)"
                if language == "EN"
                else f"{l['speed_buttons']} (+ pull-down externo de {c['buttons']['decrease_interval']['pull']['resistance_ohm']} Ω cada)"
            ),
            f"`{c['buttons']['decrease_interval']['id']}`, `{c['buttons']['increase_interval']['id']}`",
            f"GPIO {c['buttons']['decrease_interval']['gpio']}, {c['buttons']['increase_interval']['gpio']}",
        ),
        (
            (
                f"{l['status_leds']} (+ {c['status_leds']['bus_idle']['resistor_ohm']} Ω each)"
                if language == "EN"
                else f"{l['status_leds']} (+ {c['status_leds']['bus_idle']['resistor_ohm']} Ω cada)"
            ),
            f"`{c['status_leds']['bus_idle']['id']}`, `{c['status_leds']['scheduler_activity']['id']}`",
            f"GPIO {c['status_leds']['bus_idle']['gpio']}, {c['status_leds']['scheduler_activity']['gpio']}",
        ),
        (
            f"{l['cpu_oled']}, SSD1306 {c['displays']['oled0_cpu']['resolution']['width_px']}×{c['displays']['oled0_cpu']['resolution']['height_px']}, I2C({buses['oled0_i2c']['micropython_bus_id']}) @ {c['displays']['oled0_cpu']['address_hex']}",
            f"`{c['displays']['oled0_cpu']['id']}`",
            f"SCL = GPIO {buses['oled0_i2c']['scl']['gpio']}, SDA = GPIO {buses['oled0_i2c']['sda']['gpio']}",
        ),
        (
            f"{l['ram_oled']}, SSD1306 {c['displays']['oled1_ram']['resolution']['width_px']}×{c['displays']['oled1_ram']['resolution']['height_px']}, I2C({buses['oled1_i2c']['micropython_bus_id']}) @ {c['displays']['oled1_ram']['address_hex']}",
            f"`{c['displays']['oled1_ram']['id']}`",
            f"SCL = GPIO {buses['oled1_i2c']['scl']['gpio']}, SDA = GPIO {buses['oled1_i2c']['sda']['gpio']}",
        ),
        (
            f"{l['tft']}, ILI9341 {c['displays']['tft_log']['resolution']['width_px']}×{c['displays']['tft_log']['resolution']['height_px']}, SPI",
            f"`{c['displays']['tft_log']['id']}`",
            "SCK {sck}, MOSI {mosi}, CS {cs}, D/C {dc}, RST {rst}".format(
                sck=buses["tft_spi"]["sck"]["gpio"],
                mosi=buses["tft_spi"]["mosi"]["gpio"],
                cs=buses["tft_spi"]["cs"]["gpio"],
                dc=buses["tft_spi"]["dc"]["gpio"],
                rst=buses["tft_spi"]["rst"]["gpio"],
            ),
        ),
    ]

    lines = [
        f"| {l['component']} | {l['wokwi_id']} | {l['esp32_pin']} |",
        "|---|---|---:|",
    ]
    lines.extend(f"| {a} | {b} | {c_} |" for a, b, c_ in rows)
    return "\n".join(lines)


def board_summary_table(hardware: dict, language: str) -> str:
    l = LABELS[language]
    b = hardware["board"]
    rows = [
        (l["manufacturer"], b["manufacturer"]),
        (l["board_name"], b["board_name"]),
        (l["wokwi_id"], f"`{b['wokwi_type']}` (`diagram.json` id `{b['id']}`)"),
        (
            l["header_layout"],
            f"{b['header_layout']['total_pins']} pins, {b['header_layout']['pins_per_side']} per side ({', '.join(b['header_layout']['headers'])})"
            if language == "EN"
            else f"{b['header_layout']['total_pins']} terminais, {b['header_layout']['pins_per_side']} em cada lado ({', '.join(b['header_layout']['headers'])})",
        ),
        (l["mcu_family"], b["microcontroller_family"]),
        (l["physical_module"], b["recommended_physical_module"]),
        (l["firmware"], b["firmware_family"]),
        (
            l["logic_voltage"],
            f"{b['logic_voltage_v']} V (not 5 V tolerant)"
            if language == "EN"
            else f"{str(b['logic_voltage_v']).replace('.', ',')} V (GPIOs não tolerantes a 5 V)",
        ),
    ]
    lines = [f"| {l['property']} | {l['definition']} |", "|---|---|"]
    lines.extend(f"| {a} | {b_} |" for a, b_ in rows)
    return "\n".join(lines)


def gpio_map_table(hardware: dict, language: str) -> str:
    l = LABELS[language]
    c = hardware["components"]
    buses = hardware["buses"]

    rows: list[tuple[str, str, str, str, str]] = []

    for index, led in enumerate(c["blinking_leds"], start=1):
        rows.append((
            l["blue_led_output"].format(n=index),
            led["id"],
            f"blue_led_{index} / BLUE_LED_{index}_PIN",
            f"GPIO{led['gpio']}",
            led["header"],
        ))

    rows.extend([
        (l["green_led_output"], c["green_led"]["id"], "green_led / GREEN_LED_PIN", f"GPIO{c['green_led']['gpio']}", c["green_led"]["header"]),
        (l["main_button_input"], c["buttons"]["main"]["id"], "push_button / BUTTON_PIN", f"GPIO{c['buttons']['main']['gpio']}", c["buttons"]["main"]["header"]),
        (l["decrease_button"], c["buttons"]["decrease_interval"]["id"], "decrease_speed_button / DECREASE_SPEED_BUTTON_PIN", f"GPIO{c['buttons']['decrease_interval']['gpio']}", c["buttons"]["decrease_interval"]["header"]),
        (l["increase_button"], c["buttons"]["increase_interval"]["id"], "increase_speed_button / INCREASE_SPEED_BUTTON_PIN", f"GPIO{c['buttons']['increase_interval']['gpio']}", c["buttons"]["increase_interval"]["header"]),
        (l["bus_idle"], c["status_leds"]["bus_idle"]["id"], "bus_idle_led / BUS_IDLE_LED_PIN", f"GPIO{c['status_leds']['bus_idle']['gpio']}", c["status_leds"]["bus_idle"]["header"]),
        (l["scheduler_idle"], c["status_leds"]["scheduler_activity"]["id"], "scheduler_idle_led / SCHEDULER_IDLE_LED_PIN", f"GPIO{c['status_leds']['scheduler_activity']['gpio']}", c["status_leds"]["scheduler_activity"]["header"]),
        (l["oled_clock"].format(name=l["cpu_oled"]), c["displays"]["oled0_cpu"]["id"], "oled0_display / OLED0_SCL_PIN", f"GPIO{buses['oled0_i2c']['scl']['gpio']}", buses["oled0_i2c"]["scl"]["header"]),
        (l["oled_data"].format(name=l["cpu_oled"]), c["displays"]["oled0_cpu"]["id"], "oled0_display / OLED0_SDA_PIN", f"GPIO{buses['oled0_i2c']['sda']['gpio']}", buses["oled0_i2c"]["sda"]["header"]),
        (l["oled_clock"].format(name=l["ram_oled"]), c["displays"]["oled1_ram"]["id"], "oled1_display / OLED1_SCL_PIN", f"GPIO{buses['oled1_i2c']['scl']['gpio']}", buses["oled1_i2c"]["scl"]["header"]),
        (l["oled_data"].format(name=l["ram_oled"]), c["displays"]["oled1_ram"]["id"], "oled1_display / OLED1_SDA_PIN", f"GPIO{buses['oled1_i2c']['sda']['gpio']}", buses["oled1_i2c"]["sda"]["header"]),
        (l["tft_clock"], c["displays"]["tft_log"]["id"], "tft_display / TFT_SCK_PIN", f"GPIO{buses['tft_spi']['sck']['gpio']}", buses["tft_spi"]["sck"]["header"]),
        (l["tft_data"], c["displays"]["tft_log"]["id"], "tft_display / TFT_MOSI_PIN", f"GPIO{buses['tft_spi']['mosi']['gpio']}", buses["tft_spi"]["mosi"]["header"]),
        (l["tft_cs"], c["displays"]["tft_log"]["id"], "tft_display / TFT_CS_PIN", f"GPIO{buses['tft_spi']['cs']['gpio']}", buses["tft_spi"]["cs"]["header"]),
        (l["tft_dc"], c["displays"]["tft_log"]["id"], "tft_display / TFT_DC_PIN", f"GPIO{buses['tft_spi']['dc']['gpio']}", buses["tft_spi"]["dc"]["header"]),
        (l["tft_rst"], c["displays"]["tft_log"]["id"], "tft_display / TFT_RST_PIN", f"GPIO{buses['tft_spi']['rst']['gpio']}", buses["tft_spi"]["rst"]["header"]),
        (l["flash_switch"], c["flash_mode_switch"]["id"], "—", f"GPIO{c['flash_mode_switch']['gpio']}", c["flash_mode_switch"]["header"]),
        (l["supply"], "—", "—", "3V3", "J2-1"),
    ])

    lines = [
        f"| {l['function']} | {l['wokwi_id']} | {l['python_name']} | {l['gpio']} | {l['header_pin']} |",
        "|---|---|---|---:|---|",
    ]
    for function, wid, pyname, gpio, header in rows:
        wid_cell = f"`{wid}`" if wid != "—" else wid
        py_cell = f"`{pyname.split(' / ')[0]}` / `{pyname.split(' / ')[1]}`" if " / " in pyname else pyname
        lines.append(f"| {function} | {wid_cell} | {py_cell} | {gpio} | {header} |")
    return "\n".join(lines)


def gpio_constraints_table(hardware: dict, language: str) -> str:
    l = LABELS[language]
    constraints = hardware["gpio_constraints"]
    input_only = constraints["input_only"]["esp32_silicon"]
    boot = constraints["bootstrapping"]
    uart = constraints["primary_uart"]
    flash = constraints["reserved_spi_flash_signals"]

    gpio_join = (lambda xs: ", ".join(f"GPIO{x}" for x in xs))
    rows = [
        (l["reserved_flash"], ", ".join(f"`{x}`" for x in flash), l["flash_why"]),
        (l["input_only"], gpio_join(input_only), l["input_only_why"]),
        (l["bootstrapping"], gpio_join(boot), l["boot_why"]),
        (l["primary_uart"], gpio_join(uart), l["uart_why"]),
    ]
    lines = [f"| {l['restriction']} | {l['pins']} | {l['why']} |", "|---|---|---|"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def runtime_summary_table(runtime: dict, language: str) -> str:
    l = LABELS[language]
    blink = runtime["blinking_leds"]
    speed = blink["speed_control"]
    buttons = runtime["buttons"]
    graphs = runtime["resource_graphs"]
    serial = runtime["serial_status"]
    console = runtime["console"]

    rows = [
        (l["blink_base"], f'{blink["shared_base_interval_ms"]} ms'),
        (l["speed_steps"], f'{speed["step_min"]} … {speed["step_max"]}'),
        (l["button_sample"], f'{buttons["sample_interval_ms"]} ms'),
        (l["debounce"], f'{buttons["debounce_ms"]} ms'),
        (l["cpu_sample"], f'{graphs["cpu_sample_interval_ms"]} ms'),
        (l["ram_sample"], f'{graphs["ram_sample_interval_ms"]} ms'),
        (l["serial_interval"], f'{serial["print_interval_ms"]} ms'),
        (l["console_throttle"], str(console["log_throttle"])),
    ]
    lines = [f'| {l["parameter"]} | {l["value"]} |', "|---|---:|"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines)


def expected_blocks(language: str, hardware: dict, runtime: dict) -> dict[str, str]:
    return {
        "hardware-overview": overview_table(hardware, language),
        "board-summary": board_summary_table(hardware, language),
        "gpio-map": gpio_map_table(hardware, language),
        "gpio-constraints": gpio_constraints_table(hardware, language),
        "runtime-summary": runtime_summary_table(runtime, language),
    }


def replace_region(text: str, name: str, body: str) -> str:
    region = generated_region(name, body)
    pattern = re.compile(
        rf"<!-- BEGIN GENERATED: {re.escape(name)} -->.*?"
        rf"<!-- END GENERATED: {re.escape(name)} -->",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise ValueError(f"Missing generated region: {name}")
    return pattern.sub(lambda _: region, text)


def target_files() -> list[tuple[str, str, tuple[str, ...]]]:
    return [
        ("docs/EN/README.md", "EN", ("hardware-overview",)),
        ("docs/PT/README.md", "PT", ("hardware-overview",)),
        ("docs/EN/hardware-reference.md", "EN", ("board-summary", "gpio-map", "gpio-constraints")),
        ("docs/PT/hardware-reference.md", "PT", ("board-summary", "gpio-map", "gpio-constraints")),
        ("docs/EN/technical-specification.md", "EN", ("runtime-summary",)),
        ("docs/PT/technical-specification.md", "PT", ("runtime-summary",)),
    ]


def render_file(path: Path, language: str, names: tuple[str, ...], hardware: dict, runtime: dict) -> str:
    text = path.read_text(encoding="utf-8")
    blocks = expected_blocks(language, hardware, runtime)
    for name in names:
        text = replace_region(text, name, blocks[name])
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    hardware = load_json(HARDWARE_PATH)
    runtime = load_json(RUNTIME_PATH)

    stale: list[str] = []
    for relative, language, names in target_files():
        path = ROOT / relative
        expected = render_file(path, language, names, hardware, runtime)
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            if args.write:
                path.write_text(expected, encoding="utf-8")
                print(f"Updated {relative}")
            else:
                stale.append(relative)

    if stale:
        for relative in stale:
            print(f"Generated documentation is stale: {relative}")
        print("Run: python tools/generate_docs.py --write")
        return 1

    if args.check:
        print("Generated documentation blocks are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
