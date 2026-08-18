"""Test 1/13 — First blue LED, basic on/off (GPIO 26).

The simplest possible check: prove the first blue LED circuit and GPIO 26 wiring
work at all, with explicit on()/off() calls (no toggle logic, no state
tracking). See tests/README.md for how to run this on wokwi.com.

Expected: the blue LED alternates ON/OFF every 500 ms; the serial monitor
prints the pin value on every transition.
"""

from machine import Pin
from time import sleep_ms

BLUE_LED_1_PIN = 26
BLINK_INTERVAL_MS = 500

blue_led = Pin(BLUE_LED_1_PIN, Pin.OUT)
blue_led.off()

print("GPIO26 blue LED test started")

while True:
    blue_led.on()
    print("GPIO26 =", blue_led.value(), "- blue LED ON")
    sleep_ms(BLINK_INTERVAL_MS)

    blue_led.off()
    print("GPIO26 =", blue_led.value(), "- blue LED OFF")
    sleep_ms(BLINK_INTERVAL_MS)
