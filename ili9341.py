"""Minimal SPI driver for the ILI9341 TFT controller.

What this project needs: hardware reset, panel initialization,
solid-color rectangle fills, and one line of colored text, over the
4-wire SPI command interface (SCK, MOSI, CS, D/C).
"""

import framebuf
import time
from micropython import const

CHAR_WIDTH = const(8)
CHAR_HEIGHT = const(8)

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

        self._glyph_byte_tables = {}

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

    def blit(self, x, y, width, height, pixel_bytes):
        """Write raw RGB565 pixel data (row-major, 2 bytes/pixel) into the
        given window -- used by text() to paint pre-rendered glyphs."""
        self._set_window(x, y, x + width - 1, y + height - 1)
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(pixel_bytes)
        self.cs.value(1)

    def _glyph_byte_table(self, color565, bg565):
        """Return (building and caching on first use) a 256*16-byte table
        where table[b*16 : b*16+16] is the 8-pixel RGB565 expansion of
        MONO_HLSB byte value b, for this foreground/background pair.

        text() used to call framebuf's glyphs.pixel(col, row) once per
        pixel (e.g. 1920 calls for one 30-character line) plus a 2-byte
        slice assignment each time -- the dominant cost of a console line.
        Expanding one MONO_HLSB byte (8 pixels) at a time via this cached
        table cuts the per-line work 8x and turns it into table lookups
        instead of per-pixel branches, and the cache means that cost is
        only ever paid once per distinct color pair -- this project reuses
        a handful of fixed console colors, so in practice almost every
        call after the first hits the cache.
        """
        key = (color565, bg565)
        table = self._glyph_byte_tables.get(key)
        if table is not None:
            return table

        fg = bytes((color565 >> 8, color565 & 0xFF))
        bg = bytes((bg565 >> 8, bg565 & 0xFF))
        table = bytearray(256 * 16)
        for byte_value in range(256):
            offset = byte_value * 16
            for bit in range(8):
                table[offset:offset + 2] = fg if byte_value & (0x80 >> bit) else bg
                offset += 2
        table = bytes(table)
        self._glyph_byte_tables[key] = table
        return table

    def text(self, string, x, y, color565, bg565=0x0000):
        """Draw one line of monospace 8x8-font text at (x, y).

        Renders into an off-screen 1-bit framebuf.FrameBuffer (reusing
        MicroPython's built-in font, the same one ssd1306.py uses), then
        expands it to RGB565 one MONO_HLSB byte (8 pixels) at a time via
        _glyph_byte_table() before sending a single blit.
        """
        width = len(string) * CHAR_WIDTH
        if width == 0:
            return
        stride = width // 8  # exact: CHAR_WIDTH is a multiple of 8
        mono = bytearray(stride * CHAR_HEIGHT)
        glyphs = framebuf.FrameBuffer(mono, width, CHAR_HEIGHT, framebuf.MONO_HLSB)
        glyphs.text(string, 0, 0, 1)

        table = self._glyph_byte_table(color565, bg565)
        pixels = bytearray(width * CHAR_HEIGHT * 2)
        out = 0
        for byte_value in mono:
            chunk_start = byte_value * 16
            pixels[out:out + 16] = table[chunk_start:chunk_start + 16]
            out += 16

        self.blit(x, y, width, CHAR_HEIGHT, pixels)
