"""Test 9/13 — Blue interval buttons, GPIO 34/35, external pull-down.

Isolates the two blue buttons that scale the blinking LEDs' interval:
decrease on GPIO 34, increase on GPIO 35. See tests/README.md for how to
run this on wokwi.com.

Unlike the main push-button (test 4, GPIO 17, internal Pin.PULL_DOWN),
GPIO 34/35 are input-only ESP32 pins with **no internal pull resistors at
all** -- Pin.PULL_DOWN is not requested here because the hardware can't
provide it. Each button needs its own external 10 kOhm pull-down resistor
to GND in diagram.json/the physical build; without it, the pin floats and
readings will be erratic rather than a clean LOW when released. If this
test's readings look noisy or stuck HIGH with nothing pressed, check the
external resistor first, before suspecting the button/GPIO itself.

Expected: with both buttons released, the serial monitor prints "released"
for each once at startup. Pressing decrease (GPIO 34) or increase
(GPIO 35) prints its own "pressed"/"released" transition, independently
of the other button.
"""

from machine import Pin
import time

POLL_INTERVAL_MS = 50
DECREASE_INTERVAL_BUTTON_PIN = 34
INCREASE_INTERVAL_BUTTON_PIN = 35

decrease_button = Pin(DECREASE_INTERVAL_BUTTON_PIN, Pin.IN)
increase_button = Pin(INCREASE_INTERVAL_BUTTON_PIN, Pin.IN)

print("Blue interval-button test started (decrease=GPIO34, increase=GPIO35)")

last_decrease = None
last_increase = None

while True:
    decrease_state = bool(decrease_button.value())
    if decrease_state != last_decrease:
        print("Decrease (GPIO34):", "pressed" if decrease_state else "released")
        last_decrease = decrease_state

    increase_state = bool(increase_button.value())
    if increase_state != last_increase:
        print("Increase (GPIO35):", "pressed" if increase_state else "released")
        last_increase = increase_state

    time.sleep_ms(POLL_INTERVAL_MS)
