"""Test 6/6 — SSD1306 OLED full diagnostic suite.

The most complete check: exercises full-screen pixel activation, pixel
addressing, drawing primitives, text, inversion, contrast, display power
control, and framebuffer scrolling on the 128x64 SSD1306 OLED. See
tests/README.md for how to run this on wokwi.com.

Uses the same hardware machine.I2C peripheral as main.py (see
docs/EN/technical-specification.md, section 16 -- an earlier revision used
machine.SoftI2C defensively; this test's passing result on wokwi.com is
part of the evidence that confirmed hardware I2C works and made that
workaround unnecessary).

Requires the hline()/vline() methods on ssd1306.SSD1306, added
specifically to support this test (the upstream driver forwards them to
framebuf.FrameBuffer, which supports them natively).

Expected connections:
    GPIO 25 -> OLED SCL
    GPIO 16 -> OLED SDA
    3.3V    -> OLED VCC
    GND     -> OLED GND
"""

from machine import I2C, Pin
from time import sleep_ms
import ssd1306


# ---------------------------------------------------------------------------
# Hardware configuration
# ---------------------------------------------------------------------------

OLED_SCL_PIN = 25
OLED_SDA_PIN = 16
OLED_I2C_ADDRESS = 0x3C

OLED_WIDTH = 128
OLED_HEIGHT = 64

I2C_FREQUENCY_HZ = 400_000

STANDARD_TEST_DELAY_MS = 1500
SHORT_TEST_DELAY_MS = 700
PIXEL_SCAN_DELAY_MS = 20


# ---------------------------------------------------------------------------
# OLED initialization
# ---------------------------------------------------------------------------

i2c = I2C(
    0,
    scl=Pin(OLED_SCL_PIN),
    sda=Pin(OLED_SDA_PIN),
    freq=I2C_FREQUENCY_HZ,
)

detected_devices = i2c.scan()

print()
print("SSD1306 OLED diagnostic test")
print("----------------------------")
print("I2C devices detected:", detected_devices)

if OLED_I2C_ADDRESS not in detected_devices:
    raise RuntimeError(
        "SSD1306 not detected at I2C address 0x{:02X}".format(
            OLED_I2C_ADDRESS
        )
    )

oled_display = ssd1306.SSD1306_I2C(
    OLED_WIDTH,
    OLED_HEIGHT,
    i2c,
    addr=OLED_I2C_ADDRESS,
)

print(
    "SSD1306 detected at address 0x{:02X}".format(
        OLED_I2C_ADDRESS
    )
)
print("Display resolution: {}x{}".format(OLED_WIDTH, OLED_HEIGHT))


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clear_display():
    """Clear the framebuffer and update the OLED."""

    oled_display.fill(0)
    oled_display.show()


def show_test_title(line_1, line_2="", duration_ms=STANDARD_TEST_DELAY_MS):
    """Show a centered diagnostic title."""

    oled_display.fill(0)

    first_x = max(0, (OLED_WIDTH - len(line_1) * 8) // 2)
    oled_display.text(line_1, first_x, 20)

    if line_2:
        second_x = max(0, (OLED_WIDTH - len(line_2) * 8) // 2)
        oled_display.text(line_2, second_x, 36)

    oled_display.show()
    sleep_ms(duration_ms)


def announce_test(test_name):
    """Print the current test name to the serial monitor."""

    print()
    print("Running:", test_name)


# ---------------------------------------------------------------------------
# Diagnostic tests
# ---------------------------------------------------------------------------

def test_all_pixels():
    """
    Turn every pixel on and then off.

    A physical OLED should show a uniform illuminated screen followed by
    a completely dark screen.
    """

    announce_test("All pixels ON")
    oled_display.fill(1)
    oled_display.show()
    sleep_ms(2000)

    announce_test("All pixels OFF")
    oled_display.fill(0)
    oled_display.show()
    sleep_ms(1500)


def test_checkerboard_patterns():
    """
    Show two complementary one-pixel checkerboard patterns.

    Together, the two phases exercise both states at every pixel position.
    """

    for phase in (0, 1):
        announce_test("Checkerboard phase {}".format(phase + 1))

        oled_display.fill(0)

        for y in range(OLED_HEIGHT):
            for x in range(OLED_WIDTH):
                if ((x + y) & 1) == phase:
                    oled_display.pixel(x, y, 1)

        oled_display.show()
        sleep_ms(2000)


def test_horizontal_scan():
    """Move one illuminated horizontal line through all display rows."""

    announce_test("Horizontal pixel scan")

    for y in range(OLED_HEIGHT):
        oled_display.fill(0)
        oled_display.hline(0, y, OLED_WIDTH, 1)
        oled_display.show()
        sleep_ms(PIXEL_SCAN_DELAY_MS)

    sleep_ms(SHORT_TEST_DELAY_MS)


def test_vertical_scan():
    """Move one illuminated vertical line through all display columns."""

    announce_test("Vertical pixel scan")

    for x in range(OLED_WIDTH):
        oled_display.fill(0)
        oled_display.vline(x, 0, OLED_HEIGHT, 1)
        oled_display.show()
        sleep_ms(PIXEL_SCAN_DELAY_MS)

    sleep_ms(SHORT_TEST_DELAY_MS)


def test_grid():
    """Draw an eight-pixel grid and a border around the display."""

    announce_test("Grid and border")

    oled_display.fill(0)

    for x in range(0, OLED_WIDTH, 8):
        oled_display.vline(x, 0, OLED_HEIGHT, 1)

    for y in range(0, OLED_HEIGHT, 8):
        oled_display.hline(0, y, OLED_WIDTH, 1)

    oled_display.rect(
        0,
        0,
        OLED_WIDTH,
        OLED_HEIGHT,
        1,
    )

    oled_display.show()
    sleep_ms(2000)


def test_individual_pixels():
    """Draw pixels at corners, edges, center, and regular intervals."""

    announce_test("Individual pixels")

    oled_display.fill(0)

    test_points = (
        (0, 0),
        (OLED_WIDTH - 1, 0),
        (0, OLED_HEIGHT - 1),
        (OLED_WIDTH - 1, OLED_HEIGHT - 1),
        (OLED_WIDTH // 2, OLED_HEIGHT // 2),
        (OLED_WIDTH // 2 - 1, OLED_HEIGHT // 2),
        (OLED_WIDTH // 2, OLED_HEIGHT // 2 - 1),
        (OLED_WIDTH // 2 - 1, OLED_HEIGHT // 2 - 1),
    )

    for x, y in test_points:
        oled_display.pixel(x, y, 1)

    for x in range(4, OLED_WIDTH, 8):
        oled_display.pixel(x, 4, 1)
        oled_display.pixel(x, OLED_HEIGHT - 5, 1)

    for y in range(4, OLED_HEIGHT, 8):
        oled_display.pixel(4, y, 1)
        oled_display.pixel(OLED_WIDTH - 5, y, 1)

    oled_display.show()
    sleep_ms(2000)


def test_lines():
    """Draw horizontal, vertical, and diagonal lines."""

    announce_test("Line primitives")

    oled_display.fill(0)

    oled_display.hline(0, 0, OLED_WIDTH, 1)
    oled_display.hline(0, OLED_HEIGHT - 1, OLED_WIDTH, 1)

    oled_display.vline(0, 0, OLED_HEIGHT, 1)
    oled_display.vline(OLED_WIDTH - 1, 0, OLED_HEIGHT, 1)

    oled_display.line(
        0,
        0,
        OLED_WIDTH - 1,
        OLED_HEIGHT - 1,
        1,
    )

    oled_display.line(
        OLED_WIDTH - 1,
        0,
        0,
        OLED_HEIGHT - 1,
        1,
    )

    oled_display.hline(
        0,
        OLED_HEIGHT // 2,
        OLED_WIDTH,
        1,
    )

    oled_display.vline(
        OLED_WIDTH // 2,
        0,
        OLED_HEIGHT,
        1,
    )

    oled_display.show()
    sleep_ms(2000)


def test_rectangles():
    """Draw outlined and filled rectangles."""

    announce_test("Rectangle primitives")

    oled_display.fill(0)

    oled_display.rect(0, 0, 128, 64, 1)
    oled_display.rect(4, 4, 120, 56, 1)
    oled_display.rect(8, 8, 112, 48, 1)
    oled_display.rect(12, 12, 104, 40, 1)

    oled_display.fill_rect(18, 18, 25, 20, 1)
    oled_display.fill_rect(51, 18, 25, 20, 1)
    oled_display.fill_rect(84, 18, 25, 20, 1)

    oled_display.fill_rect(55, 22, 17, 12, 0)

    oled_display.show()
    sleep_ms(2000)


def test_text():
    """Test the built-in 8x8 framebuffer font."""

    announce_test("Text rendering")

    oled_display.fill(0)

    oled_display.text("SSD1306 TEST", 16, 0)
    oled_display.text("128 x 64 OLED", 8, 10)
    oled_display.text("GPIO25 SCL", 16, 20)
    oled_display.text("GPIO16 SDA", 16, 30)
    oled_display.text("0123456789", 24, 40)
    oled_display.text("AaZz !? @#", 20, 50)

    oled_display.show()
    sleep_ms(2500)


def test_inversion():
    """Test normal and inverted display modes."""

    announce_test("Normal and inverted modes")

    oled_display.fill(0)
    oled_display.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled_display.fill_rect(8, 8, 32, 20, 1)
    oled_display.text("INVERT", 55, 14)
    oled_display.text("NORMAL", 40, 42)
    oled_display.show()

    oled_display.invert(0)
    sleep_ms(1200)

    oled_display.invert(1)
    sleep_ms(1800)

    oled_display.invert(0)
    sleep_ms(800)


def test_contrast():
    """Test several SSD1306 contrast levels."""

    announce_test("Contrast control")

    oled_display.fill(0)
    oled_display.fill_rect(0, 0, OLED_WIDTH, 16, 1)
    oled_display.text("CONTRAST TEST", 12, 28)
    oled_display.rect(0, 48, OLED_WIDTH, 16, 1)
    oled_display.show()

    contrast_levels = (0, 16, 64, 128, 192, 255)

    for level in contrast_levels:
        print("Contrast level:", level)
        oled_display.contrast(level)
        sleep_ms(800)

    oled_display.contrast(255)
    sleep_ms(SHORT_TEST_DELAY_MS)


def test_power_control():
    """
    Test display power-off and power-on commands.

    The framebuffer contents should remain available after the panel is
    powered on again.
    """

    announce_test("Display power control")

    oled_display.fill(0)
    oled_display.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled_display.text("POWER TEST", 24, 20)
    oled_display.text("DISPLAY ON", 24, 36)
    oled_display.show()

    sleep_ms(1200)

    print("Display power OFF")
    oled_display.poweroff()
    sleep_ms(1500)

    print("Display power ON")
    oled_display.poweron()
    oled_display.show()
    sleep_ms(1500)


def test_scrolling():
    """Test horizontal framebuffer scrolling."""

    announce_test("Framebuffer scrolling")

    oled_display.fill(0)
    oled_display.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled_display.text("SCROLL TEST", 24, 12)
    oled_display.text(">>> MOVING >>>", 8, 32)
    oled_display.show()
    sleep_ms(800)

    for _ in range(36):
        oled_display.scroll(-2, 0)

        # Clear the newly exposed right-hand columns.
        oled_display.fill_rect(
            OLED_WIDTH - 2,
            0,
            2,
            OLED_HEIGHT,
            0,
        )

        oled_display.show()
        sleep_ms(60)

    sleep_ms(SHORT_TEST_DELAY_MS)


def show_completion_screen():
    """Show the final test result message."""

    announce_test("Diagnostic cycle completed")

    oled_display.invert(0)
    oled_display.contrast(255)
    oled_display.poweron()
    oled_display.fill(0)

    oled_display.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
    oled_display.text("OLED TEST", 32, 12)
    oled_display.text("COMPLETED", 28, 26)
    oled_display.text("I2C: 0x3C", 24, 42)

    oled_display.show()
    sleep_ms(3000)


# ---------------------------------------------------------------------------
# Main diagnostic cycle
# ---------------------------------------------------------------------------

def run_diagnostic_cycle():
    """Run one complete OLED diagnostic cycle."""

    show_test_title("SSD1306", "DIAGNOSTIC")

    test_all_pixels()
    test_checkerboard_patterns()
    test_horizontal_scan()
    test_vertical_scan()
    test_grid()
    test_individual_pixels()
    test_lines()
    test_rectangles()
    test_text()
    test_inversion()
    test_contrast()
    test_power_control()
    test_scrolling()

    show_completion_screen()


try:
    while True:
        run_diagnostic_cycle()

        clear_display()
        show_test_title(
            "RESTARTING",
            "TEST CYCLE",
            1200,
        )

except KeyboardInterrupt:
    oled_display.invert(0)
    oled_display.contrast(255)
    clear_display()
    print()
    print("OLED diagnostic test stopped")
