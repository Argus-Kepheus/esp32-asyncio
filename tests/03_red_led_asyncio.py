"""Test 3/6 — Red LED, blinking via asyncio (GPIO 2).

Same circuit and toggle idiom as test 2, but now wrapped exactly the way
main.py runs it: an `async def` coroutine scheduled with
`asyncio.create_task()` inside `asyncio.run()`, using
`await asyncio.sleep_ms()` instead of a blocking `time.sleep_ms()`. See
tests/README.md for how to run this on wokwi.com.

This isolates `import asyncio` and the asyncio event loop itself as a
variable, separate from the GPIO/wiring already confirmed by tests 1-2.
If tests 1-2 pass but this one does not, the fault is in asyncio /
firmware support for it, not in the LED circuit -- this was one of the
suspected (but previously untested in isolation) causes behind the
boot-loop bug documented in docs/EN/technical-specification.md, section 16.

Expected: identical behavior to test 2 -- the red LED toggles every
500 ms, continuously -- but driven by an asyncio task instead of a plain
loop.
"""

import asyncio
from machine import Pin

RED_LED_PIN = 2
BLINK_INTERVAL_MS = 500

red_led = Pin(RED_LED_PIN, Pin.OUT, value=0)


async def blink_red_led():
    while True:
        red_led.value(not red_led.value())
        print("Red LED:", "ON" if red_led.value() else "OFF")
        await asyncio.sleep_ms(BLINK_INTERVAL_MS)


async def main():
    print("Red LED asyncio test starting on GPIO {}".format(RED_LED_PIN))
    asyncio.create_task(blink_red_led())
    while True:
        await asyncio.sleep(3600)


try:
    asyncio.run(main())
finally:
    red_led.off()
