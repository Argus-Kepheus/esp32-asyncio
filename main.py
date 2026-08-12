"""
CESS-UFF - ESP32 MicroPython Practical Assessment
Courses: Instrumentation / Electronics / Programming Logic

Controls two LEDs and updates an SSD1306 OLED display based on the state
of a push button. Cooperative asyncio tasks prevent timing delays from
blocking the complete application and keep the red LED blinking
independently from the button-monitoring logic.

See docs/EN/technical-specification.md for the full requirements and the
rationale behind every decision below.
"""

import asyncio
import time
from machine import Pin, I2C

from ssd1306 import SSD1306_I2C

# --- Pin assignments (mandatory project requirements) -----------------------
RED_LED_PIN = 2
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SCL_PIN = 25
OLED_SDA_PIN = 16

# --- Timing configuration ----------------------------------------------------
RED_LED_BLINK_INTERVAL_MS = 500
BUTTON_SAMPLE_INTERVAL_MS = 5
# Wokwi's simulated push-button is bounce-free, so this debounce window is
# not required to pass the simulation. It is kept because it is the correct
# behavior for a real, physical button (see docs, "Debounce strategy").
BUTTON_DEBOUNCE_MS = 30

# --- Display configuration ----------------------------------------------------
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDRESS = 0x3C
OLED_I2C_FREQUENCY_HZ = 400_000
MSG_RELEASED = "Boa sorte!"  # shown while the button is released
MSG_PRESSED = "Consegui"     # shown while the button is pressed

# --- Peripheral setup ----------------------------------------------------
red_led = Pin(RED_LED_PIN, Pin.OUT, value=0)
green_led = Pin(GREEN_LED_PIN, Pin.OUT, value=0)

# Internal pull-down: the pin reads LOW when idle and HIGH when pressed,
# as required by the specification. No external resistor is used.
push_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)

# Hardware I2C bus 0, on the mandatory OLED pins. Confirmed working on
# Wokwi's simulated ESP32 by tests/05_oled_basic.py and
# tests/06_oled_full_diagnostic.py (see docs/EN/technical-specification.md,
# section 16) -- an earlier revision used machine.SoftI2C as an
# unconfirmed defensive compatibility choice; that is no longer needed.
i2c = I2C(
    0,
    scl=Pin(OLED_SCL_PIN),
    sda=Pin(OLED_SDA_PIN),
    freq=OLED_I2C_FREQUENCY_HZ,
)


def create_oled_display():
    """Initialize the OLED if it is detected on the I2C bus, else return None.

    Returning ``None`` on failure lets the LED and button functions remain
    operational while reporting a clear diagnostic, instead of crashing the
    whole program on a wiring mistake.
    """
    detected_addresses = i2c.scan()
    if OLED_I2C_ADDRESS not in detected_addresses:
        print(
            "OLED initialization failed: expected I2C address 0x{:02X}, "
            "detected {}".format(
                OLED_I2C_ADDRESS,
                ["0x{:02X}".format(address) for address in detected_addresses],
            )
        )
        return None

    return SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_I2C_ADDRESS)


oled_display = create_oled_display()


def draw_centered_message(message):
    """Clear the screen and draw a single line of text, centered."""
    if oled_display is None:
        return

    character_width = 8
    character_height = 8
    x_position = max(0, (OLED_WIDTH - len(message) * character_width) // 2)
    y_position = (OLED_HEIGHT - character_height) // 2

    oled_display.fill(0)
    oled_display.text(message, x_position, y_position, 1)
    oled_display.show()


def apply_button_state(is_pressed):
    """Update the green LED and OLED for a stable button state.

    Called only at startup and after a debounced state transition, so the
    OLED is never redrawn on every poll cycle (avoids flicker and redundant
    I2C traffic).
    """
    green_led.value(1 if is_pressed else 0)
    message = MSG_PRESSED if is_pressed else MSG_RELEASED
    draw_centered_message(message)
    print("Button: {} | Green LED: {} | OLED: {}".format(
        "pressed" if is_pressed else "released",
        "ON" if is_pressed else "OFF",
        message,
    ))


async def blink_red_led():
    """Toggle the red LED every 500 ms, independent of every other task."""
    while True:
        red_led.value(not red_led.value())
        await asyncio.sleep_ms(RED_LED_BLINK_INTERVAL_MS)


async def monitor_button(initial_state):
    """Sample, debounce and react to the push-button state."""
    stable_state = initial_state
    candidate_state = initial_state
    candidate_since = time.ticks_ms()

    while True:
        raw_state = bool(push_button.value())
        now = time.ticks_ms()

        if raw_state != candidate_state:
            candidate_state = raw_state
            candidate_since = now
        elif (
            candidate_state != stable_state
            and time.ticks_diff(now, candidate_since) >= BUTTON_DEBOUNCE_MS
        ):
            stable_state = candidate_state
            apply_button_state(stable_state)

        await asyncio.sleep_ms(BUTTON_SAMPLE_INTERVAL_MS)


async def main():
    initial_button_state = bool(push_button.value())
    apply_button_state(initial_button_state)

    asyncio.create_task(blink_red_led())
    await monitor_button(initial_button_state)


try:
    asyncio.run(main())
finally:
    # Leave outputs in a predictable safe state after an exception or stop.
    red_led.off()
    green_led.off()
