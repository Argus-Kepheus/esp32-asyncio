"""Test 7/13 — Five additional blue LEDs, checked one at a time.

Isolates blue LEDs 2-6 on GPIO 14, 27, 25, 33 and 12. All six blinking
LEDs in the current circuit are physically blue; the first one, on GPIO
26, is checked by tests 1-3. See tests/README.md for how to run this on
wokwi.com.

Deliberately lights exactly one LED at a time, in a plain blocking loop
(no asyncio) -- if only one LED in the row fails to light, the printed
name pinpoints exactly which pin/resistor/LED to check, instead of five
LEDs blinking together and leaving you to guess which one is silently
broken.

Expected: the five blue LEDs light up one after another, in the order printed
on the serial monitor, each for 500 ms, looping continuously.
"""

from machine import Pin
from time import sleep_ms

LED_STEP_INTERVAL_MS = 500

BLUE_LEDS = (
    ("blue 2", 14),
    ("blue 3", 27),
    ("blue 4", 25),
    ("blue 5", 33),
    ("blue 6", 12),
)

blue_leds = [(name, Pin(pin_number, Pin.OUT, value=0)) for name, pin_number in BLUE_LEDS]

print("Additional blue LEDs test started -- lighting one at a time:")
for name, pin_number in BLUE_LEDS:
    print("  {} -> GPIO {}".format(name, pin_number))

while True:
    for name, led in blue_leds:
        led.on()
        print("ON:", name)
        sleep_ms(LED_STEP_INTERVAL_MS)
        led.off()
