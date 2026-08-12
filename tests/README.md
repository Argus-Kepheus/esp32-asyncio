# Hardware diagnostic tests

Six standalone scripts to validate each piece of the circuit — and the
`asyncio` mechanism `main.py` is built on — in isolation, in increasing
order of complexity, **before** trying the full `main.py`. None of these
are part of the graded deliverable — they exist to make debugging
tractable: if a full-application symptom shows up (e.g. "nothing works"),
run the matching isolated test here first to narrow the fault down to a
specific GPIO/component/mechanism instead of guessing across the whole
circuit and task set at once.

## Order

| # | File | Validates | Depends on |
|---|---|---|---|
| 1 | [`01_red_led_basic.py`](01_red_led_basic.py) | Red LED wiring, GPIO 2, on/off polarity | Nothing else |
| 2 | [`02_red_led_blink.py`](02_red_led_blink.py) | Same circuit, using the toggle idiom `main.py` actually uses for the blink task | Test 1 passing |
| 3 | [`03_red_led_asyncio.py`](03_red_led_asyncio.py) | Same toggle idiom, but wrapped in `import asyncio` + `asyncio.create_task()` + `asyncio.run()`, exactly like `main.py` | Test 2 passing |
| 4 | [`04_push_button_green_led.py`](04_push_button_green_led.py) | Push-button (GPIO 17) and green LED (GPIO 4) wiring, active-HIGH behavior | Independent of 1–3 |
| 5 | [`05_oled_basic.py`](05_oled_basic.py) | OLED I2C wiring (GPIO 25/16), address `0x3C`, one static message | Independent of 1–4 |
| 6 | [`06_oled_full_diagnostic.py`](06_oled_full_diagnostic.py) | Every `ssd1306.py` drawing primitive: pixels, lines, shapes, text, invert, contrast, power on/off, scrolling | Test 5 passing |

If you only have time for a smoke test, running 3, 4, and 5 covers every
GPIO the project uses plus the `asyncio` mechanism with the least effort;
run 6 when you specifically need to debug OLED rendering.

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
   relevant, how to trigger it — e.g. pressing the button).
4. Restore the real `main.py` before continuing with the rest of the
   project.

## Notes

- Tests 1, 2 and 4 deliberately use a plain blocking loop (no `asyncio`,
  no `ssd1306` import where not needed) so a failure can only mean a
  GPIO/wiring/board problem, not an application-logic bug. Test 3 is the
  one exception — it exists specifically to bring `asyncio` in as the one
  new variable, once 1–2 have already confirmed the GPIO/wiring is fine.
- Tests 5 and 6 use the hardware `machine.I2C` peripheral. `main.py` used
  to defensively use `machine.SoftI2C` instead, but these two tests
  passing on wokwi.com confirmed hardware I2C works fine, so `main.py` has
  since been reverted to hardware `I2C` too (see
  `docs/EN/technical-specification.md`, §16 decision log).
- Wokwi's simulated push-button does not bounce, so test 4 has no
  debounce logic — that is intentional, not an oversight (see
  `docs/EN/technical-specification.md`, §6.2).
