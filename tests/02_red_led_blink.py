"""Test 2/5 — Red LED, toggle-loop blink (GPIO 2).

Same circuit as test 1, but using the toggle idiom
(`value(not value())`) that the real main.py uses for the red LED task —
this is the step that actually validates the blink pattern main.py
depends on, not just that the GPIO can be driven. See tests/README.md for
how to run this on wokwi.com.

Deliberately uses a plain blocking loop (no asyncio, no ssd1306 import,
no button) so a failure here can only mean a GPIO/wiring/board issue, not
an application-logic issue.

Expected: the red LED toggles every 500 ms, continuously.
"""

from machine import Pin
import time

RED_LED_PIN = 2
BLINK_INTERVAL_MS = 500

red_led = Pin(RED_LED_PIN, Pin.OUT, value=0)

print("Red LED blink test starting on GPIO {}".format(RED_LED_PIN))

while True:
    red_led.value(not red_led.value())
    print("Red LED:", "ON" if red_led.value() else "OFF")
    time.sleep_ms(BLINK_INTERVAL_MS)
