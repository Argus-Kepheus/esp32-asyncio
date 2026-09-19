<!-- doc-id: component-specifications -->
<!-- language: EN -->
<!-- content-revision: 2 -->

# Component Specifications — esp32-asyncio

One specification sheet per physical/simulated component used in
`diagram.json`, kept separate from the design rationale in
`technical-specification.md` so each part's identity, electrical role and
Wokwi identifier are unambiguous and easy to look up in isolation.

Each sheet documents the part as actually used in this project (not every
capability the real component has). Extend a sheet, rather than duplicating
it, if a future revision needs more detail on a given part.

> Current GPIOs, bus assignments, addresses, resistor values, pull configuration and supply rails are canonical in `config/hardware.json` and presented in generated form in `hardware-reference.md`. This document intentionally does not duplicate those values.

For the physical header position of each GPIO used here, reserved pins,
module (WROOM vs. WROVER) compatibility, electrical characteristics, and a
physical wiring checklist, see
[`docs/hardware-reference.md`](hardware-reference.md).

<!-- section: microcontroller-board -->
## 1. Microcontroller board — ESP32-DevKitC V4

Current board identity, module recommendation, header layout, firmware family and logic voltage are generated from `config/hardware.json` in [`hardware-reference.md`](hardware-reference.md), §1.

The Wokwi board intentionally leaves `attrs.env` unset. An earlier revision pinned `"micropython-20240602-v1.23.0"`, which caused an infinite reset loop on wokwi.com; removing that unsupported pin restored normal MicroPython startup. The selection rationale remains in `technical-specification.md`, §3.1.

### Pins used in this project

The full current GPIO-to-header map lives in
[`hardware-reference.md`](hardware-reference.md), §3; this row set is a
representative sample, not a duplicate of that table.

The complete current GPIO-to-header map is the generated table in [`hardware-reference.md`](hardware-reference.md), §3. It is not duplicated here.

<!-- section: displays -->
## 2. Displays — SSD1306 OLEDs and ILI9341 TFT

### 2.1 SSD1306 OLED (×2)

| Field | CPU OLED0 | RAM OLED1 |
|---|---|---|
| Display name | SSD1306 monochrome OLED, 128 × 64 | SSD1306 monochrome OLED, 128 × 64 |
| Wokwi part identifier | `board-ssd1306` | `board-ssd1306` |
| `diagram.json` part id | `oled0-display` | `oled1-display` |
| Interface used | I2C (the part also exists in SPI hardware variants, not used here — see `technical-specification.md`, §6.3) | I2C |
| Driver | `ssd1306.py` (`SSD1306_I2C` class), shared by both | (same) |
| Role in `main.py` | "CPU" resource graph (`update_cpu_graph()`) | "RAM" resource graph (`update_ram_graph()`) |

Current isolated diagnostics: `tests/05_cpu_oled_basic.py` /
`tests/06_cpu_oled_full_diagnostic.py` (CPU OLED0),
`tests/11_ram_oled_basic.py` (RAM OLED1, tested alone — does not prove
concurrent operation of both buses).

### 2.2 ILI9341 TFT

| Field | Value |
|---|---|
| Display name | ILI9341 color TFT, 240 × 320 |
| Wokwi part identifier | `wokwi-ili9341` |
| `diagram.json` part id | `tft-display` |
| Interface used | Genuine 4-wire SPI (SCK, MOSI, CS, D/C) plus a hardware RST line |
| Color depth | 16-bit RGB565 |
| Driver | `ili9341.py` (custom, this project's own `ILI9341` class) |
| Role in `main.py` | Scrolling colored activity log (`console_log()`) |

Current isolated diagnostics: `tests/12_tft_basic.py` (SPI init, solid
fills), `tests/13_tft_text_diagnostic.py` (text rendering, console
colors).

<!-- section: leds -->
## 3. LEDs

Nine LEDs total. The six blinking LEDs are all physically blue
(`#0000FF`) in `diagram.json` and use matching identifiers numbered 1–6 in
the circuit and Python source.

| Field | Blinking LEDs (×6) | Green LED | Bus-idle LED | Scheduler-idle LED |
|---|---|---|---|---|
| Wokwi part identifier | `wokwi-led` | `wokwi-led` | `wokwi-led` | `wokwi-led` |
| `diagram.json` part ids | `blue-led-1` through `blue-led-6` | `green-led` | `bus-idle-led` | `scheduler-idle-led` |
| Color attr | `#0000FF` (all six) | `green` | `orange` | `yellow` |
| Behavior | Each toggles independently on the shared interval (FR-01) | Mirrors the debounced button state (FR-02) | ON by default, OFF during an instrumented display write (FR-06) | Toggles every `scheduler_idle_task()` iteration (FR-06) |

<!-- section: series-resistors -->
## 4. Series resistors

| Field | LED resistors | Speed-button pull-downs |
|---|---|---|
| Wokwi part identifier | `wokwi-resistor` | `wokwi-resistor` |
| Purpose | Current-limiting for each LED at 3.3 V logic level | External pull-down for the speed-button input-only pins |

<!-- section: push-buttons -->
## 5. Push-buttons

| Field | Main button | Speed buttons (×2) |
|---|---|---|
| Wokwi part identifier | `wokwi-pushbutton` | `wokwi-pushbutton` |
| `diagram.json` part id | `push-button` | `decrease-speed-button`, `increase-speed-button` |
| Type | Normally-open, momentary, 4-leg (two electrically-common pairs) | Same |
| Valid `diagram.json` pin names | `1.l`, `1.r` (one node), `2.l`, `2.r` (other node) | Same |
| Simulation key binding | `" "` (space bar) | `"a"` (decrease), `"s"` (increase) |

> **Note:** an earlier draft of this project referenced this part's pins as
> `1.R` / `2.R` (wrong case, wrong side), which Wokwi cannot resolve — the
> connection silently fails and the button never registers a press. Always
> use the exact pin names listed above.

<!-- section: flash-mode-switch -->
## 6. Flash-mode slide switch

| Field | Value |
|---|---|
| Wokwi part identifier | `wokwi-slide-switch` |
| `diagram.json` part id | `flash-mode-switch` |
| Role | ROM bootloader boot-mode selection; not read by any `main.py` code — see `hardware-reference.md`, §5 |
