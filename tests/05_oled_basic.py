"""Test 5/6 — OLED basic check: I2C scan + one static message.

The simplest possible OLED check: confirm the display answers on the I2C
bus at the expected address and can render one line of static text. See
tests/README.md for how to run this on wokwi.com.

Uses the same hardware machine.I2C peripheral as main.py (see
docs/EN/technical-specification.md, section 16 -- an earlier revision used
machine.SoftI2C defensively; this test's passing result on wokwi.com is
part of the evidence that confirmed hardware I2C works and made that
workaround unnecessary).

Expected: the serial monitor lists 0x3C among the detected I2C devices,
and the OLED shows "Boa sorte!".
"""

from machine import I2C, Pin
import ssd1306

OLED_SCL_PIN = 25
OLED_SDA_PIN = 16
OLED_I2C_ADDRESS = 0x3C

i2c = I2C(
    0,
    scl=Pin(OLED_SCL_PIN),
    sda=Pin(OLED_SDA_PIN),
    freq=400_000,
)

detected_devices = i2c.scan()

print("I2C devices:", detected_devices)

if OLED_I2C_ADDRESS not in detected_devices:
    raise RuntimeError("SSD1306 not detected at address 0x3C")

oled_display = ssd1306.SSD1306_I2C(
    128,
    64,
    i2c,
    addr=OLED_I2C_ADDRESS,
)

oled_display.fill(0)
oled_display.text("Boa sorte!", 16, 28)
oled_display.show()

print("OLED test completed")
