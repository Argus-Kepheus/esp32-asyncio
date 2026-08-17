"""Test 7/14 — Five extra LEDs, basic wiring check (one at a time).

Isolates the five LEDs added after the original red/green pair: blue
(GPIO 14), yellow (GPIO 27), white (GPIO 25), orange (GPIO 33) and a
second red (GPIO 12). See tests/README.md for how to run this on
wokwi.com.

Deliberately lights exactly one LED at a time, in a plain blocking loop
(no asyncio) -- if only one LED in the row fails to light, the printed
name pinpoints exactly which pin/resistor/LED to check, instead of five
LEDs blinking together and leaving you to guess which one is silently
broken.

Expected: the five LEDs light up one after another, in the order printed
on the serial monitor, each for 500 ms, looping continuously.
"""

from machine import Pin
from time import sleep_ms

LED_STEP_INTERVAL_MS = 500

LEDS = (
    ("blue", 14),
    ("yellow", 27),
    ("white", 25),
    ("orange", 33),
    ("red 2", 12),
)

pins = [(name, Pin(pin_number, Pin.OUT, value=0)) for name, pin_number in LEDS]

print("Extra LEDs basic test started -- lighting one at a time:")
for name, pin_number in LEDS:
    print("  {} -> GPIO {}".format(name, pin_number))

while True:
    for name, led in pins:
        led.on()
        print("ON:", name)
        sleep_ms(LED_STEP_INTERVAL_MS)
        led.off()
