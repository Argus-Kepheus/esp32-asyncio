# esp32-asyncio

**Language / Idioma:** [English](README.md) | [Português](../PT/README.md)

ESP32 (MicroPython) practical assessment for the Instrumentation,
Electronics and Programming Logic courses. Two LEDs and an SSD1306 OLED
display react to a push-button, simulated in [Wokwi](https://wokwi.com).

> **🚧 Project status:** the requirements and tables below describe the
> original mandatory assessment. The red LED and push-button/green-LED
> behavior are still exactly as described; the pin numbers below are kept
> current (see the note under "Hardware requirements"). The OLED message
> behavior, however, has been **superseded**, not just extended: both
> OLEDs now show live resource-usage graphs instead of button text. Since
> the original scope was completed, the hardware and `main.py` have also
> been extended experimentally (more LEDs, a second OLED, a TFT display,
> extra buttons, and more) at the user's request, and that extension is
> **still actively changing** — see
> [`technical-specification.md`](technical-specification.md)'s "Extended
> features" section for the full current state.

**Wokwi simulation:** <https://wokwi.com/projects/471528241540407297>

## Hardware requirements

| Component | Wokwi identifier | ESP32 pin |
|---|---|---:|
| Board — Espressif ESP32-DevKitC V4 | `board-esp32-devkit-c-v4` | — |
| Red LED (+ 220 Ω resistor) | `red-led` | GPIO 26 |
| Green LED (+ 220 Ω resistor) | `green-led` | GPIO 4 |
| Push-button, normally-open | `push-button` | GPIO 17 |
| OLED display, SSD1306 128×64, I2C | `oled-display` | SCL = GPIO 32, SDA = GPIO 16 |

The red LED and OLED SCL pins moved off their originally-assigned GPIO 2
and GPIO 25 at the user's explicit request, for board layout (see
`technical-specification.md`, §16 decision log); the table above is kept
current, not historical. All components run on the board's 3.3 V rail and
share a common ground.
Full electrical detail (headers, reserved pins, wiring checklist) is in
[`hardware-reference.md`](hardware-reference.md); exact per-part
identifiers are in
[`component-specifications.md`](component-specifications.md).

## Software requirements

- MicroPython for ESP32.
- `main.py` runs the red LED blink, push-button/green LED logic, and OLED
  updates as concurrent `asyncio` tasks, so the red LED blink is never
  delayed by an OLED refresh.
- The push-button uses the ESP32's internal pull-down resistor
  (`Pin.PULL_DOWN`); no external resistor is required.
- The OLED uses I2C (`machine.I2C`) at address `0x3C`, driven by
  `ssd1306.py`.

Full requirements and design rationale are in
[`technical-specification.md`](technical-specification.md).

## Result

| Push-button state | Green LED | OLED message |
|---|---|---|
| Released | OFF | `Boa sorte!` |
| Pressed | ON | `Consegui` |

The green LED column is still accurate. The OLED message column is not
— **superseded**, not extended: neither OLED shows button text anymore,
both are live CPU/RAM usage graphs (see "Extended features" in
`technical-specification.md`).

The red LED blinks continuously every 500 ms, independently of the
push-button, green LED, and OLED.

## License

This project is dedicated to the public domain under **CC0 1.0 Universal**.
See [`LICENSE`](../../LICENSE).
