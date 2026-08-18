# Component Specifications — esp32-asyncio

One specification sheet per physical/simulated component used in
`diagram.json`, kept separate from the design rationale in
`technical-specification.md` so each part's identity, electrical role and
Wokwi identifier are unambiguous and easy to look up in isolation.

Each sheet documents the part as actually used in this project (not every
capability the real component has). Extend a sheet, rather than duplicating
it, if a future revision needs more detail on a given part.

For the physical header position of each GPIO used here, reserved pins,
module (WROOM vs. WROVER) compatibility, electrical characteristics, and a
physical wiring checklist, see
[`docs/hardware-reference.md`](hardware-reference.md).

## 1. Microcontroller board — ESP32-DevKitC V4

| Field | Value |
|---|---|
| Board name | Espressif ESP32-DevKitC V4 |
| Wokwi part identifier | `board-esp32-devkit-c-v4` |
| `diagram.json` part id | `esp32` |
| Microcontroller family | ESP32 |
| Recommended module profile | ESP32-WROOM-32E |
| Header layout | 38 pins, 19 pins per side |
| Firmware | MicroPython for ESP32 |
| Firmware version pin in `diagram.json` (`attrs.env`) | None — `attrs: {}`. An earlier revision pinned `"env": "micropython-20240602-v1.23.0"`, which caused an infinite boot-loop on wokwi.com (repeated `SW_RESET`, MicroPython never starts). Removed; the board now uses Wokwi's default/current MicroPython build. See `docs/technical-specification.md`, §16. |
| Pin-numbering convention | ESP32 GPIO numbers, not sequential physical header positions |
| Logic level | 3.3 V |
| Selection rationale | See `technical-specification.md`, §3.1 |

### Pins used in this project

The full current GPIO-to-header map lives in
[`hardware-reference.md`](hardware-reference.md), §3; this row set is a
representative sample, not a duplicate of that table.

| Board pin | GPIO | Connected to |
|---|---:|---|
| `26` | GPIO 26 | Blinking LED 1 (through 220 Ω resistor) |
| `4` | GPIO 4 | Green LED (through 220 Ω resistor) |
| `17` | GPIO 17 | Main push-button |
| `32` | GPIO 32 | First OLED SCL |
| `16` | GPIO 16 | First OLED SDA |
| `3V3` | — | Push-button and OLED supply |
| `5V` | — | TFT supply |
| `GND.1` / `GND.2` | — | LED cathodes, OLED GND, TFT GND |
| `TX` / `RX` | — | `$serialMonitor` (debug output only, not part of the functional requirements) |

## 2. Displays — SSD1306 OLEDs and ILI9341 TFT

### 2.1 SSD1306 OLED (×2)

| Field | First OLED | Second OLED |
|---|---|---|
| Display name | SSD1306 monochrome OLED, 128 × 64 | SSD1306 monochrome OLED, 128 × 64 |
| Wokwi part identifier | `board-ssd1306` | `board-ssd1306` |
| `diagram.json` part id | `oled-display` | `oled-display-2` |
| Interface used | I2C (the part also exists in SPI hardware variants, not used here — see `technical-specification.md`, §6.3) | I2C |
| I2C address | `0x3C` | `0x3C` |
| MicroPython bus object | `machine.I2C(0, ...)` | `machine.I2C(1, ...)`, independent bus |
| Supply | 3.3 V and GND | 3.3 V and GND |
| Driver | `ssd1306.py` (`SSD1306_I2C` class), shared by both | (same) |
| Role in `main.py` | "CPU" resource graph (`update_cpu_graph()`) | "RAM" resource graph (`update_ram_graph()`) |
| Pins | SCL → GPIO 32, SDA → GPIO 16 | SCL → GPIO 15, SDA → GPIO 22 |

Current isolated diagnostics: `tests/05_cpu_oled_basic.py` /
`tests/06_cpu_oled_full_diagnostic.py` (first OLED),
`tests/11_ram_oled_basic.py` (second OLED, tested alone — does not prove
concurrent operation of both buses).

### 2.2 ILI9341 TFT

| Field | Value |
|---|---|
| Display name | ILI9341 color TFT, 240 × 320 |
| Wokwi part identifier | `wokwi-ili9341` |
| `diagram.json` part id | `tft-display` |
| Interface used | Genuine 4-wire SPI (SCK, MOSI, CS, D/C) plus a hardware RST line |
| Color depth | 16-bit RGB565 |
| Supply | 5 V and GND (see `hardware-reference.md`, §6, for the physical-build caveat this implies) |
| Driver | `ili9341.py` (custom, this project's own `ILI9341` class) |
| MicroPython bus object | `machine.SPI(2, ...)` |
| Role in `main.py` | Scrolling colored activity log (`console_log()`) |
| Pins | SCK → GPIO 18, MOSI → GPIO 23, CS → GPIO 5, D/C → GPIO 21, RST → GPIO 19 |

Current isolated diagnostics: `tests/12_tft_basic.py` (SPI init, solid
fills), `tests/13_tft_text_diagnostic.py` (text rendering, console
colors).

## 3. LEDs

Nine LEDs total. The six blinking LEDs are all physically blue
(`#0000FF`) in `diagram.json`; their `diagram.json`/Python identifiers
are historical per-LED labels, not color descriptions (see
`technical-specification.md`, §16, for why).

| Field | Blinking LEDs (×6) | Green LED | Bus-idle LED | Scheduler-idle LED |
|---|---|---|---|---|
| Wokwi part identifier | `wokwi-led` | `wokwi-led` | `wokwi-led` | `wokwi-led` |
| `diagram.json` part ids | `red-led`, `blue-led`, `yellow-led`, `white-led`, `orange-led`, `red-led-2` | `green-led` | `bus-idle-led` | `scheduler-idle-led` |
| Color attr | `#0000FF` (all six) | `green` | `orange` | `yellow` |
| GPIO (anode via resistor) | 26, 14, 27, 25, 33, 12 | 4 | 13 | 2 |
| Cathode connected to | ESP32 GND | ESP32 GND | ESP32 GND | ESP32 GND |
| Behavior | Each toggles independently on the shared interval (FR-01) | Mirrors the debounced button state (FR-02) | ON by default, OFF during an instrumented display write (FR-06) | Toggles every `scheduler_idle_task()` iteration (FR-06) |

## 4. Series resistors

| Field | LED resistors | Speed-button pull-downs |
|---|---|---|
| Wokwi part identifier | `wokwi-resistor` | `wokwi-resistor` |
| `diagram.json` part ids | one per LED (9 total): `red-led-resistor`, `blue-led-resistor`, `yellow-led-resistor`, `white-led-resistor`, `orange-led-resistor`, `red-led-2-resistor`, `green-led-resistor`, `bus-idle-led-resistor`, `scheduler-idle-led-resistor` | `decrease-speed-button-pulldown`, `increase-speed-button-pulldown` |
| Value | 220 Ω | 10 kΩ |
| Purpose | Current-limiting for each LED at 3.3 V logic level | External pull-down for GPIO34/35, which have no internal one |

## 5. Push-buttons

| Field | Main button | Speed buttons (×2) |
|---|---|---|
| Wokwi part identifier | `wokwi-pushbutton` | `wokwi-pushbutton` |
| `diagram.json` part id | `push-button` | `decrease-speed-button`, `increase-speed-button` |
| Type | Normally-open, momentary, 4-leg (two electrically-common pairs) | Same |
| Valid `diagram.json` pin names | `1.l`, `1.r` (one node), `2.l`, `2.r` (other node) | Same |
| Pins used in this project | `1.l` → ESP32 `3V3`; `2.l` → ESP32 GPIO 17 | `1.l` → ESP32 `3V3`; `2.l` → ESP32 GPIO 34 / GPIO 35, each through its own external 10 kΩ pull-down |
| Simulation key binding | `" "` (space bar) | `"a"` (decrease), `"s"` (increase) |
| Electrical role | Active-high input with internal `Pin.PULL_DOWN` on GPIO 17 — see `technical-specification.md`, §6.2 | Active-high input, no internal pull resistor (input-only pins) — external pull-down required |

> **Note:** an earlier draft of this project referenced this part's pins as
> `1.R` / `2.R` (wrong case, wrong side), which Wokwi cannot resolve — the
> connection silently fails and the button never registers a press. Always
> use the exact pin names listed above.

## 6. Flash-mode slide switch

| Field | Value |
|---|---|
| Wokwi part identifier | `wokwi-slide-switch` |
| `diagram.json` part id | `flash-mode-switch` |
| Pins used in this project | one terminal → ESP32 GPIO 0, the other → GND |
| Role | ROM bootloader boot-mode selection; not read by any `main.py` code — see `hardware-reference.md`, §5 |
