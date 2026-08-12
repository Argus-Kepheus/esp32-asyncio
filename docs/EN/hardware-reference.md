# ESP32-DevKitC V4 Hardware Reference

The single source of truth for the physical board, module, GPIO-to-header
mapping, and electrical constraints. Behavioral/software rationale (why
`asyncio`, why I2C over SPI, debounce strategy, OLED update strategy) lives
in [`technical-specification.md`](technical-specification.md) and is not
repeated here. Per-part Wokwi identifiers live in
[`component-specifications.md`](component-specifications.md).

## 1. Selected board

| Property | Project definition |
|---|---|
| Manufacturer | Espressif Systems |
| Board name | ESP32-DevKitC V4 |
| Wokwi part identifier | `board-esp32-devkit-c-v4` (`diagram.json` id `esp32`) |
| Header arrangement | 38 pins, 19 per side (J2, J3) |
| Microcontroller family | Original ESP32 |
| Recommended physical module | ESP32-WROOM-32E |
| Firmware | MicroPython for ESP32 |
| Logic voltage | 3.3 V (not 5 V tolerant) |

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

Must not be replaced with another board type without reviewing the
complete pin mapping in §3 — see also the decision log in
`technical-specification.md`, §16.

## 2. Why this board, and why "ESP32" alone is not enough

The assignment only requires "MicroPython for ESP32," not a specific
board. The ESP32-DevKitC V4 was selected because it is an official
Espressif board, natively supported by Wokwi, exposes every GPIO the
project needs, and has complete manufacturer documentation — this
maximizes reproducibility and avoids the ambiguity of generic ESP32
clones (which vary in header count, module variant, and printed pin
labels; see ESP32-S2/S3/C3/C6 families, NodeMCU-style boards, WROVER
variants, etc.). For this reason the project is always documented as
**"Espressif ESP32-DevKitC V4 / `board-esp32-devkit-c-v4`,"** never just
"ESP32" or "ESP32 DevKit."

The board and the radio module are different things: the DevKitC V4 is
the carrier PCB (USB, regulator, headers); the module is the
metal-shielded part with the actual chip, flash, and antenna. A DevKitC
V4 can be fitted with different modules — see §4.

## 3. GPIO-to-header mapping

All source and circuit references use the **ESP32 GPIO number**, not the
sequential physical position of a header terminal — e.g. `GPIO25` is the
signal named GPIO25, not the 25th physical pin.

| Function | Wokwi ID | Python variable/constant | GPIO | Header pin |
|---|---|---|---:|---|
| Red LED output | `red-led` | `red_led` / `RED_LED_PIN` | GPIO2 | J3-15 |
| Green LED output | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Push-button input | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| OLED I²C data | `oled-display` | `oled_display` / `OLED_SDA_PIN` | GPIO16 | J3-12 |
| OLED I²C clock | `oled-display` | `oled_display` / `OLED_SCL_PIN` | GPIO25 | J2-9 |
| OLED / push-button supply | — | — | 3V3 | J2-1 |

```python
RED_LED_PIN = 2
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SDA_PIN = 16
OLED_SCL_PIN = 25
```

Wiring topology (see `component-specifications.md` for exact Wokwi part
IDs and `diagram.json` for routed connections):

```text
GPIO2  ── 220 Ω resistor ── red LED anode   · red LED cathode   ── GND
GPIO4  ── 220 Ω resistor ── green LED anode · green LED cathode ── GND
3V3    ── push-button ── GPIO17                       (active HIGH)
GPIO25 = OLED SCL   GPIO16 = OLED SDA   3V3 = OLED VCC   GND = OLED GND
```

All peripherals share a common ground; the OLED and push-button use the
3.3 V rail only.

## 4. Module compatibility — WROOM vs. WROVER

This project requires GPIO16 and GPIO17 (OLED SDA and the push-button).

| Module family | Compatibility |
|---|---|
| ESP32-WROOM | Recommended — GPIO16/17 available for general use |
| ESP32-WROOM-32E | Preferred physical target |
| ESP32-WROVER | **Not recommended** — GPIO16/17 may be routed internally to PSRAM |

A WROVER-based board would need a pin reassignment across `main.py`,
`diagram.json`, the wiring, and this documentation. Since GPIO16/17 are
predefined project requirements, that reassignment is out of scope here.

## 5. Restricted / reserved GPIOs

| Restriction | Pins | Why |
|---|---|---|
| Reserved for SPI flash | `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` | Internal flash communication; using them as GPIO can prevent the firmware from booting |
| Input-only | GPIO34–GPIO39 | Cannot drive outputs; no internal pull-up/pull-down |
| Bootstrapping | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | Sampled at boot to select boot mode. GPIO2 is used here for the red LED (a required assignment) — the LED/resistor circuit does not force an external level on it, so it does not interfere with boot |
| Primary UART | GPIO1, GPIO3 | Used for programming/diagnostic output and the Wokwi serial monitor; not used by project peripherals |

## 6. Electrical characteristics

- **Logic level:** 3.3 V. Never apply 5 V to a GPIO.
- **Common ground:** every component (LEDs, button, OLED) must share the
  same GND reference, or GPIO/I²C signal levels are undefined.
- **LED current limiting:** each LED uses a 220 Ω series resistor; do not
  omit it in a physical build.
- **OLED interface:** I²C only, on GPIO25 (SCL) / GPIO16 (SDA) — this is a
  predefined project requirement, not an optimization; see
  `technical-specification.md` §6.3 for why I²C was chosen over SPI, and
  `component-specifications.md` §2 for the driver/bus details (hardware
  `machine.I2C`).

## 7. Physical implementation checklist

For a future real-hardware build (this project currently targets
simulation only):

- board is an ESP32-DevKitC V4 (or verified-compatible equivalent) fitted
  with a WROOM, not WROVER, module;
- OLED powered from 3.3 V; all grounds tied together;
- each LED has its 220 Ω series resistor; red → GPIO2, green → GPIO4;
- push-button between GPIO17 and 3V3, no external pull-up;
- OLED SDA → GPIO16, OLED SCL → GPIO25;
- nothing connected to `CLK`, `D0`–`D3`, `CMD`;
- no GPIO receives 5 V.

## 8. References

**Espressif / MicroPython:**
- [ESP32-DevKitC V4 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
- [ESP32 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [ESP32-WROOM-32E datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf)
- [MicroPython ESP32 quick reference](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [`machine.Pin`](https://docs.micropython.org/en/latest/library/machine.Pin.html) · [`machine.I2C`](https://docs.micropython.org/en/latest/library/machine.I2C.html) · [`asyncio`](https://docs.micropython.org/en/latest/library/asyncio.html)

**Wokwi:**
- [`board-esp32-devkit-c-v4` component](https://docs.wokwi.com/parts/board-esp32-devkit-c-v4)
- [`diagram.json` format](https://docs.wokwi.com/diagram-format)

## 9. Board identification statement

For use in reports and submission documentation:

> The project targets the official Espressif ESP32-DevKitC V4 development
> board, represented in Wokwi by `board-esp32-devkit-c-v4`. A physical
> implementation should preferably use an ESP32-DevKitC V4 fitted with an
> ESP32-WROOM-32E module so that GPIO16 and GPIO17 remain available for the
> predefined OLED and push-button connections. All pin references use ESP32
> GPIO numbers rather than sequential physical header positions.
