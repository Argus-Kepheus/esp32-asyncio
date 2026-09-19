# Current-hardware diagnostic tests

Thirteen standalone scripts validate only components present in the current
`diagram.json`: six blue blinking LEDs, the green push-button and green LED,
two blue interval buttons, orange/yellow status LEDs, two SSD1306 OLEDs and one
ILI9341 TFT. The suite does not preserve historical component colors, messages
or pin assignments.

These scripts are manual hardware diagnostics for Wokwi or a physical ESP32.
They are not automated proof that `main.py` passes: record the observed result
after actually running each relevant script.

## Recorded execution

All thirteen scripts were run successfully on Wokwi web on 2026-08-18. The
expected behavior described by each script was observed. Because
`diagram.json` does not pin `attrs.env`, the web simulator used its default
MicroPython firmware; its exact build identifier was not recorded.

The full-application procedures TC-08 through TC-11 were also run successfully
on Wokwi web on 2026-08-18. They cover interval clamping, simultaneous use of
all three displays, the TFT failure path and a 10–15 minute run; their detailed
results are recorded in `docs/EN/technical-specification.md`, section 12.

## Current order

| # | File | Current hardware checked | Pins / bus |
|---|---|---|---|
| 1 | [`01_blue_led_basic.py`](01_blue_led_basic.py) | First blue LED, explicit ON/OFF | GPIO 26 |
| 2 | [`02_blue_led_blink.py`](02_blue_led_blink.py) | First blue LED, toggle loop | GPIO 26 |
| 3 | [`03_blue_led_asyncio.py`](03_blue_led_asyncio.py) | First blue LED driven by `asyncio` | GPIO 26 |
| 4 | [`04_green_button_led.py`](04_green_button_led.py) | Green push-button driving the green LED | GPIO 17 / GPIO 4 |
| 5 | [`05_cpu_oled_basic.py`](05_cpu_oled_basic.py) | CPU OLED: I2C scan and current-role label | `I2C(0)`, SCL 32, SDA 16, `0x3C` |
| 6 | [`06_cpu_oled_full_diagnostic.py`](06_cpu_oled_full_diagnostic.py) | CPU OLED and all `ssd1306.py` drawing primitives | `I2C(0)`, SCL 32, SDA 16, `0x3C` |
| 7 | [`07_additional_blue_leds_basic.py`](07_additional_blue_leds_basic.py) | Blue LEDs 2–6, one at a time | GPIO 14, 27, 25, 33, 12 |
| 8 | [`08_blue_leds_asyncio.py`](08_blue_leds_asyncio.py) | All six blue LEDs in separate `asyncio` tasks | GPIO 26, 14, 27, 25, 33, 12 |
| 9 | [`09_blue_interval_buttons.py`](09_blue_interval_buttons.py) | Two blue interval buttons and external pull-downs | GPIO 34 / GPIO 35 |
| 10 | [`10_status_leds_basic.py`](10_status_leds_basic.py) | Orange and yellow status-LED wiring | GPIO 13 / GPIO 2 |
| 11 | [`11_ram_oled_basic.py`](11_ram_oled_basic.py) | RAM OLED: independent I2C scan and label | `I2C(1)`, SCL 15, SDA 22, `0x3C` |
| 12 | [`12_tft_basic.py`](12_tft_basic.py) | TFT initialization and solid-color fills | `SPI(2)`, SCK 18, MOSI 23, CS 5, D/C 21, RST 19 |
| 13 | [`13_tft_text_diagnostic.py`](13_tft_text_diagnostic.py) | TFT text, console colors and row wrapping | Same TFT pins as test 12 |

## Recommended sequence

For a short current-hardware check, run tests 4, 5, 8, 9, 10, 11 and 12.
Together they exercise every GPIO used by `main.py`. Run tests 1–3, 6, 7 and
13 only when the broader check identifies a problem that needs to be isolated.

Dependencies:

- Run test 2 after test 1 and test 3 after test 2.
- Run test 6 after test 5.
- Run test 8 after tests 3 and 7.
- Run test 13 after test 12.

The slide switch on GPIO 0 belongs to the ROM flashing path rather than
`main.py`; verify it during an actual flashing attempt, not with a MicroPython
test script.

## How to run a test on Wokwi

1. Keep a copy of the repository's real `main.py` open locally.
2. Replace the online `main.py` temporarily with one test script.
3. Start the simulation and compare the behavior with the script's `Expected`
   section.
4. Restore the real `main.py` before running the application.

## Hardware notes

- GPIO 17 uses the ESP32's internal `Pin.PULL_DOWN` for the green button.
- GPIO 34 and GPIO 35 have no internal pull resistors; each blue interval
  button requires its external 10 kOhm pull-down from `diagram.json`.
- The orange LED test checks only GPIO 13 wiring. In `main.py`, ON means the
  display buses are idle and OFF marks an instrumented display write.
- The yellow LED test checks only GPIO 2 wiring. Its behavior in `main.py` is a
  scheduler-throughput visualization, not a literal idle-priority signal.
- Test 11 checks the RAM OLED's `I2C(1)` bus in isolation; it does not prove
  concurrent operation with the CPU OLED.
- Tests 1, 2, 4, 7, 9 and 10 intentionally use simple blocking loops so that
  they isolate wiring from the application's cooperative scheduler.
