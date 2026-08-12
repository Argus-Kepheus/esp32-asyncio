# Technical Specification — cess-uff

## 1. Document control

| Field | Value |
|---|---|
| Project | CESS-UFF ESP32 MicroPython Practical Assessment |
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

1. blinks a red LED at a fixed interval;
2. reads a normally-open, active-high push-button;
3. controls a green LED according to the button state; and
4. dynamically changes an SSD1306 OLED message according to that same
   state.

The mandatory deliverables are a complete executable `main.py`, this
repository published on GitHub, and a shareable Wokwi platform link showing
the simulated circuit.

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

### FR-01 — Independent red LED

- Component ID: `red-led` · Python variable: `red_led` · Pin constant: `RED_LED_PIN`
- GPIO: 2 · Direction: digital output
- Behavior: toggle continuously every 500 ms (≈1 s full cycle)
- Constraint: must never block, and must never be blocked by, the button,
  green LED, or OLED logic

### FR-02 — Green LED

- Component ID: `green-led` · Python variable: `green_led` · Pin constant: `GREEN_LED_PIN`
- GPIO: 4 · Direction: digital output
- Button released → OFF · Button pressed → ON

### FR-03 — Push-button

- Component ID: `push-button` · Python variable: `push_button` · Pin constant: `BUTTON_PIN`
- GPIO: 17 · Type: normally-open momentary push-button
- Released electrical state: LOW · Pressed electrical state: HIGH
- Input mode: `Pin.IN` with internal `Pin.PULL_DOWN`

### FR-04 — OLED communication

- Component ID: `oled-display` · Python variable: `oled_display`
- Controller: SSD1306 · Resolution: 128 × 64 · Interface: I2C · Address: `0x3C`
- SCL: GPIO 25 · SDA: GPIO 16 · Supply: 3.3 V and GND

The original assignment only requires the OLED to show the messages
according to the button state — it does not specify a communication
interface or pins. The I2C interface and the GPIO 25 (SCL) / GPIO 16 (SDA)
mapping were fixed by the candidate before development started, not chosen
through an optimization study, and then treated as a fixed predefined
assignment for the rest of the project (see §6.3).

### FR-05 — OLED content

- Stable button released → display exactly `Boa sorte!`
- Stable button pressed → display exactly `Consegui`
- Content updates dynamically on every state change.
- The initial display must match the physical button state at startup.

### FR-06 — Deliverables

- Complete executable `main.py` and the `ssd1306.py` driver it depends on
- Wokwi circuit definition in `diagram.json`
- Wokwi VS Code configuration in `wokwi.toml`
- This `README.md` and this technical specification
- Shareable GitHub repository URL
- Shareable Wokwi platform URL showing the circuit

## 5. Naming conventions

| Context | Convention | Examples |
|---|---|---|
| Wokwi component IDs | kebab-case | `red-led`, `green-led`, `push-button`, `oled-display` |
| Python variables | snake_case | `red_led`, `green_led`, `push_button`, `oled_display` |
| Python pin constants | UPPER_SNAKE_CASE | `RED_LED_PIN`, `GREEN_LED_PIN`, `BUTTON_PIN`, `OLED_SCL_PIN`, `OLED_SDA_PIN` |
| Repository folder | kebab-case | `cess-uff` |

All source code, comments and documentation are written in English. The two
OLED display strings (`Boa sorte!` / `Consegui`) are a deliberate
exception, kept in Portuguese per the assignment's explicit requirement.

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

### 6.3 OLED interface limitation

An SSD1306 can exist in I2C or SPI module variants. SPI needs more signals
(SCK, MOSI, CS, D/C, optionally RESET) and offers higher transfer
throughput, but that option is unavailable here because:

1. the project explicitly assigns only two communication pins;
2. GPIO 25 is predefined as SCL and GPIO 16 as SDA; and
3. the Wokwi `board-ssd1306` part used here is the I2C 128 × 64 variant.

For two short, static messages, I2C bandwidth is adequate.

## 7. Software architecture

### 7.1 Cooperative asynchronous tasks

The application uses `asyncio` exclusively for task scheduling:

- `blink_red_led()` — periodic, unconditional red LED toggling;
- `monitor_button()` — button sampling, state-change detection, and
  synchronizing the green LED and OLED.

### 7.2 Why `asyncio` was selected

- Clear separation of independent responsibilities.
- Easier extension with additional sensors, actuators, or communication
  tasks — each becomes one more `asyncio.create_task()` call instead of
  another timestamp/condition block hand-rolled into a growing loop.
- Explicit cooperative pauses through `await asyncio.sleep_ms()`, so the
  red LED task never stalls waiting on the button task or an OLED refresh.

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

## 9. Dynamic OLED update strategy

The OLED frame buffer is transferred only:

- once during initialization (matching the physical button state at
  startup); and
- after a debounced button-state transition.

The display is never cleared and redrawn on every poll cycle while the
state is unchanged. This event-driven approach reduces I2C traffic,
processor usage and cooperative-task latency, and avoids visible flicker
from repeated clear/draw cycles.

## 10. State model

| Stable state | GPIO 17 | Green LED | OLED message |
|---|---:|---|---|
| Released | LOW | OFF | `Boa sorte!` |
| Pressed | HIGH | ON | `Consegui` |

The red LED task is orthogonal to this state model and keeps toggling every
500 ms in both states.

## 11. Startup and failure behavior

At startup, the application:

1. configures both LEDs as outputs and turns them off;
2. configures GPIO 17 with `Pin.PULL_DOWN`;
3. creates the I2C bus on the mandatory OLED pins and scans for address
   `0x3C`;
4. initializes the display if the address is detected;
5. applies the current physical button state to the LED/OLED outputs; and
6. starts the red LED task and the button-monitoring task.

If the OLED is not detected at the expected address, the program prints a
diagnostic (expected vs. detected addresses) and keeps the LED and button
logic running normally. This graceful degradation is a debugging aid; it
does not replace the requirement for a correctly wired OLED in the
submitted simulation.

## 12. Verification plan

### TC-01 — Startup with button released

**Precondition:** button not pressed when the simulation starts.
**Expected:** red LED begins toggling; green LED stays off; OLED shows
`Boa sorte!`.

### TC-02 — Press button

**Action:** press and hold the push-button.
**Expected after debounce:** green LED turns on; OLED changes once to
`Consegui`; red LED keeps toggling without freezing or a visible timing
glitch.

### TC-03 — Release button

**Action:** release the push-button.
**Expected after debounce:** green LED turns off; OLED changes once back to
`Boa sorte!`; red LED keeps toggling.

### TC-04 — Rapid repeated presses

**Action:** press and release the button several times in quick
succession.
**Expected:** no visible rapid green LED oscillation, and no redundant OLED
refreshes beyond one per genuine state change.

### TC-05 — Timing independence

**Action:** press and release the button at different points in the red
LED's on/off cycle.
**Expected:** the button/display response remains prompt, and the red LED
keeps its ≈500 ms toggle interval regardless of when the OLED redraws.

### TC-06 — OLED disconnected

**Action:** temporarily remove an OLED I2C wire in `diagram.json`, run the
simulation, then restore it.
**Expected:** a serial diagnostic identifies the missing address; LED and
button logic keep working. Restore the correct circuit before final
submission.

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

## 13. Wokwi, VS Code and GitHub workflow

The GitHub repository is the version-controlled source of truth. Wokwi
provides two execution surfaces:

1. **Wokwi Web** — the interactive online project used to produce the
   shareable platform/circuit URL (no local setup required).
2. **Wokwi for VS Code** — local simulation using `diagram.json`,
   `wokwi.toml`, a locally downloaded MicroPython firmware image, and
   RFC2217 file transfer through `mpremote`.

Both links are required in the README because they serve different
purposes: GitHub exposes source, documentation and history; Wokwi runs the
submitted behavior interactively with no installation.

## 14. Repository contents

| File | Purpose |
|---|---|
| `main.py` | Complete executable application |
| `ssd1306.py` | SSD1306 I2C OLED driver |
| `diagram.json` | Wokwi components and electrical connections |
| `wokwi.toml` | Local VS Code simulator configuration (not used by wokwi.com) |
| `README.md` | Setup, execution, GitHub and sharing guide |
| `LICENSE` | CC0 1.0 Universal legal code |
| `.gitignore` | Excludes downloaded firmware and generated files |
| `docs/technical-specification.md` | This document |
| `docs/component-specifications.md` | Per-component specification sheets (board, display, LEDs, resistors, push-button) |
| `docs/hardware-reference.md` | Board/module identification, GPIO-to-header map, reserved pins, electrical characteristics, wiring checklist |
| `tests/` | Standalone per-component diagnostic scripts (not part of the deliverable) — see `tests/README.md` |

## 15. Acceptance criteria

The project is accepted when:

- all pin assignments match §4/§6;
- `main.py` starts without errors on the Wokwi MicroPython firmware;
- the red LED toggles every 500 ms without blocking or being blocked by
  other behaviors;
- the green LED and OLED match the button state per §10;
- no `time.sleep()` blocking delay is used anywhere;
- the OLED is updated only on initialization or on a state change, per §9;
- the Wokwi simulation is saved and shareable by URL; and
- the repository is published on GitHub with both project links in the
  README.

## 16. Design decision log

This table exists so collaborators can append their own decisions,
alternatives considered, or amendments without rewriting the document — add
a row, keep the reasoning short and explicit.

| Decision | Rationale | Alternatives considered |
|---|---|---|
| Wokwi over Tinkercad | Wokwi natively produces both mandatory deliverables: an executable MicroPython `main.py` and a shareable project link. Tinkercad cannot execute MicroPython at all. | A C/C++ Tinkercad sketch alongside the MicroPython version; Tinkercad for the schematic only, no code execution |
| `board-esp32-devkit-c-v4` as the target board | An official Espressif development board supported natively by Wokwi, providing all GPIO pins required by the specification and complete manufacturer documentation. Improves reproducibility and removes ambiguities associated with generic or unofficial ESP32 boards. | Other Wokwi ESP32 board parts (e.g. `board-esp32-devkit-v1`), which one of the original drafts used and which uses different pin-label conventions |
| Cooperative `asyncio` tasks instead of a manual super loop | Scalability and separation of concerns as the project grows (see §7.2). Does **not** make the OLED I2C write non-blocking (§7.2 engineering note). | Manual super loop with `ticks_ms()`/`ticks_diff()` per task (simpler, functionally equivalent here, scales worse) |
| I2C (2 wires: SCL = GPIO 25, SDA = GPIO 16) for the OLED | Imposed by the project's own pin specification, not chosen for technical superiority (§6.3). | SPI (4–5 lines), faster refresh but unavailable under the 2-pin constraint |
| Internal pull-down on the button (`Pin.PULL_DOWN`) | Satisfies "HIGH when pressed" without an external resistor. | External 10 kΩ pull-down drawn explicitly in the schematic |
| Software debounce kept despite the simulated button not bouncing | Correct behavior for a future real, physical button (§6.2, §8); zero cost in simulation. | No debounce at all (would need to be added later for real hardware) |
| OLED redrawn only on button state change, not every poll cycle | Avoids visible flicker and redundant I2C writes (§9). | Unconditional redraw every loop iteration |
| Button sampled every 5 ms, accepted after 30 ms stable | Fast enough to feel instantaneous; the 30 ms window is the actual debounce guard, sampling itself is not the filter. | Coarser polling (e.g. 50 ms) with no separate acceptance window — simpler but couples sampling rate to debounce time |
| `machine.I2C` (hardware), not `machine.SoftI2C` | **Confirmed on a live wokwi.com run**: `tests/05_oled_basic.py` and `tests/06_oled_full_diagnostic.py`, both using hardware `I2C(0, scl=Pin(25), sda=Pin(16), freq=400_000)`, passed — including every `ssd1306.py` drawing primitive. This retroactively shows hardware I2C was never actually the cause of the original wokwi.com issues (the real cause was the `attrs.env` boot loop, see the row below); `SoftI2C` had been adopted earlier as an unconfirmed, purely defensive substitute and is no longer needed. `main.py` was reverted to hardware `I2C` accordingly. | `machine.SoftI2C` (previously adopted defensively, now confirmed unnecessary; kept only as a documented fallback if a future hardware-I2C regression appears) |
| `push-button` wired with pin names `1.l` / `2.l` | These are the actual pin names exposed by the Wokwi `wokwi-pushbutton` part. One of the three original drafts used `1.R` / `2.R` (wrong case, wrong side), which Wokwi cannot resolve — the connection silently fails and the button never registers a press in that simulation. | `1.R` / `2.R` naming (rejected: invalid pin reference) |
| `esp32` board part uses `"attrs": {}` (no pinned firmware `env`) | **Confirmed root cause of a live wokwi.com failure**: pinning `"env": "micropython-20240602-v1.23.0"` (carried over from the `p/` draft) caused an infinite boot loop — the console showed repeated `POWERON_RESET` / `SW_RESET` cycles and MicroPython never started, so *nothing* ran, not even a trivial one-GPIO test script (see TC-07). Removing the pin and letting Wokwi select its default/current MicroPython build resolved it. This also retroactively confirms this exact line was very likely the original issue reported against the `p/` draft before consolidation. | Pinning a specific firmware `env` string for reproducibility (rejected: the specific string used was invalid/unsupported and silently broke boot, with no error surfaced other than the reset loop) |

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
