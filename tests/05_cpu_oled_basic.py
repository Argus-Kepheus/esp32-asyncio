"""Test 5/13 — CPU OLED basic check: I2C scan + current-role label.

The simplest possible OLED check: confirm the display answers on the I2C
bus at the expected address and can render one line of static text. See
tests/README.md for how to run this on wokwi.com.

This is main.py's CPU OLED (I2C bus 0) -- the RAM OLED
(I2C bus 1, GPIO 15/22) has its own isolated check, test 11.

Uses the same hardware machine.I2C peripheral and current GPIO mapping as
main.py.

Expected: the serial monitor lists 0x3C among the detected I2C devices,
and the OLED shows "CPU OLED OK".
"""

from machine import I2C, Pin
import ssd1306

CPU_OLED_SCL_PIN = 32
CPU_OLED_SDA_PIN = 16
CPU_OLED_I2C_ADDRESS = 0x3C

cpu_i2c = I2C(
    0,
    scl=Pin(CPU_OLED_SCL_PIN),
    sda=Pin(CPU_OLED_SDA_PIN),
    freq=400_000,
)

detected_devices = cpu_i2c.scan()

print("I2C devices:", detected_devices)

if CPU_OLED_I2C_ADDRESS not in detected_devices:
    raise RuntimeError("CPU SSD1306 not detected at address 0x3C")

cpu_oled = ssd1306.SSD1306_I2C(
    128,
    64,
    cpu_i2c,
    addr=CPU_OLED_I2C_ADDRESS,
)

cpu_oled.fill(0)
cpu_oled.text("CPU OLED OK", 16, 28)
cpu_oled.show()

print("CPU OLED test completed")
