# Hardware diagnostic tests

Thirteen standalone scripts to validate each piece of the circuit — and
the `asyncio` mechanism `main.py` is built on — in isolation, in
increasing order of complexity, **before** trying the full `main.py`.
None of these are part of the graded deliverable — they exist to make
physical assembly and debugging tractable: build and test one piece of
hardware at a time, confirm it works on its own, then move to the next.
If a full-application symptom shows up later (e.g. "nothing works"), run
the matching isolated test here first to narrow the fault down to a
specific GPIO/component/mechanism instead of guessing across the whole
circuit and task set at once.

## Order

| # | File | Validates | Depends on |
|---|---|---|---|
| 1 | [`01_red_led_basic.py`](01_red_led_basic.py) | Red LED wiring, GPIO 26, on/off polarity | Nothing else |
| 2 | [`02_red_led_blink.py`](02_red_led_blink.py) | Same circuit, using the toggle idiom `main.py` actually uses for the blink task | Test 1 passing |
| 3 | [`03_red_led_asyncio.py`](03_red_led_asyncio.py) | Same toggle idiom, but wrapped in `import asyncio` + `asyncio.create_task()` + `asyncio.run()`, exactly like `main.py` | Test 2 passing |
| 4 | [`04_push_button_green_led.py`](04_push_button_green_led.py) | Push-button (GPIO 17) and green LED (GPIO 4) wiring, active-HIGH, internal pull-down | Independent of 1–3 |
| 5 | [`05_oled_basic.py`](05_oled_basic.py) | First OLED's I2C wiring (GPIO 32/16), address `0x3C`, one static message | Independent of 1–4 |
| 6 | [`06_oled_full_diagnostic.py`](06_oled_full_diagnostic.py) | Every `ssd1306.py` drawing primitive: pixels, lines, shapes, text, invert, contrast, power on/off, scrolling | Test 5 passing |
| 7 | [`07_extra_leds_basic.py`](07_extra_leds_basic.py) | The five other blinking LEDs' wiring: blue (14), yellow (27), white (25), orange (33), red 2 (12) — one at a time | Independent of 1–6 |
| 8 | [`08_blinking_leds_asyncio.py`](08_blinking_leds_asyncio.py) | All six blinking LEDs (test 1–3's red plus test 7's five) running concurrently as independent asyncio tasks, exactly like `BLINKING_LEDS` in `main.py` | Tests 3 and 7 passing |
| 9 | [`09_speed_buttons.py`](09_speed_buttons.py) | Speed step-buttons, GPIO 34/35, **external** pull-down (unlike test 4's internal one) | Independent of 1–8 |
| 10 | [`10_idle_leds_basic.py`](10_idle_leds_basic.py) | Idle-indicator LEDs' wiring: bus-busy orange (GPIO 13), scheduler yellow (GPIO 2) | Independent of 1–9 |
| 11 | [`11_oled2_basic.py`](11_oled2_basic.py) | Second OLED's own I2C bus (`I2C(1)`, GPIO 15/22), independent of the first OLED's bus | Independent of 1–10 |
| 12 | [`12_tft_basic.py`](12_tft_basic.py) | TFT's 4-wire SPI wiring (SCK 18, MOSI 23, CS 5, D/C 21) and reset line (RST 19): panel init + solid-color fills | Independent of 1–11 |
| 13 | [`13_tft_text_diagnostic.py`](13_tft_text_diagnostic.py) | `ili9341.py`'s `text()` — the primitive `main.py`'s TFT log console is built on — across every console color, plus row-wrapping | Test 12 passing |

If you only have time for a smoke test, running 3, 4, 5, 9, 11 and 12
covers every GPIO the project uses plus the `asyncio` mechanism with the
least effort; run 6, 8, 10, or 13 when you specifically need to debug
that subsystem.

Test 3 exists specifically because `import asyncio` was one of the
suspected — but, until this test existed, never isolated — causes behind
a boot-loop bug found while validating this project (see
`docs/EN/technical-specification.md`, §16 decision log). Tests 1–2 alone
cannot rule asyncio in or out, since they never import it.

## How to run one of these on wokwi.com

1. Open the project and keep the repository's real `main.py` open
   elsewhere (you are about to overwrite the online copy).
2. Replace the online `main.py`'s content with the test file's content.
3. Start the simulation and compare the behavior against the file's own
   docstring (each script documents its expected result and, where
   relevant, how to trigger it — e.g. pressing a button).
4. Restore the real `main.py` before continuing with the rest of the
   project.

## Notes

- Tests 1, 2, 4, 7, 9 and 10 deliberately use a plain blocking loop (no
  `asyncio`, no `ssd1306`/`ili9341` import where not needed) so a failure
  can only mean a GPIO/wiring/board problem, not an application-logic
  bug. Tests 3 and 8 are the exceptions — they exist specifically to
  bring `asyncio` and multi-task concurrency in as the one new variable,
  once the plain-loop tests have already confirmed the GPIO/wiring is
  fine on its own.
- Tests 5, 6 and 11 use the hardware `machine.I2C` peripheral. `main.py`
  used to defensively use `machine.SoftI2C` instead, but tests 5 and 6
  passing on wokwi.com confirmed hardware I2C works fine, so `main.py`
  has since been reverted to hardware `I2C` too (see
  `docs/EN/technical-specification.md`, §16 decision log). Test 11 uses a
  second, independent hardware I2C bus (`I2C(1)`) for the second OLED, so
  it can be wired and run at the same time as the first OLED without bus
  contention.
- Wokwi's simulated push-button does not bounce, so test 4 has no
  debounce logic — that is intentional, not an oversight (see
  `docs/EN/technical-specification.md`, §6.2).
- Test 9's two buttons are wired differently from test 4's: GPIO 34/35
  are input-only ESP32 pins with no internal pull resistors at all, so
  each one needs its own external 10 kOhm pull-down resistor to GND
  (already in `diagram.json`). If test 9's readings look noisy or stuck
  HIGH with nothing pressed, suspect that external resistor first.
- Test 10's `scheduler_idle_led` sits on GPIO 2, a boot-strapping pin.
  That only matters at reset, before any script runs, and only if
  something forces an external level on the pin during boot; this LED
  only ever sinks current to GND through its resistor once GPIO 2 is
  already configured as an output, so it does not interfere with boot
  (same reasoning as the original red LED's GPIO 2 assignment, before it
  moved to GPIO 26 -- see `docs/EN/technical-specification.md`, §16).
- There is no numbered test for the flash-mode slide switch (GPIO 0): it
  is read by the ESP32's ROM bootloader before any MicroPython script
  runs, so no script can exercise it. It is verified simply by using it
  during a real flashing attempt.
