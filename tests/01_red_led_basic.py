"""Test 1/5 — Red LED, basic on/off (GPIO 2).

The simplest possible check: prove the red LED circuit and GPIO 2 wiring
work at all, with explicit on()/off() calls (no toggle logic, no state
tracking). See tests/README.md for how to run this on wokwi.com.

Expected: the red LED alternates ON/OFF every 500 ms; the serial monitor
prints the pin value on every transition.
"""

from machine import Pin
from time import sleep_ms

RED_LED_PIN = 2
BLINK_INTERVAL_MS = 500

red_led = Pin(RED_LED_PIN, Pin.OUT)
red_led.off()

print("GPIO2 red LED test started")

while True:
    red_led.on()
    print("GPIO2 =", red_led.value(), "- LED ON")
    sleep_ms(BLINK_INTERVAL_MS)

    red_led.off()
    print("GPIO2 =", red_led.value(), "- LED OFF")
    sleep_ms(BLINK_INTERVAL_MS)
