"""Test 3/13 — First blue LED, blinking via asyncio (GPIO 26).

Same circuit and toggle idiom as test 2, but now wrapped exactly the way
main.py runs it: an `async def` coroutine scheduled with
`asyncio.create_task()` inside `asyncio.run()`, using
`await asyncio.sleep_ms()` instead of a blocking `time.sleep_ms()`. See
tests/README.md for how to run this on wokwi.com.

This isolates `import asyncio` and the asyncio event loop itself from the
GPIO/wiring already checked by tests 1-2.

Expected: identical behavior to test 2 -- the blue LED toggles every
500 ms, continuously -- but driven by an asyncio task instead of a plain
loop.
"""

import asyncio
from machine import Pin

BLUE_LED_1_PIN = 26
BLINK_INTERVAL_MS = 500

blue_led = Pin(BLUE_LED_1_PIN, Pin.OUT, value=0)


async def blink_blue_led():
    while True:
        blue_led.value(not blue_led.value())
        print("Blue LED:", "ON" if blue_led.value() else "OFF")
        await asyncio.sleep_ms(BLINK_INTERVAL_MS)


async def main():
    print("Blue LED asyncio test starting on GPIO {}".format(BLUE_LED_1_PIN))
    asyncio.create_task(blink_blue_led())
    while True:
        await asyncio.sleep(3600)


try:
    asyncio.run(main())
finally:
    blue_led.off()
