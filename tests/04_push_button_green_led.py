"""Test 4/6 — Push-button (GPIO 17) driving the green LED (GPIO 4).

Isolates the digital input side of the project: the push-button and the
green LED it directly drives. See tests/README.md for how to run this on
wokwi.com.

Deliberately uses a plain blocking loop (no asyncio, no ssd1306 import,
no red LED, no debounce) so a failure here can only mean a GPIO/wiring
problem with the button or the green LED, not an application-logic issue.
Wokwi's simulated push-button does not bounce, so debounce is not needed
for this isolated hardware check (see docs/EN/technical-specification.md,
section 6.2).

Expected: button released -> green LED OFF, console prints
"Button: released". Button pressed (click it, or focus the diagram and
hold Space) -> green LED ON, console prints "Button: pressed".
"""

from machine import Pin
import time

GREEN_LED_PIN = 4
BUTTON_PIN = 17
POLL_INTERVAL_MS = 100

green_led = Pin(GREEN_LED_PIN, Pin.OUT, value=0)
push_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)

print("Push-button test starting on GPIO {} (green LED on GPIO {})".format(
    BUTTON_PIN, GREEN_LED_PIN
))

last_state = None

while True:
    current_state = bool(push_button.value())
    if current_state != last_state:
        green_led.value(current_state)
        print("Button:", "pressed" if current_state else "released")
        last_state = current_state
    time.sleep_ms(POLL_INTERVAL_MS)
