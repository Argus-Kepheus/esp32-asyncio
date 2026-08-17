"""Test 13/13 — TFT text-rendering diagnostic (the console mechanism).

Exercises ili9341.py's text() -- the same primitive main.py's TFT log
console (console_log()) is built on -- across every color the console
uses, plus the row-wrapping behavior once the screen fills. See
tests/README.md for how to run this on wokwi.com.

Run this only after test 12 (TFT basic fills) has passed: text() renders
into an off-screen framebuf and blits the result, so it depends on
fill_rect()/blit() already working correctly.

Expected: one line per console color (blue, orange, yellow, green, red,
purple, white) prints top to bottom, each labeled with its own name and
color; once enough lines have been printed to fill the screen, new lines
resume from the top, overwriting the oldest ones -- the same wrap
behavior console_log() uses instead of true scrolling.
"""

from machine import Pin, SPI
from time import sleep_ms
from ili9341 import ILI9341, CHAR_HEIGHT

TFT_SCK_PIN = 18
TFT_MOSI_PIN = 23
TFT_CS_PIN = 5
TFT_DC_PIN = 21
TFT_RST_PIN = 19

LINE_STEP_MS = 400
BACKGROUND = 0x0000

spi = SPI(2, baudrate=20_000_000, sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))
tft = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN, Pin.OUT, value=1),
    dc=Pin(TFT_DC_PIN, Pin.OUT, value=0),
    rst=Pin(TFT_RST_PIN, Pin.OUT, value=1),
)
tft.fill(BACKGROUND)

# Same seven colors main.py's console_log() uses, so this test exercises
# exactly the color set the real console depends on.
COLORS = (
    ("blue", 0x001F),
    ("orange", 0xFD20),
    ("yellow", 0xFFE0),
    ("green", 0x07E0),
    ("red", 0xF800),
    ("purple", 0xCD1C),
    ("white", 0xFFFF),
)

max_rows = tft.height // CHAR_HEIGHT
row = 0

print("TFT text diagnostic started -- {} rows fit on screen".format(max_rows))

count = 0
while True:
    name, color565 = COLORS[count % len(COLORS)]
    message = "{} #{}".format(name, count)
    y = row * CHAR_HEIGHT

    tft.fill_rect(0, y, tft.width, CHAR_HEIGHT, BACKGROUND)
    tft.text(message, 0, y, color565, BACKGROUND)
    print("Row {}: {}".format(row, message))

    row = (row + 1) % max_rows
    count += 1
    sleep_ms(LINE_STEP_MS)
