"""Test 14/14 -- Serial fallback for the TFT console log, no hardware needed.

Isolates one specific claim from main.py's console_log(): every line is
printed to the serial console unconditionally, not only when tft_display
is None. This matters because create_tft_display() cannot reliably tell
a physically absent TFT from a present one (see its docstring in
main.py): the SPI link there is write-only, so a disconnected panel very
likely raises no OSError at all, and tft_display stays a live object.
Relying on "tft_display is None" as the only trigger for a serial
fallback would silently lose every console event on exactly the hardware
fault this project cares about catching.

This test touches no GPIO or peripheral -- it reproduces console_log()'s
two relevant lines (the unconditional print(), then the
tft_display-gated early return) against a stand-in value that is either
None or a dummy "connected" object, and checks that the message reaches
the serial console either way.

Expected: all four lines below print, regardless of the simulated
tft_display state -- confirming the fallback does not depend on
tft_display actually being None.
"""


def console_log_like(message, tft_display):
    print(message)
    if tft_display is None:
        return
    print("  (would also write to the physical TFT here)")


class _DummyTFT:
    """Stands in for a live ILI9341 object -- a physically disconnected
    but electrically silent TFT would leave create_tft_display()
    returning something just like this, not None."""


print("Case 1/2: tft_display is None (TFT construction raised OSError)")
console_log_like("  Button pressed -> Green LED ON", None)

print("Case 2/2: tft_display is a live object (TFT absent but SPI silent)")
console_log_like("  Button pressed -> Green LED ON", _DummyTFT())

print("Serial-fallback test finished -- both cases above must have printed their message line.")
