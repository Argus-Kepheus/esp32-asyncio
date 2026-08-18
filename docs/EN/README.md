# esp32-asyncio

**Language / Idioma:** [English](README.md) | [Português](../PT/README.md)

ESP32 (MicroPython) personal project exploring asynchronous (`asyncio`)
processing, originally a practical assessment for the Instrumentation,
Electronics and Programming Logic courses. Six independently-blinking
LEDs, a push-button driving a green LED, two activity-indicator LEDs,
two SSD1306 OLEDs plotting live CPU/RAM graphs, and an ILI9341 TFT log
console — all simulated in [Wokwi](https://wokwi.com).

**Wokwi simulation:** <https://wokwi.com/projects/471528241540407297>

## Hardware requirements

| Component | Wokwi identifier | ESP32 pin |
|---|---|---:|
| Board — Espressif ESP32-DevKitC V4 | `board-esp32-devkit-c-v4` | — |
| Six blinking LEDs (+ 220 Ω resistor each) | `red-led`, `blue-led`, `yellow-led`, `white-led`, `orange-led`, `red-led-2` | GPIO 26, 14, 27, 25, 33, 12 |
| Green LED (+ 220 Ω resistor) | `green-led` | GPIO 4 |
| Main push-button, normally-open | `push-button` | GPIO 17 |
| Two speed buttons (+ external 10 kΩ pull-down each) | `decrease-speed-button`, `increase-speed-button` | GPIO 34, 35 |
| Two status-indicator LEDs (+ 220 Ω resistor each) | `bus-idle-led` (orange), `scheduler-idle-led` (yellow) | GPIO 13, 2 |
| First OLED, SSD1306 128×64, I2C(0) | `oled-display` | SCL = GPIO 32, SDA = GPIO 16 |
| Second OLED, SSD1306 128×64, I2C(1) | `oled-display-2` | SCL = GPIO 15, SDA = GPIO 22 |
| TFT, ILI9341 240×320, SPI | `tft-display` | SCK 18, MOSI 23, CS 5, D/C 21, RST 19 |

The two OLEDs and the three push-buttons run on the board's 3.3 V rail;
the TFT runs on 5 V (see `hardware-reference.md`, §6, for the physical-build
caveat that implies). All components share a common ground.
Full electrical detail (headers, reserved pins, wiring checklist) is in
[`hardware-reference.md`](hardware-reference.md); exact per-part
identifiers are in
[`component-specifications.md`](component-specifications.md).

## Software requirements

- MicroPython for ESP32.
- `main.py` runs thirteen concurrent `asyncio` flows — six blinking-LED
  tasks, the scheduler-activity indicator, both OLED graph tasks, a
  serial status task, and three button monitors — so no LED's blink is
  ever delayed by a display refresh beyond the write itself.
- The main push-button uses the ESP32's internal pull-down resistor
  (`Pin.PULL_DOWN`); the two speed buttons need their own external
  pull-down (GPIO34/35 have none internally).
- The two OLEDs use I2C (`machine.I2C`, one bus each) at address `0x3C`,
  driven by `ssd1306.py`; the TFT uses SPI (`machine.SPI`), driven by
  this project's own `ili9341.py`.

Full requirements and design rationale are in
[`technical-specification.md`](technical-specification.md).

## Result

Six LEDs blink independently on a shared, button-adjustable interval; the
main push-button drives a green LED and logs every transition to the TFT
console and the serial console; the two OLEDs plot live CPU- and
RAM-usage graphs; and the two status-indicator LEDs reflect display-bus
and scheduler activity in real time.

## License

This project is dedicated to the public domain under **CC0 1.0 Universal**.
See [`LICENSE`](../../LICENSE).
