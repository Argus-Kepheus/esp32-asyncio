# Technical Specification — esp32-asyncio

## 1. Document control

| Field | Value |
|---|---|
| Project | Personal ESP32 MicroPython asyncio exploration |
| Courses | Instrumentation, Electronics and Programming Logic |
| Target platform | ESP32 (MicroPython) |
| Simulation platform | Wokwi |
| Main executable | `main.py` |
| Circuit definition | `diagram.json` |
| License | CC0 1.0 Universal |
| Document language | English |
| User-visible OLED messages | Portuguese, as explicitly required |

This document consolidates the project's requirements and engineering
decisions. Comments from additional collaborators may be integrated in
later revisions provided that the mandatory behavior and traceability
described here are preserved. See §7 for the process.

## 2. Objective

Develop and simulate an ESP32 MicroPython application that concurrently:

1. blinks six LEDs, each its own independent `asyncio` task, all sharing one
   adjustable interval;
2. reads a normally-open, active-high push-button and drives a green LED
   from its state;
3. reads two further push-buttons that speed up or slow down all six
   blinking LEDs at once;
4. plots live CPU- and RAM-usage graphs on two independent SSD1306 OLEDs;
5. logs colored, per-subsystem activity lines to an ILI9341 TFT console,
   mirrored to the serial console; and
6. lights two status-indicator LEDs reflecting display-bus and scheduler
   activity.

The deliverables are a complete executable `main.py` (with its `ssd1306.py`
and `ili9341.py` drivers), this repository published on GitHub, and a
shareable Wokwi platform link showing the simulated circuit.

## 3. Simulation platform decision

Wokwi is the platform used for this project.

**Rationale:** Wokwi natively supports ESP32 simulation, a complete
MicroPython `main.py`, an I2C SSD1306 OLED component, circuit definition
through `diagram.json`, interactive button/LED simulation, and a shareable
browser project URL.

Tinkercad Circuits was excluded: it only runs Arduino-style C/C++ or block
code on its boards and cannot execute a MicroPython script at all, so it
could not satisfy the assignment's source-code deliverable as specified —
this is not a general statement that Tinkercad lacks educational value.

### 3.1 Board selection

The `board-esp32-devkit-c-v4` part (`diagram.json`, part id `esp32`) is used
as the project's target board. The ESP32-DevKitC V4 was selected as the
project target because it is an official Espressif development board
supported natively by Wokwi, provides all GPIO pins required by the
specification, and has complete manufacturer documentation. The selection is
intended to improve reproducibility and eliminate ambiguities associated
with generic or unofficial ESP32 development boards.

Full field-by-field specifications for this board, the OLED display, and
every other simulated part are kept in
[`docs/component-specifications.md`](component-specifications.md) — one
sheet per component, so identifiers and pin names stay unambiguous and don't
have to be re-derived from `diagram.json` each time. The GPIO-to-physical-
header mapping, module compatibility, reserved pins, and a physical wiring
checklist are kept in
[`docs/hardware-reference.md`](hardware-reference.md).

## 4. Functional requirements

### FR-01 — Six blinking LEDs

- Component IDs: `blue-led-1` through `blue-led-6` · Python variables:
  `blue_led_1` through `blue_led_6` · Pin constants: `BLUE_LED_1_PIN`
  (GPIO 26), `BLUE_LED_2_PIN` (14), `BLUE_LED_3_PIN` (27),
  `BLUE_LED_4_PIN` (25), `BLUE_LED_5_PIN` (33), `BLUE_LED_6_PIN` (12)
- All six are physically blue (`#0000FF`) in `diagram.json`, and the same
  1–6 numbering is used consistently in the circuit and Python source
- Direction: digital output, each its own independent `asyncio` task
  (`blink_led()`, driven by the `BLINKING_LEDS` list)
- Behavior: toggle on a shared 500 ms base interval, adjustable per FR-03
- Constraint: logically independent of every other task — none calls or
  waits on another — though all still share the single cooperative
  scheduler (§7.2 engineering note)

### FR-02 — Push-button and green LED

- Component IDs: `push-button`, `green-led` · Python variables:
  `push_button`, `green_led` · Pin constants: `BUTTON_PIN` (GPIO 17),
  `GREEN_LED_PIN` (GPIO 4)
- Button: normally-open momentary, `Pin.IN` with internal `Pin.PULL_DOWN`;
  released electrical state LOW, pressed HIGH
- Green LED: digital output; button released → OFF, button pressed → ON
- Every debounced transition is logged through `console_log()` in green
  (FR-05)

### FR-03 — Speed buttons

- Component IDs: `decrease-speed-button`, `increase-speed-button` · Python
  variables: `decrease_speed_button`, `increase_speed_button` · Pin
  constants: `DECREASE_SPEED_BUTTON_PIN` (GPIO 34),
  `INCREASE_SPEED_BUTTON_PIN` (GPIO 35)
- Input-only pins with no internal pull resistor — each needs its own
  external 10 kΩ pull-down to GND (already in `diagram.json`)
- Each press scales every blinking LED's interval by the same power-of-two
  factor at once, clamped to [125 ms, 4 s] (`BLINK_SPEED_STEP_MIN`/`_MAX`)

### FR-04 — Two OLED resource graphs

- Component IDs: `oled0-display`, `oled1-display` · Python variables:
  `oled0_display`, `oled1_display`
- Controller: SSD1306 · Resolution: 128 × 64 · Address: `0x3C` on both
- CPU OLED0: `machine.I2C(0)`, SCL GPIO 32, SDA GPIO 16 — plots the "CPU"
  graph (§19.2)
- RAM OLED1: `machine.I2C(1)`, SCL GPIO 15, SDA GPIO 22 — its own
  independent hardware I2C bus, plots the "RAM" graph
- Both redrawn at least every 250 ms (`CPU_GRAPH_SAMPLE_INTERVAL_MS` /
  `RAM_GRAPH_SAMPLE_INTERVAL_MS`, a floor not an exact period — §9)

### FR-05 — TFT log console

- Component ID: `tft-display` · Python variable: `tft_display`
- Controller: ILI9341 · genuine 4-wire SPI: SCK GPIO 18, MOSI GPIO 23, CS
  GPIO 5, D/C GPIO 21, RST GPIO 19
- `console_log()` writes one colored line per system event (one color per
  subsystem), wrapping back to the top of the screen once full, and always
  mirrors every line to the serial console too, regardless of whether the
  TFT is present (§19.4)

### FR-06 — Status-indicator LEDs

- Component IDs: `bus-idle-led`, `scheduler-idle-led` · Python variables:
  `bus_idle_led`, `scheduler_idle_led` · Pin constants: `BUS_IDLE_LED_PIN`
  (GPIO 13), `SCHEDULER_IDLE_LED_PIN` (GPIO 2)
- Orange (`bus_idle_led`): ON by default, OFF only while an instrumented
  display write is in flight — an inverted "bus busy" reading
- Yellow (`scheduler_idle_led`): toggled every `scheduler_idle_task()`
  iteration — a coarse scheduler-throughput visualization, not a literal
  idle/priority signal (§19)

### FR-07 — Deliverables

- Complete executable `main.py` and the `ssd1306.py` / `ili9341.py`
  drivers it depends on
- Wokwi circuit definition in `diagram.json`
- Wokwi VS Code configuration in `wokwi.toml`
- This `README.md` and this technical specification
- Shareable GitHub repository URL
- Shareable Wokwi platform URL showing the circuit

## 5. Naming conventions

| Context | Convention | Examples |
|---|---|---|
| Wokwi component IDs | kebab-case | `blue-led-1`, `green-led`, `push-button`, `oled0-display` |
| Python variables | snake_case | `blue_led_1`, `green_led`, `push_button`, `oled0_display` |
| Python pin constants | UPPER_SNAKE_CASE | `BLUE_LED_1_PIN`, `GREEN_LED_PIN`, `BUTTON_PIN`, `OLED0_SCL_PIN`, `OLED0_SDA_PIN` |
| Repository folder | kebab-case | `esp32-asyncio` |

All source code, comments and documentation are written in English.

## 6. Electrical design

### 6.1 Connection table

The full GPIO-to-header connection table and wiring diagrams are kept in
[`docs/hardware-reference.md`](hardware-reference.md), §3, to avoid
maintaining the same pin table in two places.

### 6.2 Button input conditioning

The button input uses the ESP32's internal pull-down resistor:

- an open button produces a defined LOW state;
- a pressed button connects GPIO 17 to 3.3 V and produces HIGH;
- no external pull-down resistor is required.

**Simulated vs. real bounce.** Wokwi's `wokwi-pushbutton` component behaves
as an ideal, bounce-free switch — it does not model mechanical contact
bounce, so a debounce filter is not strictly required to pass the
simulation. The software debounce described in §8 is kept anyway as the
correct, forward-looking behavior for a real physical button, which does
bounce. A physical implementation would also need to account for wiring
quality, cable length and electromagnetic interference that the simulation
does not reproduce.

### 6.3 Why I2C for the OLEDs, and SPI for the TFT

An SSD1306 can exist in I2C or SPI module variants. I2C was fixed for both
OLEDs (SCL GPIO 32 / SDA GPIO 16 on the first, SCL GPIO 15 / SDA GPIO 22 on
the second — one independent hardware bus per OLED, FR-04) because:

1. it uses only two signals per bus, keeping the pin budget low across two
   displays;
2. the Wokwi `board-ssd1306` part used here is the I2C 128 × 64 variant; and
3. their content — two periodically-redrawn bar graphs — does not need SPI's
   higher throughput to stay responsive at a 250 ms refresh floor.

The TFT console (FR-05) is a separate case: it uses genuine 4-wire SPI (SCK,
MOSI, CS, D/C, plus RST), because the ILI9341 controller used here is an SPI
part and because the console's larger 240×320 color frame benefits from
SPI's higher transfer rate. The two interface choices are independent
decisions for two different displays, not a single project-wide constraint.

## 7. Software architecture

### 7.1 Cooperative asynchronous tasks

The application uses `asyncio` exclusively for task scheduling. Thirteen
concurrent flows run under one scheduler:

- `blink_led(entry)` — six independent tasks, one per `BLINKING_LEDS` entry,
  each toggling its own LED on the shared interval (FR-01);
- `scheduler_idle_task()` — one task, toggling the yellow status LED every
  loop iteration (FR-06);
- `update_cpu_graph()` / `update_ram_graph()` — one task per OLED, redrawing
  its resource graph (FR-04);
- `print_status()` — one task, printing the periodic serial status line;
- `monitor_step_button()` — two tasks, one per speed button (FR-03), each
  created with `asyncio.create_task()`;
- `monitor_button()` — the main button's monitor (FR-02), the only one of
  the thirteen that `main()` `await`s directly instead of dispatching with
  `create_task()`; since it never returns, `main()` never completes on its
  own, but this does not distinguish it from the other twelve in scheduling
  behavior.

### 7.2 Why `asyncio` was selected

- Clear separation of independent responsibilities.
- Easier extension with additional sensors, actuators, or communication
  tasks — each becomes one more `asyncio.create_task()` call instead of
  another timestamp/condition block hand-rolled into a growing loop.
- Explicit cooperative pauses through `await asyncio.sleep_ms()`, so the
  a blue LED task never stalls waiting on the button task or an OLED refresh.

**Engineering note — what `asyncio` does *not* solve here:** the `ssd1306`
driver performs a synchronous, blocking I2C write inside `show()` (no
internal `await` points). That write blocks the CPU for the same duration
whether the surrounding code uses `asyncio`, a manual super loop, or nothing
at all. `asyncio` was adopted for scalability and code organization, not to
make the OLED I/O non-blocking — documented explicitly to avoid a later,
incorrect assumption to the contrary.

### 7.3 Rejected alternatives

- **Blocking `time.sleep()` / `time.sleep_ms()`:** stops all script
  progress during the pause, so the button could not be sampled promptly.
- **Manually-timed super loop** (`time.ticks_ms()` / `time.ticks_diff()`
  per task): functionally equivalent at this project's small scope, and
  uses less memory than `asyncio`, but does not scale as cleanly as more
  independent behaviors are added. `time.ticks_ms()` / `time.ticks_diff()`
  remain appropriate *inside* the button coroutine to measure the debounce
  stability window — that local use does not turn the application into a
  manually scheduled super loop.
- **Hardware/virtual `machine.Timer` callback:** unnecessary, since strict
  interrupt-like periodicity is not required here, and OLED transfers must
  not be performed from inside a timer callback.

## 8. Debounce strategy

Although the simulated `wokwi-pushbutton` does not bounce (§6.2), the
button coroutine still implements a non-blocking software debounce so the
behavior is correct on real hardware without any code change:

1. sample GPIO 17 every 5 ms;
2. when a different raw level appears, mark it as a candidate state and
   record the time;
3. restart the candidate timestamp if the raw level changes again before
   being accepted;
4. accept the candidate only once it has remained unchanged for 30 ms;
5. invoke output updates (`apply_button_state()`) only after acceptance.

This avoids a blocking debounce delay and prevents false LED/OLED
transitions, while the 30 ms acceptance window stays imperceptible during
normal manual operation.

## 9. OLED graph update strategy

Both OLEDs redraw on a fixed sampling window — `CPU_GRAPH_SAMPLE_INTERVAL_MS`
/ `RAM_GRAPH_SAMPLE_INTERVAL_MS`, currently 250 ms each — not on a
button-state or other event edge:

- `update_cpu_graph()` and `update_ram_graph()` each run their own
  `while True` loop, redrawing every iteration and then
  `await asyncio.sleep_ms(250)`;
- `asyncio.sleep_ms()` guarantees only a minimum delay, so the sampling
  window is measured with `time.ticks_us()` rather than assumed exact — a
  slower iteration (e.g. a concurrent `console_log()` write) pushes the real
  gap past 250 ms, and `update_cpu_graph()` accounts for that explicitly
  when computing its percentage (§19.2);
- every redraw does a full `fill()` and re-plots the whole scrolling
  history, not just the newest column, since `framebuf` has no primitive
  for shifting existing pixel data left.

This is unconditional periodic redraw, not event-driven update: the two
OLEDs are themselves part of what keeps the processor busy (§19.2's "CPU"
measurement), so redrawing continuously is intentional here, not something
to minimize.

## 10. State model

| Stable state | GPIO 17 | Green LED | Console log line |
|---|---:|---|---|
| Released | LOW | OFF | `Button released -> Green LED OFF` (green) |
| Pressed | HIGH | ON | `Button pressed -> Green LED ON` (green) |

The six blinking-LED tasks, the two OLED graph tasks and the TFT console are
all orthogonal to this state model: none of them pause, restart or change
behavior when the button transitions.

## 11. Startup and failure behavior

At module-load time, before `main()` runs, the application:

1. configures the six blinking LEDs, the green LED, and the two
   status-indicator LEDs as outputs, all off;
2. configures the button pins (`Pin.PULL_DOWN` on `BUTTON_PIN`; external
   pull-downs on the two speed-button pins, per `diagram.json`);
3. creates both OLED I2C buses and scans each for address `0x3C`,
   initializing `oled0_display` / `oled1_display` only where detected;
4. creates the TFT SPI object and attempts `ILI9341(...)` construction,
   catching `OSError` into `tft_display = None` on failure.

Then `main()` logs a startup line, applies the initial button state, resets
the bus-busy accumulator (so `update_cpu_graph()`'s first window isn't
charged with startup-time I/O), and creates all twelve `asyncio.create_task()`
flows before `await`-ing the main button monitor directly (§7.1).

If an OLED is not detected at its expected address, `create_oled_display()`
prints a diagnostic (expected vs. detected addresses) and returns `None`;
`draw_usage_graph()` and `console_log()` both check for `None` and skip
their display write while continuing everything else normally. The TFT's
`None` case is different: because its SPI link is write-only, a missing
panel does not reliably produce an `OSError` at all (§19.4), so this
graceful-degradation path is confirmed to trigger only for driver/wiring
faults that do raise, not for a simply-disconnected TFT.

## 12. Verification plan

### TC-01 — Startup with button released

**Precondition:** button not pressed when the simulation starts.
**Expected:** all six blinking LEDs begin toggling; green LED stays off;
both OLED graphs begin plotting; the TFT console (if present) and the
serial console both show a startup line.

### TC-02 — Press button

**Action:** press and hold the push-button.
**Expected after debounce:** green LED turns on; a green
`Button pressed -> Green LED ON` line appears on the TFT console and on
serial; all six blinking LEDs keep toggling without freezing or a visible
timing glitch.

### TC-03 — Release button

**Action:** release the push-button.
**Expected after debounce:** green LED turns off; a green
`Button released -> Green LED OFF` line appears on both consoles; the
blinking LEDs keep toggling.

### TC-04 — Rapid repeated presses

**Action:** press and release the button several times in quick
succession.
**Expected:** no visible rapid green LED oscillation, and no redundant
console lines beyond one per genuine debounced state change.

### TC-05 — Timing independence

**Action:** press and release the button at different points in the
blinking LEDs' on/off cycle.
**Expected:** the button response remains prompt, and the blinking LEDs
keep their shared toggle interval regardless of when the OLEDs or TFT
redraw (subject to the blocking-write latency documented in §19.2).

### TC-06 — OLED disconnected

**Action:** temporarily remove one OLED's I2C wire in `diagram.json`, run
the simulation, then restore it.
**Expected:** a serial diagnostic identifies the missing address for that
OLED; the other OLED, the TFT, the LEDs and the button all keep working
normally. Restore the correct circuit before further work.

### TC-07 — Boot sanity check (no application code involved)

**Action:** before trusting any application-level debugging, load a
trivial one-GPIO script (e.g. blink a single LED with a plain blocking
loop, no `asyncio`, no OLED, no button) as `main.py` and run it.
**Expected:** the serial monitor shows a single `POWERON_RESET` boot
banner and then the script's own output; the LED blinks.
**Failure signature to watch for:** the console instead shows the ROM
boot banner repeating over and over (`POWERON_RESET` once, then
`SW_RESET` indefinitely) with no application output ever appearing. This
means MicroPython itself never starts — the fault is at the firmware/board
configuration level (see the `attrs.env` decision-log entry in §16), not in
application code, wiring of individual peripherals, or GPIO assignment.
When this signature appears, check `diagram.json`'s `esp32` part `attrs`
for a pinned `env` value first.

### TC-08 — Speed-button interval limits (clamping)

**Action:** press the decrease-speed button (GPIO 34) repeatedly, well
past the point where the blinking LEDs' interval should stop shrinking;
then do the same with the increase-speed button (GPIO 35) in the other
direction.
**Expected:** the interval stops changing once it reaches 125 ms
(fastest, `BLINK_SPEED_STEP_MIN`) or 4 s (slowest,
`BLINK_SPEED_STEP_MAX`) — further presses in the same direction have no
additional effect, confirmed by `print_status()`'s serial line.
**Executed and passed on 2026-08-18 in Wokwi web.** The project author
confirmed that both interval limits and the corresponding serial values
matched the expected result above.

### TC-09 — Simultaneous three-display operation

**Action:** let `main.py` run continuously and observe both OLEDs and
the TFT at the same time for several minutes.
**Expected:** both OLED graphs keep updating on their independent I2C
buses, and the TFT console keeps logging, without one display's write
visibly stalling the others for longer than a single instrumented
draw/transfer call (§19.2); no display silently stops updating while the
others continue.
**Executed and passed on 2026-08-18 in Wokwi web.** The project author
confirmed that all three displays continued operating as expected.

### TC-10 — TFT failure path

**Action:** remove the TFT's SPI wiring (or its GND) in `diagram.json`,
run the simulation, and watch the serial console.
**Expected:** per §19.4, this is not guaranteed to produce a detected
failure — `tft_display` may remain a live object even with no panel
responding, since the SPI link is write-only. What is guaranteed: every
`console_log()` line is still printed to serial regardless, so no event
is silently lost even if the TFT itself never shows anything.
**Executed and passed on 2026-08-18 in Wokwi web.** The project author
confirmed the expected write-only-SPI behavior and preservation of all log
messages on the serial console.

### TC-11 — Long-run LED desynchronization and button-hold latency

**Action:** let `main.py` run continuously, unmodified, for at least
10–15 minutes, watching the six blinking LEDs' relative phase and
periodically pressing the main button.
**Expected:** the six LEDs, nominally sharing one interval, visibly
drift out of phase with each other over that window (§2.1 desync
explanation in the report); occasionally a button press needs to be held
longer than the nominal debounce window to register, especially during
display-heavy periods.
**Executed and passed on 2026-08-18 in Wokwi web.** The project author
confirmed the expected long-run LED phase drift and button latency behavior.

## 13. Wokwi, VS Code and GitHub workflow

The GitHub repository is the version-controlled source of truth. Wokwi
provides two execution surfaces:

1. **Wokwi Web** — the interactive online project used to produce the
   shareable platform/circuit URL (no local setup required).
2. **Wokwi for VS Code** — local simulation using `diagram.json`,
   `wokwi.toml`, a locally downloaded MicroPython firmware image
   (`firmware.bin`, obtained separately per the download steps in
   `wokwi.toml`'s own header comment, and never committed — see
   `.gitignore`), and RFC2217 file transfer
   through `mpremote`.

Both links are required in the README because they serve different
purposes: GitHub exposes source, documentation and history; Wokwi runs the
submitted behavior interactively with no installation.

## 14. Repository contents

| File | Purpose |
|---|---|
| `main.py` | Complete executable application |
| `ssd1306.py` | SSD1306 I2C OLED driver |
| `ili9341.py` | Custom ILI9341 TFT SPI driver (§19.4) |
| `diagram.json` | Wokwi components and electrical connections |
| `wokwi.toml` | Local VS Code simulator configuration (not used by wokwi.com) |
| `firmware.bin` | MicroPython firmware image for local simulation; downloaded separately per developer, never committed (`.gitignore`) |
| `README.md` | Setup, execution, GitHub and sharing guide |
| `LICENSE` | CC0 1.0 Universal legal code |
| `.gitignore` | Excludes downloaded firmware and generated files |
| `docs/technical-specification.md` | This document |
| `docs/component-specifications.md` | Per-component specification sheets (board, display, LEDs, resistors, push-button) |
| `docs/hardware-reference.md` | Board/module identification, GPIO-to-header map, reserved pins, electrical characteristics, wiring checklist |
| `tests/` | Thirteen current-hardware diagnostic scripts, `01_blue_led_basic.py` through `13_tft_text_diagnostic.py` (not part of the deliverable) — see `tests/README.md` |
| `report/` | LaTeX source (`relatorio.tex`), compiled PDF, build script and circuit figure for the (Portuguese-language) technical report — see `report/README.md` |

## 15. Acceptance criteria

The project is accepted when:

- all pin assignments match §4/§6;
- `main.py` starts without errors on the Wokwi MicroPython firmware;
- all six blinking LEDs toggle on their shared interval without blocking or
  being blocked by other tasks beyond the display-write latency documented
  in §19.2;
- the green LED matches the button state per §10;
- the two speed buttons scale the blinking interval within its clamped
  range (FR-03);
- both OLED graphs and the TFT console update per §9 and FR-05;
- no `time.sleep()` blocking delay is used anywhere in `main.py`;
- the Wokwi simulation is saved and shareable by URL; and
- the repository is published on GitHub with both project links in the
  README.

## 16. Design decision log

This table exists so collaborators can append their own decisions,
alternatives considered, or amendments without rewriting the document — add
a row, keep the reasoning short and explicit.

| Decision | Rationale | Alternatives considered |
|---|---|---|
| Numbered blue-LED identifiers in source and circuit | `blue_led_1` through `blue_led_6`, `BLUE_LED_1_PIN` through `BLUE_LED_6_PIN`, and `blue-led-1` through `blue-led-6` state the physical color and preserve one unambiguous ordering across every artifact. | Color-based identifiers unrelated to the current hardware (rejected because they made six blue components appear to have different colors) |
| Wokwi over Tinkercad | Wokwi natively produces both mandatory deliverables: an executable MicroPython `main.py` and a shareable project link. Tinkercad cannot execute MicroPython at all. | A C/C++ Tinkercad sketch alongside the MicroPython version; Tinkercad for the schematic only, no code execution |
| `board-esp32-devkit-c-v4` as the target board | An official Espressif development board supported natively by Wokwi, providing all GPIO pins required by the specification and complete manufacturer documentation. Improves reproducibility and removes ambiguities associated with generic or unofficial ESP32 boards. | Other Wokwi ESP32 board parts (e.g. `board-esp32-devkit-v1`), which one of the original drafts used and which uses different pin-label conventions |
| Cooperative `asyncio` tasks instead of a manual super loop | Scalability and separation of concerns as the project grows (see §7.2). Does **not** make the OLED I2C write non-blocking (§7.2 engineering note). | Manual super loop with `ticks_ms()`/`ticks_diff()` per task (simpler, functionally equivalent here, scales worse) |
| I2C for both OLEDs, SPI for the TFT | Two signals per OLED bus keeps the pin budget low across two displays; the TFT uses genuine SPI instead because its controller is an SPI part with a larger, faster-refreshed frame (§6.3). | SPI for the OLEDs too (rejected: no throughput benefit for two periodically-redrawn bar graphs, at the cost of more pins) |
| Internal pull-down on the button (`Pin.PULL_DOWN`) | Satisfies "HIGH when pressed" without an external resistor. | External 10 kΩ pull-down drawn explicitly in the schematic |
| Software debounce kept despite the simulated button not bouncing | Correct behavior for a future real, physical button (§6.2, §8); zero cost in simulation. | No debounce at all (would need to be added later for real hardware) |
| *(Superseded — see the OLED-graph row below)* OLED redrawn only on button state change | Original rationale: avoided visible flicker and redundant I2C writes for a static button-state message. No longer how either OLED behaves (§9). | Unconditional redraw every loop iteration (this is what both OLEDs do now, deliberately, since they graph a continuously-changing value) |
| Button sampled every 5 ms, accepted after 30 ms stable | Fast enough to feel instantaneous; the 30 ms window is the actual debounce guard, sampling itself is not the filter. | Coarser polling (e.g. 50 ms) with no separate acceptance window — simpler but couples sampling rate to debounce time |
| `machine.I2C` (hardware), not `machine.SoftI2C` | The current CPU OLED diagnostics, `tests/05_cpu_oled_basic.py` and `tests/06_cpu_oled_full_diagnostic.py`, use GPIO32 (SCL) and GPIO16 (SDA) and passed on Wokwi web on 2026-08-18. | `machine.SoftI2C` (previously adopted defensively, now confirmed unnecessary; kept only as a documented fallback if a future hardware-I2C regression appears) |
| `push-button` wired with pin names `1.l` / `2.l` | These are the actual pin names exposed by the Wokwi `wokwi-pushbutton` part. One of the three original drafts used `1.R` / `2.R` (wrong case, wrong side), which Wokwi cannot resolve — the connection silently fails and the button never registers a press in that simulation. | `1.R` / `2.R` naming (rejected: invalid pin reference) |
| `esp32` board part uses `"attrs": {}` (no pinned firmware `env`) | **Confirmed root cause of a live wokwi.com failure**: pinning `"env": "micropython-20240602-v1.23.0"` (carried over from the `p/` draft) caused an infinite boot loop — the console showed repeated `POWERON_RESET` / `SW_RESET` cycles and MicroPython never started, so *nothing* ran, not even a trivial one-GPIO test script (see TC-07). Removing the pin and letting Wokwi select its default/current MicroPython build resolved it. This also retroactively confirms this exact line was very likely the original issue reported against the `p/` draft before consolidation. | Pinning a specific firmware `env` string for reproducibility (rejected: the specific string used was invalid/unsupported and silently broke boot, with no error surfaced other than the reset loop) |
| Both OLEDs plot live resource-usage graphs, not button-state text (§19.2) | User-requested change, after the button-state OLED message (the project's earlier behavior) was already validated. The "CPU" value is real measured time inside the displays' instrumented draw/transfer calls (drawing plus I2C/SPI transfer, not bus transfer alone), a partial approximation kept because bare-metal MicroPython on the ESP32 exposes no OS-level scheduler load metric to read instead — see §19.2 for what it does and doesn't cover. | A synthetic/simulated waveform for "CPU usage" (rejected: would not reflect anything real about the running program); reusing the earlier text message alongside a graph (rejected: no space on a 128×64 monochrome panel without shrinking the graph) |
| Six blinking LEDs share one interval, still six separate `asyncio` tasks (§19.3) | Demonstrates that adding "more of the same" only ever means one more concurrent task, never more shared-loop logic — the same principle FR-01 already establishes for all six LEDs today. | A single task toggling all six LEDs together (rejected: defeats the point of demonstrating independent concurrent equipment, and reintroduces the coupling `asyncio` was adopted to avoid, §7.2) |

## 17. Future work (physical hardware phase, out of scope here)

- A **real, mechanical** push button needs the debounce logic in §8 (and
  optionally a hardware RC filter), since physical contacts bounce and the
  simulated one does not.
- Re-evaluate I2C vs. SPI if the physical build has spare GPIOs and a higher
  display refresh rate becomes a requirement.

## 18. Revision integration guidance

Complementary comments from other designers should be added through
reviewed commits. Proposed changes should identify whether they affect:

- mandatory requirements;
- electrical assumptions;
- timing or concurrency;
- simulator compatibility;
- documentation only; or
- a future physical implementation.

Mandatory pin mappings and user-visible messages must not be changed
without an explicit update to the assessment requirements.

## 19. Implementation notes

This section expands on implementation detail for the requirements in §4,
beyond what fits in a single FR entry. §16's decision log carries the short
rationale behind each choice described here.

### 19.1 Two independent OLED I2C buses

The CPU OLED0 (`oled0-display` / `oled0_display`) runs on
`machine.I2C(0)`, GPIO32 (SCL) / GPIO16 (SDA). The RAM OLED1
(`oled1-display` / `oled1_display`) runs on its own independent hardware
I2C bus, `machine.I2C(1)`, GPIO15 (SCL) / GPIO22 (SDA) — not a second
address on the first bus — so both are addressed concurrently without bus
contention.

### 19.2 What the two OLED graphs plot

Both OLEDs are Task-Manager-style scrolling bar graphs, one sample per
horizontal pixel column (up to 128 samples of history), redrawn every
sampling window:

- **OLED0 — labeled "CPU."** MicroPython on bare ESP32 exposes no
  OS-level scheduler load metric, so the plotted value is a partial,
  approximate stand-in, not a full CPU utilization metric: the fraction
  of each ≥250 ms sampling window (a floor, not an exact period — see
  `update_cpu_graph()`'s own timing comment) spent inside the three
  displays' instrumented synchronous calls, timed end-to-end by
  `_bus_busy_begin()` / `_bus_busy_end()`. That span covers both the
  Python-side framebuffer/drawing work (`draw_usage_graph()`'s per-column
  loop, `ili9341.py`'s glyph-to-pixel conversion) and the I2C/SPI transfer
  itself — it is not a pure bus-transfer measurement. It also does not
  cover every source of CPU use: button debounce sampling,
  `scheduler_idle_task()`'s own bookkeeping, `print_status()`'s
  formatting, and the rest of the Python code all consume CPU time
  outside this window. The `CPU` label was kept (rather than renamed to
  something like `DISPLAY`) because it is already consolidated across the
  serial status line, the TFT console color scheme, and this
  documentation, and fits the OLED's small screen — see `main.py`'s
  `update_cpu_graph()` docstring for the full caveat.
- **OLED1 — labeled "RAM."** A real measured value, not a
  simulated one, but scoped to MicroPython's own garbage-collector heap
  statistics (`gc.mem_alloc()` / `gc.mem_free()`), sampled every ≥250 ms
  — not total physical RAM on the ESP32. The execution stack, native/C
  allocations internal to the firmware, and anything outside the
  gc-managed heap are not included. See `update_ram_graph()`.

The push-button's state is logged through `console_log()` (§19.4), not a
text message on either OLED, since neither has room left for both a graph
and a legible text message on a 128×64 monochrome panel.

### 19.3 Six LEDs, one shared interval, six independent tasks

All six LEDs (red, blue, yellow, white, orange, and a second red) are
painted the same color on the board (`#0000FF`) even though `main.py`
still tracks each one individually (see `BLINKING_LEDS`). Each runs as its
own independent `asyncio` task (`blink_led()`) — one more LED is always
one more concurrent task, never more logic added to a shared loop.

### 19.4 TFT log console, write-only SPI, and the serial-mirroring decision

The ILI9341 TFT uses genuine 4-wire SPI (SCK, MOSI, CS, D/C, plus a reset
line — GPIO 18/23/5/21/19). Unlike the two
OLEDs' graphs, the TFT (`tft_display`, driven by `ili9341.py`) works as a
scrolling, colored activity log: `console_log()` writes one line per
system event, one color per subsystem, wrapping back to the top of the
screen once it fills (no true scrolling).

This SPI link is write-only: it has no MISO line, and `ili9341.py` never
reads anything back from the panel (no ID query, no status read).
`create_tft_display()` therefore only returns `None` when constructing
the `ILI9341` object itself raises `OSError` — a driver/peripheral-level
failure, not general "TFT missing" detection. A physically disconnected
but electrically quiet panel very likely raises nothing at all, leaving
`tft_display` a live object with no real display listening on the bus.

Because that detection is unreliable, `console_log()` does not gate its
serial fallback on `tft_display is None`: every line is printed to the
serial console unconditionally, in addition to being written to the TFT
when one is present. This is the one fallback that actually covers a
physically-missing-but-electrically-silent panel, which an
`is None` check alone cannot.

`console_log()`'s text rendering (`ili9341.py`'s `text()`) also went
through a performance pass: the initial implementation converted each
glyph to individual pixels via `framebuf.FrameBuffer.pixel()`, up to
~1920 calls per line of text. The current version precomputes, once per
text/background color pair, a 256-entry lookup table from byte value to
the corresponding 16 RGB565 bytes for that 8-pixel glyph slice, and reuses
it per character rendered.
