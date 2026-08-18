"""Test 8/13 — All six blue LEDs, concurrently, via asyncio.

Integration step for the blue-LED row: GPIO 26, 14, 27, 25, 33 and 12
all blinking at the same 500 ms interval, each as
its own independent asyncio task -- exactly the pattern main.py uses
(BLINKING_LEDS / blink_led()). See tests/README.md for how to run this on
wokwi.com.

Run this only after tests 1-3 (first blue LED + asyncio) and test 7 (the
other five blue LEDs) have each passed on their own. If every LED blinked
correctly alone in test 7 but one stalls, lags, or stops here, the fault
is in concurrency (one task blocking the others), not in that LED's GPIO
wiring -- exactly the kind of bug this project's asyncio design exists to
prevent (see docs/EN/technical-specification.md, section 7).

Expected: all six blue LEDs blink continuously as independent tasks,
toggling after waits of at least 500 ms. Small phase drift is possible
under the cooperative scheduler and is not a wiring failure.
"""

import asyncio
from machine import Pin

BLINK_INTERVAL_MS = 500

BLUE_LEDS = (
    ("blue 1", 26),
    ("blue 2", 14),
    ("blue 3", 27),
    ("blue 4", 25),
    ("blue 5", 33),
    ("blue 6", 12),
)

blue_leds = [(name, Pin(pin_number, Pin.OUT, value=0)) for name, pin_number in BLUE_LEDS]


async def blink_led(name, led):
    while True:
        led.value(not led.value())
        print("{}: {}".format(name, "ON" if led.value() else "OFF"))
        await asyncio.sleep_ms(BLINK_INTERVAL_MS)


async def main():
    print("Blinking-LEDs asyncio test starting -- 6 independent tasks:")
    for name, pin_number in BLUE_LEDS:
        print("  {} -> GPIO {}".format(name, pin_number))

    for name, led in blue_leds:
        asyncio.create_task(blink_led(name, led))

    while True:
        await asyncio.sleep(3600)


try:
    asyncio.run(main())
finally:
    for _, led in blue_leds:
        led.off()
