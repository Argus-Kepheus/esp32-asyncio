"""Test 8/13 — All six blinking LEDs, concurrently, via asyncio.

Integration step for the LED side of the project: red (GPIO 26), blue
(GPIO 14), yellow (GPIO 27), white (GPIO 25), orange (GPIO 33) and a
second red (GPIO 12) all blinking at the same 500 ms interval, each as
its own independent asyncio task -- exactly the pattern main.py uses
(BLINKING_LEDS / blink_led()). See tests/README.md for how to run this on
wokwi.com.

Run this only after test 1-3 (red LED + asyncio) and test 7 (the other
five LEDs' wiring) have each passed on their own. If every LED blinked
correctly alone in test 7 but one stalls, lags, or stops here, the fault
is in concurrency (one task blocking the others), not in that LED's GPIO
wiring -- exactly the kind of bug this project's asyncio design exists to
prevent (see docs/EN/technical-specification.md, section 7).

Expected: all six LEDs blink continuously and independently, toggling
every 500 ms, with no visible stall, drift, or timing glitch in any one
of them relative to the others.
"""

import asyncio
from machine import Pin

BLINK_INTERVAL_MS = 500

LEDS = (
    ("red", 26),
    ("blue", 14),
    ("yellow", 27),
    ("white", 25),
    ("orange", 33),
    ("red 2", 12),
)

leds = [(name, Pin(pin_number, Pin.OUT, value=0)) for name, pin_number in LEDS]


async def blink_led(name, led):
    while True:
        led.value(not led.value())
        print("{}: {}".format(name, "ON" if led.value() else "OFF"))
        await asyncio.sleep_ms(BLINK_INTERVAL_MS)


async def main():
    print("Blinking-LEDs asyncio test starting -- 6 independent tasks:")
    for name, pin_number in LEDS:
        print("  {} -> GPIO {}".format(name, pin_number))

    for name, led in leds:
        asyncio.create_task(blink_led(name, led))

    while True:
        await asyncio.sleep(3600)


try:
    asyncio.run(main())
finally:
    for _, led in leds:
        led.off()
