"""Test 11/14 — Second OLED basic check: its own I2C bus, I2C scan + text.

Isolates main.py's second OLED (oled_display_2): its own independent
hardware I2C bus, machine.I2C(1), on GPIO 15 (SCL) / GPIO 22 (SDA) --
deliberately a different bus instance than the first OLED's I2C(0) (test
5, GPIO 32/16), so both can be wired and addressed at the same time
without contention. See tests/README.md for how to run this on wokwi.com.

Run this independently of test 5 -- a failure here says nothing about the
first OLED, and vice versa, since they are on entirely separate buses.
This script only initializes I2C(1) alone, though: it does not open
I2C(0) at the same time, so passing this test does not confirm the two
buses actually work concurrently, the way main.py runs them together --
only that this bus works in isolation, same as test 5 for the other one.

Expected: the serial monitor lists 0x3C among the detected I2C devices on
bus 1, and this OLED shows "OLED 2 OK".
"""

from machine import I2C, Pin
import ssd1306

OLED2_SCL_PIN = 15
OLED2_SDA_PIN = 22
OLED_I2C_ADDRESS = 0x3C

i2c = I2C(
    1,
    scl=Pin(OLED2_SCL_PIN),
    sda=Pin(OLED2_SDA_PIN),
    freq=400_000,
)

detected_devices = i2c.scan()

print("I2C(1) devices:", detected_devices)

if OLED_I2C_ADDRESS not in detected_devices:
    raise RuntimeError("Second SSD1306 not detected at address 0x3C on I2C(1)")

oled_display_2 = ssd1306.SSD1306_I2C(
    128,
    64,
    i2c,
    addr=OLED_I2C_ADDRESS,
)

oled_display_2.fill(0)
oled_display_2.text("OLED 2 OK", 16, 28)
oled_display_2.show()

print("Second OLED test completed")
