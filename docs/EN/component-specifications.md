# Component Specifications — cess-uff

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

| Board pin | GPIO | Connected to |
|---|---:|---|
| `2` | GPIO 2 | Red LED (through 220 Ω resistor) |
| `4` | GPIO 4 | Green LED (through 220 Ω resistor) |
| `17` | GPIO 17 | Push-button |
| `25` | GPIO 25 | OLED SCL |
| `16` | GPIO 16 | OLED SDA |
| `3V3` | — | Push-button supply, OLED VCC |
| `GND.2` | — | LED cathodes, OLED GND |
| `TX` / `RX` | — | `$serialMonitor` (debug output only, not part of the functional requirements) |

## 2. Display — SSD1306 OLED

| Field | Value |
|---|---|
| Display name | SSD1306 monochrome OLED, 128 × 64 |
| Wokwi part identifier | `board-ssd1306` |
| `diagram.json` part id | `oled-display` |
| Controller IC | SSD1306 |
| Resolution | 128 × 64 px, monochrome |
| Interface used | I2C (the part also exists in SPI hardware variants, not used here — see `technical-specification.md`, §6.3) |
| I2C address | `0x3C` (`diagram.json` attr `i2cAddress`) |
| Supply | 3.3 V and GND |
| Driver | `ssd1306.py` (`SSD1306_I2C` class) |
| MicroPython bus object | `machine.I2C(0, ...)` (hardware) — confirmed working on wokwi.com by `tests/05_oled_basic.py` and `tests/06_oled_full_diagnostic.py`; see `technical-specification.md`, §16 decision log |

### Pins used in this project

| Display pin | Connected to |
|---|---|
| `VCC` | ESP32 `3V3` |
| `GND` | ESP32 `GND.2` |
| `SCL` | ESP32 GPIO 25 |
| `SDA` | ESP32 GPIO 16 |

## 3. LEDs

| Field | Red LED | Green LED |
|---|---|---|
| Wokwi part identifier | `wokwi-led` | `wokwi-led` |
| `diagram.json` part id | `red-led` | `green-led` |
| Color attr | `red` | `green` |
| Anode (`A`) connected to | 220 Ω resistor `red-led-resistor` → ESP32 GPIO 2 | 220 Ω resistor `green-led-resistor` → ESP32 GPIO 4 |
| Cathode (`C`) connected to | ESP32 `GND.2` | ESP32 `GND.2` |
| Behavior | Toggles every 500 ms, always | Mirrors the debounced button state |

## 4. Series resistors

| Field | Value |
|---|---|
| Wokwi part identifier | `wokwi-resistor` |
| `diagram.json` part ids | `red-led-resistor`, `green-led-resistor` |
| Value | 220 Ω |
| Purpose | Current-limiting for each LED at 3.3 V logic level |

## 5. Push-button

| Field | Value |
|---|---|
| Wokwi part identifier | `wokwi-pushbutton` |
| `diagram.json` part id | `push-button` |
| Type | Normally-open, momentary, 4-leg (two electrically-common pairs) |
| Valid `diagram.json` pin names | `1.l`, `1.r` (one node), `2.l`, `2.r` (other node) |
| Pins used in this project | `1.l` → ESP32 `3V3`; `2.l` → ESP32 GPIO 17 |
| Simulation key binding | `" "` (attr `key`; the literal `KeyboardEvent.key` value for the space bar) |
| Electrical role | Active-high input with internal `Pin.PULL_DOWN` on GPIO 17 — see `technical-specification.md`, §6.2 |

> **Note:** an earlier draft of this project referenced this part's pins as
> `1.R` / `2.R` (wrong case, wrong side), which Wokwi cannot resolve — the
> connection silently fails and the button never registers a press. Always
> use the exact pin names listed above.
