"""Test 2/13 — First blue LED, toggle-loop blink (GPIO 26).

Same circuit as test 1, but using the toggle idiom
(`value(not value())`) that the real main.py uses for each blue LED task —
this is the step that actually validates the blink pattern main.py
depends on, not just that the GPIO can be driven. See tests/README.md for
how to run this on wokwi.com.

Deliberately uses a plain blocking loop (no asyncio, no ssd1306 import,
no button) so a failure here can only mean a GPIO/wiring/board issue, not
an application-logic issue.

Expected: the blue LED toggles every 500 ms, continuously.
"""

from machine import Pin
import time

BLUE_LED_1_PIN = 26
BLINK_INTERVAL_MS = 500

blue_led_1 = Pin(BLUE_LED_1_PIN, Pin.OUT, value=0)

print("Blue LED blink test starting on GPIO {}".format(BLUE_LED_1_PIN))

while True:
    blue_led_1.value(not blue_led_1.value())
    print("Blue LED:", "ON" if blue_led_1.value() else "OFF")
    time.sleep_ms(BLINK_INTERVAL_MS)
