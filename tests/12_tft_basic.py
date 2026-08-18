"""Test 12/13 — TFT basic check: SPI init + solid-color fills.

Isolates the ILI9341 TFT: hardware SPI on SCK=GPIO18, MOSI=GPIO23,
CS=GPIO5, D/C=GPIO21, RST=GPIO19 -- the 4-wire SPI command interface (SCK,
MOSI, CS, D/C) plus a hardware reset line. See tests/README.md for how to
run this on wokwi.com.

Only exercises ili9341.py's init sequence and fill_rect()/fill() -- no
text rendering. If this test fails (blank/garbled screen, or an
exception during init), the fault is in the SPI wiring or the panel init
sequence itself, before text rendering (test 13) becomes a relevant
variable at all.

Expected: the screen cycles red, green, blue, white, black, each held for
1 second, then repeats.
"""

from machine import Pin, SPI
from time import sleep_ms
from ili9341 import ILI9341

TFT_SCK_PIN = 18
TFT_MOSI_PIN = 23
TFT_CS_PIN = 5
TFT_DC_PIN = 21
TFT_RST_PIN = 19

COLOR_STEP_MS = 1000

spi = SPI(2, baudrate=20_000_000, sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))
tft = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN, Pin.OUT, value=1),
    dc=Pin(TFT_DC_PIN, Pin.OUT, value=0),
    rst=Pin(TFT_RST_PIN, Pin.OUT, value=1),
)

print("TFT basic test started -- cycling red/green/blue/white/black")

colors = (
    ("red", 0xF800),
    ("green", 0x07E0),
    ("blue", 0x001F),
    ("white", 0xFFFF),
    ("black", 0x0000),
)

while True:
    for name, color565 in colors:
        print("Fill:", name)
        tft.fill(color565)
        sleep_ms(COLOR_STEP_MS)
