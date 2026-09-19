<!-- doc-id: hardware-reference -->
<!-- language: EN -->
<!-- content-revision: 3 -->

# ESP32-DevKitC V4 Hardware Reference

The single source of truth for the physical board, module, GPIO-to-header
mapping, and electrical constraints. Behavioral/software rationale (why
`asyncio`, why I2C over SPI, debounce strategy, OLED update strategy) lives
in [`technical-specification.md`](technical-specification.md) and is not
repeated here. Per-part Wokwi identifiers live in
[`component-specifications.md`](component-specifications.md).

<!-- section: selected-board -->
## 1. Selected board

<!-- BEGIN GENERATED: board-summary -->
| Property | Project definition |
|---|---|
| Manufacturer | Espressif Systems |
| Board name | ESP32-DevKitC V4 |
| Wokwi identifier | `board-esp32-devkit-c-v4` (`diagram.json` id `esp32`) |
| Header arrangement | 38 pins, 19 per side (J2, J3) |
| Microcontroller family | ESP32 |
| Recommended physical module | ESP32-WROOM-32E |
| Firmware | MicroPython for ESP32 |
| Logic voltage | 3.3 V (not 5 V tolerant) |
<!-- END GENERATED: board-summary -->

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

Must not be replaced with another board type without reviewing the
complete pin mapping in §3 — see also the decision log in
`technical-specification.md`, §16.

<!-- section: board-rationale -->
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

<!-- section: gpio-header-mapping -->
## 3. GPIO-to-header mapping

All source and circuit references use the **ESP32 GPIO number**, not the
sequential physical position of a header terminal — e.g. `GPIO25` is the
signal named GPIO25, not the 25th physical pin.

<!-- BEGIN GENERATED: gpio-map -->
| Function | Wokwi identifier | Python variable/constant | GPIO | Header pin |
|---|---|---|---:|---|
| Blinking LED 1 output | `blue-led-1` | `blue_led_1` / `BLUE_LED_1_PIN` | GPIO26 | J2-10 |
| Blinking LED 2 output | `blue-led-2` | `blue_led_2` / `BLUE_LED_2_PIN` | GPIO14 | J2-12 |
| Blinking LED 3 output | `blue-led-3` | `blue_led_3` / `BLUE_LED_3_PIN` | GPIO27 | J2-11 |
| Blinking LED 4 output | `blue-led-4` | `blue_led_4` / `BLUE_LED_4_PIN` | GPIO25 | J2-9 |
| Blinking LED 5 output | `blue-led-5` | `blue_led_5` / `BLUE_LED_5_PIN` | GPIO33 | J2-8 |
| Blinking LED 6 output | `blue-led-6` | `blue_led_6` / `BLUE_LED_6_PIN` | GPIO12 | J2-13 |
| Green LED output | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Push-button input | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| Decrease-speed button | `decrease-speed-button` | `decrease_speed_button` / `DECREASE_SPEED_BUTTON_PIN` | GPIO34 | J2-5 |
| Increase-speed button | `increase-speed-button` | `increase_speed_button` / `INCREASE_SPEED_BUTTON_PIN` | GPIO35 | J2-6 |
| Bus-idle LED (orange) | `bus-idle-led` | `bus_idle_led` / `BUS_IDLE_LED_PIN` | GPIO13 | J2-15 |
| Scheduler-idle LED (yellow) | `scheduler-idle-led` | `scheduler_idle_led` / `SCHEDULER_IDLE_LED_PIN` | GPIO2 | J3-15 |
| CPU OLED0, I2C clock | `oled0-display` | `oled0_display` / `OLED0_SCL_PIN` | GPIO32 | J2-7 |
| CPU OLED0, I2C data | `oled0-display` | `oled0_display` / `OLED0_SDA_PIN` | GPIO16 | J3-12 |
| RAM OLED1, I2C clock | `oled1-display` | `oled1_display` / `OLED1_SCL_PIN` | GPIO15 | J3-16 |
| RAM OLED1, I2C data | `oled1-display` | `oled1_display` / `OLED1_SDA_PIN` | GPIO22 | J3-3 |
| TFT SPI clock | `tft-display` | `tft_display` / `TFT_SCK_PIN` | GPIO18 | J3-9 |
| TFT SPI data out | `tft-display` | `tft_display` / `TFT_MOSI_PIN` | GPIO23 | J3-2 |
| TFT chip select | `tft-display` | `tft_display` / `TFT_CS_PIN` | GPIO5 | J3-10 |
| TFT data/command | `tft-display` | `tft_display` / `TFT_DC_PIN` | GPIO21 | J3-6 |
| TFT hardware reset | `tft-display` | `tft_display` / `TFT_RST_PIN` | GPIO19 | J3-8 |
| Flash-mode slide switch | `flash-mode-switch` | — | GPIO0 | J3-14 |
| OLED / push-button supply | — | — | 3V3 | J2-1 |
<!-- END GENERATED: gpio-map -->

The six blinking LEDs are all physically blue (`#0000FF`) and use the same 1–6 numbering in Wokwi IDs and Python identifiers.

Conceptual wiring topology:

```text
ESP32 output ── current-limiting resistor ── LED ── GND
supply rail ── push-button ── ESP32 input
ESP32 input ── external pull-down ── GND   (where required)
ESP32 bus signals ── display interface
```

Concrete GPIOs, resistor values, pull configuration, bus IDs, display addresses and supply rails are not repeated in prose. They are canonical in `config/hardware.json` and presented above in the generated GPIO map. `diagram.json` remains the authority for Wokwi routing geometry.

<!-- section: module-compatibility -->
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

<!-- section: restricted-gpios -->
## 5. Restricted / reserved GPIOs

<!-- BEGIN GENERATED: gpio-constraints -->
| Restriction | Pins | Why |
|---|---|---|
| Reserved for SPI flash | `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` | Internal flash communication; do not use as project GPIO |
| Input-only | GPIO34, GPIO35, GPIO36, GPIO37, GPIO38, GPIO39 | Cannot drive outputs; no internal pull-up/pull-down |
| Bootstrapping | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | Sampled at boot; project uses are documented and validated |
| Primary UART | GPIO1, GPIO3 | Used for programming/diagnostic serial; not a project peripheral |
<!-- END GENERATED: gpio-constraints -->

The generated table above lists the restricted categories relevant to this project. Project-specific bootstrapping/input-only notes are maintained in `config/hardware.json` under `gpio_constraints.notes`, so changes in component roles do not require a second manually synchronized pin list here.

For a physical build, treat any bootstrapping-pin use as a verification point: confirm that the attached circuit does not force an incompatible startup level. UART pins remain reserved for programming/REPL/serial diagnostics rather than normal project peripherals.

<!-- section: electrical-characteristics -->
## 6. Electrical characteristics

- Respect the board logic voltage shown in the generated board summary; never drive a GPIO from a higher supply rail.
- All peripherals must share a common ground reference.
- Every LED requires current limiting; the current resistor values are canonical in `config/hardware.json`.
- OLED bus selection, pins, addresses and frequency are canonical in `config/hardware.json`; `technical-specification.md` explains why I2C was selected.
- The TFT supply rail and SPI mapping are also canonical in `config/hardware.json`. For physical hardware, verify whether the specific ILI9341 module includes the regulator/level-shifting expected by its supply connection before applying power.
- Button pull configuration is canonical in `config/hardware.json`; debounce behavior is a runtime/software concern documented in `technical-specification.md`.

<!-- section: physical-checklist -->
## 7. Physical implementation checklist

For a future real-hardware build (the current project targets simulation):

- verify the exact board/module against the generated board summary and module-compatibility section;
- reproduce every signal connection from the generated GPIO map rather than from prose examples;
- reproduce resistor values, pull configuration and supply rails from `config/hardware.json`;
- keep all grounds common;
- review every bootstrapping/input-only/reserved-pin constraint before assembly;
- verify the actual OLED and ILI9341 module electrical characteristics before applying power;
- treat `diagram.json` as the simulation netlist/layout, not as proof that a physical module includes protection/regulation circuitry;
- rerun the manual hardware diagnostics after assembly.

<!-- section: references -->
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

<!-- section: board-identification -->
## 9. Board identification statement

For use in reports and submission documentation:

> The project targets the official Espressif ESP32-DevKitC V4 development
> board, represented in Wokwi by `board-esp32-devkit-c-v4`. A physical
> implementation should preferably use an ESP32-DevKitC V4 fitted with an
> ESP32-WROOM-32E module so that GPIO16 and GPIO17 remain available for the
> predefined OLED and push-button connections. All pin references use ESP32
> GPIO numbers rather than sequential physical header positions.
