"""Test 11/13 — RAM OLED basic check: its own I2C bus and text.

Isolates the current RAM OLED1 on its independent hardware I2C bus,
machine.I2C(1), on GPIO 15 (SCL) / GPIO 22 (SDA). This is deliberately a
different bus instance from CPU OLED0's I2C(0) (test 5, GPIO 32/16), so
both can be wired and addressed at the same time without contention. See
tests/README.md for how to run this on wokwi.com.

Run this independently of test 5 -- a failure here says nothing about the
CPU OLED0, and vice versa, since they are on entirely separate buses.
This script only initializes I2C(1) alone, though: it does not open
I2C(0) at the same time, so passing this test does not confirm the two
buses actually work concurrently, the way main.py runs them together --
only that this bus works in isolation, same as test 5 for the other one.

Expected: the serial monitor lists 0x3C among the detected I2C devices on
bus 1, and this OLED shows "RAM OLED OK".
"""

from machine import I2C, Pin
import ssd1306

OLED1_SCL_PIN = 15
OLED1_SDA_PIN = 22
RAM_OLED_I2C_ADDRESS = 0x3C

ram_i2c = I2C(
    1,
    scl=Pin(OLED1_SCL_PIN),
    sda=Pin(OLED1_SDA_PIN),
    freq=400_000,
)

detected_devices = ram_i2c.scan()

print("I2C(1) devices:", detected_devices)

if RAM_OLED_I2C_ADDRESS not in detected_devices:
    raise RuntimeError("RAM SSD1306 not detected at address 0x3C on I2C(1)")

ram_oled = ssd1306.SSD1306_I2C(
    128,
    64,
    ram_i2c,
    addr=RAM_OLED_I2C_ADDRESS,
)

ram_oled.fill(0)
ram_oled.text("RAM OLED OK", 16, 28)
ram_oled.show()

print("RAM OLED test completed")
