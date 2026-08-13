"""
CESS-UFF - ESP32 MicroPython Practical Assessment
Courses: Instrumentation / Electronics / Programming Logic

Controls nine LEDs (six blinking at the same adjustable interval, each its
own independent task, plus one driven by a push button and two idle
indicators) and updates three displays -- two SSD1306 OLEDs, each on its
own I2C bus, and an ILI9341 TFT over 4-wire SPI. The two OLEDs are live
Task-Manager-style resource graphs: the first plots real I2C/SPI bus-busy
time as a stand-in "CPU usage," the second plots real MicroPython heap
usage as "RAM usage." Two extra push-buttons speed up or slow down every
blinking LED at once. Cooperative asyncio tasks prevent timing delays from
blocking the complete application and keep every LED and every display
update running independently of each other and of the button-monitoring
logic.

See docs/EN/technical-specification.md for the full requirements and the
rationale behind every decision below.
"""

import asyncio
import gc
import time
from machine import Pin, I2C, SPI

from ssd1306 import SSD1306_I2C
from ili9341 import ILI9341

# --- Pin assignments (mandatory project requirements) -----------------------
# NOTE: RED_LED_PIN and OLED_SCL_PIN were moved off their original fixed
# pins (GPIO 2 and GPIO 25) at the user's explicit request, for board layout.
RED_LED_PIN = 26
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SCL_PIN = 32
OLED_SDA_PIN = 16

# --- Pin assignments (extra blinking LEDs, different frequencies) -----------
# GPIO 34/35 are input-only on the ESP32 (no output driver) and cannot be
# used here. GPIO 12 (RED_LED_2_PIN) is a strapping pin (sets flash voltage
# at boot) -- safe here because this LED only ever sinks current to GND
# through a resistor, it never pulls the pin toward 3V3 during boot.
BLUE_LED_PIN = 14
YELLOW_LED_PIN = 27
WHITE_LED_PIN = 25
ORANGE_LED_PIN = 33
RED_LED_2_PIN = 12

# --- Pin assignments (4-wire SPI TFT: SCK, MOSI, CS, D/C) -------------------
TFT_SCK_PIN = 18
TFT_MOSI_PIN = 23
TFT_CS_PIN = 5
TFT_DC_PIN = 21
TFT_RST_PIN = 19

# --- Pin assignments (speed buttons + idle indicators) ----------------------
# GPIO 34/35 are input-only and have no internal pull resistors at all, so
# (unlike BUTTON_PIN) these two need an external physical pull-down --
# see diagram.json.
DECREASE_SPEED_BUTTON_PIN = 34
INCREASE_SPEED_BUTTON_PIN = 35
BUS_IDLE_LED_PIN = 13
SCHEDULER_IDLE_LED_PIN = 2

# --- Pin assignments (second OLED, its own I2C bus) --------------------------
# A separate machine.I2C(1) bus, independent of the first OLED's I2C(0), so
# both can be addressed at the same time without bus contention.
OLED2_SCL_PIN = 15
OLED2_SDA_PIN = 22

# --- Timing configuration ----------------------------------------------------
# All six blinking LEDs share the same base interval -- each is still its
# own independent asyncio task (see BLINKING_LEDS/blink_led()), just running
# the same 500 ms period, as if they were separate, identical equipment.
RED_LED_2_BLINK_INTERVAL_MS = 500
BLUE_LED_BLINK_INTERVAL_MS = 500
YELLOW_LED_BLINK_INTERVAL_MS = 500
RED_LED_BLINK_INTERVAL_MS = 500
WHITE_LED_BLINK_INTERVAL_MS = 500
ORANGE_LED_BLINK_INTERVAL_MS = 500

# Each speed-button press doubles or halves every blinking LED's interval at
# once (relative to its own 500 ms base above), so all six always stay in
# lockstep with each other. The step is clamped so the interval can't reach
# 0 ms or run away to an absurd wait.
BLINK_SPEED_STEP_MIN = -2  # fastest: 500ms x0.25 = 125 ms
BLINK_SPEED_STEP_MAX = 3   # slowest: 500ms x8 = 4 s

BUTTON_SAMPLE_INTERVAL_MS = 5
# Wokwi's simulated push-button is bounce-free, so this debounce window is
# not required to pass the simulation. It is kept because it is the correct
# behavior for a real, physical button (see docs, "Debounce strategy").
BUTTON_DEBOUNCE_MS = 30

# --- Display configuration ----------------------------------------------------
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDRESS = 0x3C
OLED_I2C_FREQUENCY_HZ = 400_000
CPU_GRAPH_SAMPLE_INTERVAL_MS = 250
RAM_GRAPH_SAMPLE_INTERVAL_MS = 250

# --- Peripheral setup ----------------------------------------------------
red_led = Pin(RED_LED_PIN, Pin.OUT, value=0)
green_led = Pin(GREEN_LED_PIN, Pin.OUT, value=0)
blue_led = Pin(BLUE_LED_PIN, Pin.OUT, value=0)
yellow_led = Pin(YELLOW_LED_PIN, Pin.OUT, value=0)
white_led = Pin(WHITE_LED_PIN, Pin.OUT, value=0)
orange_led = Pin(ORANGE_LED_PIN, Pin.OUT, value=0)
red_led_2 = Pin(RED_LED_2_PIN, Pin.OUT, value=0)

# Every LED that blinks on a fixed interval, paired with its current
# interval, so main() can launch one independent asyncio task per LED from a
# single loop instead of one hand-written coroutine per LED. Each pair is a
# mutable list (not a tuple) because the speed buttons rewrite the interval
# in place while blink_led() is already running its loop on that same entry.
BLINKING_LEDS = [
    [red_led, RED_LED_BLINK_INTERVAL_MS],
    [blue_led, BLUE_LED_BLINK_INTERVAL_MS],
    [yellow_led, YELLOW_LED_BLINK_INTERVAL_MS],
    [white_led, WHITE_LED_BLINK_INTERVAL_MS],
    [orange_led, ORANGE_LED_BLINK_INTERVAL_MS],
    [red_led_2, RED_LED_2_BLINK_INTERVAL_MS],
]
# Snapshot of each LED's un-scaled interval, same order as BLINKING_LEDS --
# the reference apply_blink_speed_step() always scales from, so repeated
# presses can't compound rounding error across many small steps.
BASE_BLINK_INTERVALS_MS = tuple(interval_ms for _, interval_ms in BLINKING_LEDS)
blink_speed_step = 0


def apply_blink_speed_step(step_delta):
    """Shift every blinking LED's interval by the same power-of-two factor,
    clamped to [BLINK_SPEED_STEP_MIN, BLINK_SPEED_STEP_MAX]."""
    global blink_speed_step
    blink_speed_step = max(
        BLINK_SPEED_STEP_MIN, min(BLINK_SPEED_STEP_MAX, blink_speed_step + step_delta)
    )
    scale = 2**blink_speed_step
    for entry, base_interval_ms in zip(BLINKING_LEDS, BASE_BLINK_INTERVALS_MS):
        entry[1] = round(base_interval_ms * scale)


# Internal pull-down: the pin reads LOW when idle and HIGH when pressed,
# as required by the specification. No external resistor is used.
push_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)

# GPIO 34/35 have no internal pull resistors, so an external physical
# pull-down (diagram.json) gives the same released=LOW/pressed=HIGH
# behavior as push_button's internal one.
decrease_speed_button = Pin(DECREASE_SPEED_BUTTON_PIN, Pin.IN)
increase_speed_button = Pin(INCREASE_SPEED_BUTTON_PIN, Pin.IN)

# On by default; _bus_busy_begin()/_bus_busy_end() turn it off only for the
# few milliseconds an I2C/SSD1306 or SPI/ILI9341 write is actually in
# flight -- the only blocking calls this project has (see
# docs/EN/technical-specification.md, section 7.2's engineering note).
bus_idle_led = Pin(BUS_IDLE_LED_PIN, Pin.OUT, value=1)

# Accumulates microseconds spent inside a _bus_busy_begin()/_bus_busy_end()
# span since the last time the CPU-usage graph task read and reset it --
# see update_cpu_graph(). This is real measured I2C/SPI bus-busy time, not
# a simulated number.
bus_busy_time_us = 0


def _bus_busy_begin():
    bus_idle_led.off()
    return time.ticks_us()


def _bus_busy_end(started_at_us):
    global bus_busy_time_us
    bus_busy_time_us += time.ticks_diff(time.ticks_us(), started_at_us)
    bus_idle_led.on()


# Lowest-priority task in the cooperative scheduler: it has no fixed
# schedule of its own and always asks to run again immediately
# (asyncio.sleep_ms(0)), so it only gets CPU time in the gaps between every
# other task's own await point. uasyncio has no real task-priority levels,
# so this is a coarse visualization of scheduler activity, not a literal
# RTOS idle task.
scheduler_idle_led = Pin(SCHEDULER_IDLE_LED_PIN, Pin.OUT, value=0)

# Hardware I2C bus 0, on the mandatory OLED pins. Confirmed working on
# Wokwi's simulated ESP32 by tests/05_oled_basic.py and
# tests/06_oled_full_diagnostic.py (see docs/EN/technical-specification.md,
# section 16) -- an earlier revision used machine.SoftI2C as an
# unconfirmed defensive compatibility choice; that is no longer needed.
i2c = I2C(
    0,
    scl=Pin(OLED_SCL_PIN),
    sda=Pin(OLED_SDA_PIN),
    freq=OLED_I2C_FREQUENCY_HZ,
)


def create_oled_display(i2c_bus, label):
    """Initialize an SSD1306 OLED if detected on the given I2C bus, else
    return None.

    Returning ``None`` on failure lets the rest of the application stay
    operational while reporting a clear diagnostic, instead of crashing the
    whole program on a wiring mistake.
    """
    detected_addresses = i2c_bus.scan()
    if OLED_I2C_ADDRESS not in detected_addresses:
        print(
            "{} initialization failed: expected I2C address 0x{:02X}, "
            "detected {}".format(
                label,
                OLED_I2C_ADDRESS,
                ["0x{:02X}".format(address) for address in detected_addresses],
            )
        )
        return None

    return SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c_bus, addr=OLED_I2C_ADDRESS)


oled_display = create_oled_display(i2c, "OLED")

# Second, independent hardware I2C bus (I2C(1)) driving a second SSD1306 --
# runs alongside the first OLED's I2C(0) bus without contention.
i2c_2 = I2C(
    1,
    scl=Pin(OLED2_SCL_PIN),
    sda=Pin(OLED2_SDA_PIN),
    freq=OLED_I2C_FREQUENCY_HZ,
)
oled_display_2 = create_oled_display(i2c_2, "OLED 2")

# 4-wire SPI TFT (SCK, MOSI, CS, D/C), independent of the I2C OLEDs above --
# all three displays run at the same time, on separate buses/pins.
tft_spi = SPI(2, baudrate=20_000_000, sck=Pin(TFT_SCK_PIN), mosi=Pin(TFT_MOSI_PIN))


def create_tft_display():
    """Initialize the SPI TFT, or return None if it fails to respond.

    Same graceful-degradation shape as create_oled_display(): a wiring
    mistake on the TFT must not take down the LEDs, button or OLED.
    """
    try:
        return ILI9341(
            tft_spi,
            cs=Pin(TFT_CS_PIN, Pin.OUT, value=1),
            dc=Pin(TFT_DC_PIN, Pin.OUT, value=0),
            rst=Pin(TFT_RST_PIN, Pin.OUT, value=1),
        )
    except OSError as error:
        print("TFT initialization failed:", error)
        return None


tft_display = create_tft_display()

# RGB565 colors, one per entry in BLINKING_LEDS, in the same order.
BLINKING_LED_COLORS565 = (0xF800, 0x001F, 0xFFE0, 0xFFFF, 0xFD20, 0x7800)


def draw_frequency_legend():
    """Draw one color bar per blinking LED, ordered top-to-bottom to match
    BLINKING_LEDS -- a static legend, drawn once at startup like the OLED's
    initial message, not redrawn on a timer.
    """
    if tft_display is None:
        return

    bar_height = tft_display.height // len(BLINKING_LEDS)
    started_at = _bus_busy_begin()
    for index, color565 in enumerate(BLINKING_LED_COLORS565):
        tft_display.fill_rect(0, index * bar_height, tft_display.width, bar_height, color565)
    _bus_busy_end(started_at)


# One history buffer per OLED graph, one sample per horizontal pixel column
# (oldest sample scrolls off the left edge once the buffer is full).
cpu_usage_history = []
ram_usage_history = []


def draw_usage_graph(display, history, value_percent, label):
    """Task-Manager-style scrolling bar graph: append value_percent as the
    newest column, drop the oldest one past OLED_WIDTH samples, and redraw
    every column as a bar from the bottom of the screen."""
    if display is None:
        return

    history.append(max(0, min(100, value_percent)))
    if len(history) > OLED_WIDTH:
        del history[0]

    started_at = _bus_busy_begin()
    display.fill(0)
    for x, percent in enumerate(history):
        bar_height = round(percent / 100 * (OLED_HEIGHT - 1))
        if bar_height > 0:
            display.vline(x, OLED_HEIGHT - bar_height, bar_height, 1)
    display.text(label, 0, 0, 1)
    display.show()
    _bus_busy_end(started_at)


def apply_button_state(is_pressed):
    """Update the green LED for a stable button state.

    Called only at startup and after a debounced state transition. The
    OLEDs no longer show button text -- both are now live resource-usage
    graphs (see draw_usage_graph()), unrelated to the button.
    """
    green_led.value(1 if is_pressed else 0)
    print("Button: {} | Green LED: {}".format(
        "pressed" if is_pressed else "released",
        "ON" if is_pressed else "OFF",
    ))


async def blink_led(entry):
    """Toggle one LED at its own interval, independent of every other task
    -- one call per entry in BLINKING_LEDS gives each LED its own frequency
    without blocking, or being blocked by, any other LED. entry[1] is read
    fresh every cycle (not captured once) so apply_blink_speed_step() can
    change the running speed without restarting the task."""
    led, _ = entry
    while True:
        led.value(not led.value())
        await asyncio.sleep_ms(entry[1])


async def debounce_button(pin, initial_state, on_change):
    """Sample and debounce a button, calling on_change(stable_state) once
    per accepted transition. Shared by the main push-button monitor and the
    two speed step-buttons below."""
    stable_state = initial_state
    candidate_state = initial_state
    candidate_since = time.ticks_ms()

    while True:
        raw_state = bool(pin.value())
        now = time.ticks_ms()

        if raw_state != candidate_state:
            candidate_state = raw_state
            candidate_since = now
        elif (
            candidate_state != stable_state
            and time.ticks_diff(now, candidate_since) >= BUTTON_DEBOUNCE_MS
        ):
            stable_state = candidate_state
            on_change(stable_state)

        await asyncio.sleep_ms(BUTTON_SAMPLE_INTERVAL_MS)


async def monitor_button(initial_state):
    """React to every debounced push-button transition (press and release)."""
    await debounce_button(push_button, initial_state, apply_button_state)


async def monitor_step_button(pin, on_press):
    """React only to the debounced press edge of a momentary button, e.g. a
    speed-step button that should fire once per press, not on release too."""
    def on_change(is_pressed):
        if is_pressed:
            on_press()

    await debounce_button(pin, False, on_change)


async def scheduler_idle_task():
    """See SCHEDULER_IDLE_LED_PIN's setup comment: on only while no other
    task's own turn is in progress."""
    while True:
        scheduler_idle_led.on()
        await asyncio.sleep_ms(0)
        scheduler_idle_led.off()
        await asyncio.sleep_ms(0)


async def update_cpu_graph():
    """First OLED: "CPU usage" graph. The percentage is the real fraction of
    each sampling window spent inside a blocking I2C/SPI transfer (the only
    time this single-core cooperative app is actually busy, as opposed to
    suspended in an await) -- not a value read from an OS scheduler, since
    MicroPython on bare ESP32 exposes no such thing."""
    global bus_busy_time_us
    while True:
        window_us = CPU_GRAPH_SAMPLE_INTERVAL_MS * 1000
        cpu_percent = round(bus_busy_time_us / window_us * 100)
        bus_busy_time_us = 0
        draw_usage_graph(oled_display, cpu_usage_history, cpu_percent, "CPU")
        await asyncio.sleep_ms(CPU_GRAPH_SAMPLE_INTERVAL_MS)


async def update_ram_graph():
    """Second OLED: RAM usage graph, from MicroPython's real gc heap stats
    (gc.mem_alloc() / gc.mem_free()) -- an actual measured value, not a
    simulated one."""
    while True:
        allocated = gc.mem_alloc()
        free = gc.mem_free()
        ram_percent = round(allocated / (allocated + free) * 100)
        draw_usage_graph(oled_display_2, ram_usage_history, ram_percent, "RAM")
        await asyncio.sleep_ms(RAM_GRAPH_SAMPLE_INTERVAL_MS)


async def main():
    initial_button_state = bool(push_button.value())
    apply_button_state(initial_button_state)
    draw_frequency_legend()

    for entry in BLINKING_LEDS:
        asyncio.create_task(blink_led(entry))
    asyncio.create_task(scheduler_idle_task())
    asyncio.create_task(update_cpu_graph())
    asyncio.create_task(update_ram_graph())
    asyncio.create_task(
        monitor_step_button(decrease_speed_button, lambda: apply_blink_speed_step(-1))
    )
    asyncio.create_task(
        monitor_step_button(increase_speed_button, lambda: apply_blink_speed_step(+1))
    )
    await monitor_button(initial_button_state)


try:
    asyncio.run(main())
finally:
    # Leave outputs in a predictable safe state after an exception or stop.
    red_led.off()
    green_led.off()
    blue_led.off()
    yellow_led.off()
    white_led.off()
    orange_led.off()
    red_led_2.off()
    scheduler_idle_led.off()
