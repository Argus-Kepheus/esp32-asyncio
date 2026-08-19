# ESP32 Asyncio Playground

![Simulated circuit: ESP32-DevKitC V4, two SSD1306 OLEDs, an ILI9341 TFT, six blue LEDs, a green LED, two state-indicator LEDs (orange and yellow), three push-buttons and a slide switch](report/figures/circuito-wokwi.png)

Personal ESP32 (MicroPython) project exploring asynchronous (`asyncio`)
processing, originally a practical assessment for the Instrumentation,
Electronics and Programming Logic courses. Six independently-blinking
LEDs, a push-button driving a green LED, two activity-indicator LEDs,
two SSD1306 OLEDs plotting live CPU/RAM graphs, and an ILI9341 TFT log
console.

**Full documentation:** [English](docs/EN/README.md) · [Português](docs/PT/README.md)

**Technical report (Portuguese):** [`report/relatorio.pdf`](report/relatorio.pdf)

**Wokwi simulation:** <https://wokwi.com/projects/471528241540407297>

## Quick start

1. Open the Wokwi link or import `diagram.json`, `main.py`, `ili9341.py`,
   `ssd1306.py` and `wokwi.toml` into a MicroPython ESP32 Wokwi project.
2. Start the simulation.
3. Press the main button to toggle the green LED; use the two speed buttons
   to speed up or slow down all six blue LEDs together.
4. Watch the live CPU/RAM graphs on the two OLEDs and the event log on the
   TFT; the serial console prints the same figures once a second.

## Structure

| Path | Content |
|---|---|
| `main.py` | Main MicroPython/`asyncio` firmware |
| `ili9341.py`, `ssd1306.py` | Display drivers |
| `diagram.json` | Circuit and layout for Wokwi |
| `wokwi.toml` | Local Wokwi-for-VS-Code simulator config |
| `docs/PT/` and `docs/EN/` | Bilingual technical documentation |
| `tests/` | Manual hardware diagnostic scripts |
| `report/` | Technical report in LaTeX and PDF |

## Validation

The `tests/` folder contains standalone scripts that isolate individual
components (each LED, each button, each display) rather than exercising
`main.py` as a whole. They are manual diagnostics for Wokwi or a physical
board, not automated proof that `main.py` passes — see
[`tests/README.md`](tests/README.md) for the recommended run order and
recorded results.

## Limitations

The CPU and RAM graphs are approximations: "CPU usage" only reflects time
spent inside the displays' instrumented draw/transfer calls, and "RAM usage"
reflects MicroPython heap usage, not total physical RAM — see `main.py`'s
module docstring and `docs/EN/technical-specification.md` for the full
rationale. The button debounce is tuned for Wokwi's simulated, bounce-free
contacts; a real mechanical button would need the debounce logic already
described in the technical specification.

**License:** CC0 1.0 Universal — see [`LICENSE`](LICENSE).
