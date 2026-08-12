"""Minimal SPI driver for the ILI9341 TFT controller.

Only what this project needs: hardware reset, panel initialization and
solid-color rectangle fills over the 4-wire SPI command interface (SCK,
MOSI, CS, D/C) -- no framebuffer, no text rendering.
"""

import time
from micropython import const

_SWRESET = const(0x01)
_SLPOUT = const(0x11)
_PIXFMT = const(0x3A)
_MADCTL = const(0x36)
_CASET = const(0x2A)
_PASET = const(0x2B)
_RAMWR = const(0x2C)
_DISPON = const(0x29)


class ILI9341:
    def __init__(self, spi, cs, dc, rst, width=240, height=320):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.width = width
        self.height = height

        self.cs.value(1)
        self._hard_reset()
        self._init_sequence()

    def _hard_reset(self):
        self.rst.value(1)
        time.sleep_ms(10)
        self.rst.value(0)
        time.sleep_ms(10)
        self.rst.value(1)
        time.sleep_ms(120)

    def _write(self, buffer, is_data):
        self.dc.value(1 if is_data else 0)
        self.cs.value(0)
        self.spi.write(buffer)
        self.cs.value(1)

    def _command(self, command, args=b""):
        self._write(bytes([command]), False)
        if args:
            self._write(args, True)

    def _init_sequence(self):
        self._command(_SWRESET)
        time.sleep_ms(120)
        self._command(_SLPOUT)
        time.sleep_ms(120)
        self._command(_PIXFMT, b"\x55")  # 16 bits/pixel (RGB565)
        self._command(_MADCTL, b"\x48")  # standard row/column order
        self._command(_DISPON)
        time.sleep_ms(20)

    def _set_window(self, x0, y0, x1, y1):
        self._command(_CASET, bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        self._command(_PASET, bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        self._command(_RAMWR)

    def fill_rect(self, x, y, width, height, color565):
        self._set_window(x, y, x + width - 1, y + height - 1)
        row = bytes([color565 >> 8, color565 & 0xFF]) * width
        self.dc.value(1)
        self.cs.value(0)
        for _ in range(height):
            self.spi.write(row)
        self.cs.value(1)

    def fill(self, color565):
        self.fill_rect(0, 0, self.width, self.height, color565)
