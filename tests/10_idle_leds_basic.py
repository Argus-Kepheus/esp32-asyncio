"""Test 10/13 — Idle-indicator LEDs, basic wiring check (GPIO 13, GPIO 2).

Isolates the two LEDs main.py drives as activity indicators rather than a
fixed blink pattern: bus_idle_led (orange, GPIO 13, ON when the I2C/SPI
bus is idle, OFF while a display write is in flight -- an inverted
"busy" reading) and scheduler_idle_led (yellow, GPIO 2, scheduler
throughput, not a literal idle/priority signal -- see main.py's
scheduler_idle_task() docstring). See tests/README.md for how to run
this on wokwi.com.

This test only confirms the GPIO/resistor/LED wiring itself by
alternating both LEDs on a fixed timer -- it does not exercise the real
busy/idle logic in main.py, which needs the I2C/SPI bus and the
scheduler running to mean anything.

GPIO 2 is a boot-strapping pin; that only matters at reset, before this
script (or any MicroPython script) runs, and only if something forces an
external level on it during boot. This LED only ever sinks current to
GND through its resistor once GPIO 2 is already configured as an output,
so it does not interfere with boot.

Expected: the two LEDs alternate -- orange (GPIO13) ON while yellow
(GPIO2) is OFF, then the reverse -- every 500 ms, continuously.
"""

from machine import Pin
from time import sleep_ms

BLINK_INTERVAL_MS = 500

bus_idle_led = Pin(13, Pin.OUT, value=1)
scheduler_idle_led = Pin(2, Pin.OUT, value=0)

print("Idle-LED test started (orange=GPIO13, yellow=GPIO2)")

while True:
    bus_idle_led.value(not bus_idle_led.value())
    scheduler_idle_led.value(not scheduler_idle_led.value())
    print(
        "orange(GPIO13):", "ON" if bus_idle_led.value() else "OFF",
        "| yellow(GPIO2):", "ON" if scheduler_idle_led.value() else "OFF",
    )
    sleep_ms(BLINK_INTERVAL_MS)
