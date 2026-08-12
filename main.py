"""
CESS-UFF - ESP32 MicroPython Practical Assessment
Courses: Instrumentation / Electronics / Programming Logic

Controls seven LEDs (six blinking at independent frequencies, one driven by
a push button) and updates two displays -- an SSD1306 OLED over I2C and an
ILI9341 TFT over 4-wire SPI -- based on the button state. Cooperative
asyncio tasks prevent timing delays from blocking the complete application
and keep every LED blinking independently of the others and of the
button-monitoring logic.

See docs/EN/technical-specification.md for the full requirements and the
rationale behind every decision below.
"""

import asyncio
import time
from machine import Pin, I2C, SPI

from ssd1306 import SSD1306_I2C
from ili9341 import ILI9341

# --- Pin assignments (mandatory project requirements) -----------------------
# NOTE: RED_LED_PIN and OLED_SCL_PIN were moved off their original fixed
# pins (GPIO 2 and GPIO 25) at the user's explicit request, for board layout.
RED_LED_PIN = 26
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SCL_PIN = 32
OLED_SDA_PIN = 16

# --- Pin assignments (extra blinking LEDs, different frequencies) -----------
# GPIO 34/35 are input-only on the ESP32 (no output driver) and cannot be
# used here. GPIO 12 (RED_LED_2_PIN) is a strapping pin (sets flash voltage
# at boot) -- safe here because this LED only ever sinks current to GND
# through a resistor, it never pulls the pin toward 3V3 during boot.
BLUE_LED_PIN = 14
YELLOW_LED_PIN = 27
WHITE_LED_PIN = 25
ORANGE_LED_PIN = 33
RED_LED_2_PIN = 12

# --- Pin assignments (4-wire SPI TFT: SCK, MOSI, CS, D/C) -------------------
TFT_SCK_PIN = 18
TFT_MOSI_PIN = 23
TFT_CS_PIN = 5
TFT_DC_PIN = 21
TFT_RST_PIN = 19

# --- Timing configuration ----------------------------------------------------
# Each blinking LED's interval is half the previous one, from 4 s down to
# 125 ms: RED_LED_2 -> BLUE -> YELLOW -> RED -> WHITE -> ORANGE.
RED_LED_2_BLINK_INTERVAL_MS = 4000
BLUE_LED_BLINK_INTERVAL_MS = 2000
YELLOW_LED_BLINK_INTERVAL_MS = 1000
RED_LED_BLINK_INTERVAL_MS = 500
WHITE_LED_BLINK_INTERVAL_MS = 250
ORANGE_LED_BLINK_INTERVAL_MS = 125
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
blue_led = Pin(BLUE_LED_PIN, Pin.OUT, value=0)
yellow_led = Pin(YELLOW_LED_PIN, Pin.OUT, value=0)
white_led = Pin(WHITE_LED_PIN, Pin.OUT, value=0)
orange_led = Pin(ORANGE_LED_PIN, Pin.OUT, value=0)
red_led_2 = Pin(RED_LED_2_PIN, Pin.OUT, value=0)

# Every LED that blinks on a fixed interval, paired with that interval, so
# main() can launch one independent asyncio task per LED from a single loop
# instead of one hand-written coroutine per LED.
BLINKING_LEDS = (
    (red_led, RED_LED_BLINK_INTERVAL_MS),
    (blue_led, BLUE_LED_BLINK_INTERVAL_MS),
    (yellow_led, YELLOW_LED_BLINK_INTERVAL_MS),
    (white_led, WHITE_LED_BLINK_INTERVAL_MS),
    (orange_led, ORANGE_LED_BLINK_INTERVAL_MS),
    (red_led_2, RED_LED_2_BLINK_INTERVAL_MS),
)

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

# 4-wire SPI TFT (SCK, MOSI, CS, D/C), independent of the I2C OLED above --
# both displays run at the same time, on separate buses/pins.
tft_spi = SPI(2, baudrate=20_000_000, sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))


def create_tft_display():
    """Initialize the SPI TFT, or return None if it fails to respond.

    Same graceful-degradation shape as create_oled_display(): a wiring
    mistake on the TFT must not take down the LEDs, button or OLED.
    """
    try:
        return ILI9341(
            tft_spi,
            cs=Pin(TFT_CS_PIN, Pin.OUT, value=1),
            dc=Pin(TFT_DC_PIN, Pin.OUT, value=0),
            rst=Pin(TFT_RST_PIN, Pin.OUT, value=1),
        )
    except OSError as error:
        print("TFT initialization failed:", error)
        return None


tft_display = create_tft_display()

# RGB565 colors, one per entry in BLINKING_LEDS, in the same order.
BLINKING_LED_COLORS565 = (0xF800, 0x001F, 0xFFE0, 0xFFFF, 0xFD20, 0x7800)


def draw_frequency_legend():
    """Draw one color bar per blinking LED, ordered top-to-bottom to match
    BLINKING_LEDS -- a static legend, drawn once at startup like the OLED's
    initial message, not redrawn on a timer.
    """
    if tft_display is None:
        return

    bar_height = tft_display.height // len(BLINKING_LEDS)
    for index, color565 in enumerate(BLINKING_LED_COLORS565):
        tft_display.fill_rect(0, index * bar_height, tft_display.width, bar_height, color565)


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


async def blink_led(led, interval_ms):
    """Toggle one LED at its own fixed interval, independent of every other
    task -- one call per entry in BLINKING_LEDS gives each LED its own
    frequency without blocking, or being blocked by, any other LED."""
    while True:
        led.value(not led.value())
        await asyncio.sleep_ms(interval_ms)


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
    draw_frequency_legend()

    for led, interval_ms in BLINKING_LEDS:
        asyncio.create_task(blink_led(led, interval_ms))
    await monitor_button(initial_button_state)


try:
    asyncio.run(main())
finally:
    # Leave outputs in a predictable safe state after an exception or stop.
    red_led.off()
    green_led.off()
    blue_led.off()
    yellow_led.off()
    white_led.off()
    orange_led.off()
    red_led_2.off()
