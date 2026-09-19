# ESP32 Asyncio Playground

![Simulated circuit: ESP32-DevKitC V4, two SSD1306 OLEDs, an ILI9341 TFT, six blue LEDs, a green LED, two state-indicator LEDs (orange and yellow), three push-buttons and a slide switch](report/figures/circuito-wokwi.png)

Personal ESP32 (MicroPython) project exploring asynchronous (`asyncio`)
processing, originally a practical assessment for the Instrumentation,
Electronics and Programming Logic courses. Six independently-blinking
LEDs, a push-button driving a green LED, two activity-indicator LEDs,
two SSD1306 OLEDs plotting live CPU/RAM graphs, and an ILI9341 TFT log
console.

**Full documentation:** [English](docs/EN/README.md) · [Português](docs/PT/README.md) · [Español](docs/ES/README.md)

**Technical report (Portuguese):** [`report/relatorio.pdf`](report/relatorio.pdf)

**Wokwi simulation:** <https://wokwi.com/projects/471528241540407297>

## Quick start

1. Open the Wokwi link or import `diagram.json`, `main.py`, `ili9341.py`,
   `ssd1306.py`, `lib/__init__.py`, `lib/generated_config.py` and
   `wokwi.toml` into a MicroPython ESP32 Wokwi project.
2. Start the simulation.
3. Press and hold the main button to turn the green LED on (release it to turn the LED off); use the two speed buttons
   to speed up or slow down all six blue LEDs together.
4. Watch the live CPU/RAM graphs on the two OLEDs and the event log on the
   TFT; the serial console prints the same figures once a second.

## Structure

| Path | Content |
|---|---|
| `main.py` | Main MicroPython/`asyncio` orchestrator; consumes generated configuration |
| `ili9341.py`, `ssd1306.py` | Display drivers kept at root for the established Wokwi/mpremote workflow |
| `diagram.json` | Circuit and layout for Wokwi |
| `wokwi.toml` | Local Wokwi-for-VS-Code simulator config |
| `config/` | Canonical hardware/runtime configuration |
| `lib/` | Explicit MicroPython support package; contains generated runtime configuration |
| `tools/` | Configuration/document generation and repository validation |
| `docs/EN/`, `docs/PT/`, `docs/ES/` | Multilingual technical documentation governed by `docs/metadata.json` |
| `diagnostics/` | Manual Wokwi/physical-hardware diagnostic scripts |
| `tests/` | Host-side automated `unittest` suite |
| `report/` | Technical report in LaTeX and PDF |

## Validation

Validation has two deliberately separate layers:

- `tests/` contains automated host-side CPython tests for configuration
  generation, multilingual documentation contracts and static source
  invariants. Run them with
  `python -m unittest discover -s tests -p "test_*.py" -v`.
- `diagnostics/` contains manual Wokwi/physical-hardware checks for
  individual components. They require observed simulator/hardware behavior
  and remain necessary because host-side tests do not execute MicroPython
  peripherals.

See [`tests/README.md`](tests/README.md) and
[`diagnostics/README.md`](diagnostics/README.md).

## Limitations

The CPU and RAM graphs are approximations: "CPU usage" only reflects time
spent inside the displays' instrumented draw/transfer calls, and "RAM usage"
reflects MicroPython heap usage, not total physical RAM — see `main.py`'s
module docstring and `docs/EN/technical-specification.md` for the full
rationale. The button debounce is tuned for Wokwi's simulated, bounce-free
contacts; a real mechanical button would need the debounce logic already
described in the technical specification.

**License:** CC0 1.0 Universal — see [`LICENSE`](LICENSE).


Documentation governance and multilingual parity are defined in [`docs/README.md`](docs/README.md) and [`docs/metadata.json`](docs/metadata.json).
