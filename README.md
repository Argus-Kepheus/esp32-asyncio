# esp32-asyncio

Personal ESP32 (MicroPython) project exploring asynchronous (`asyncio`)
processing, originally a practical assessment for the Instrumentation,
Electronics and Programming Logic courses. Six independently-blinking
LEDs, a push-button driving a green LED, two activity-indicator LEDs,
two SSD1306 OLEDs plotting live CPU/RAM graphs, and an ILI9341 TFT log
console.

> **Project status:** the original mandatory assessment (two LEDs, a
> push-button, one OLED showing button-state text) is complete and its
> pin assignments still traceable in the docs, but its OLED/message
> behavior was later superseded — not just extended — by the hardware
> above, added at the user's request. See `technical-specification.md`'s
> "Extended features" section ([English](docs/EN/technical-specification.md) ·
> [Português](docs/PT/technical-specification.md)) for the full current
> state, and [`report/relatorio.pdf`](report/relatorio.pdf) for the
> standalone (Portuguese-language) technical report describing this
> project directly.

**Full documentation:** [English](docs/EN/README.md) · [Português](docs/PT/README.md)

**Wokwi simulation:** <https://wokwi.com/projects/471528241540407297>

![Simulated circuit: ESP32-DevKitC V4, two SSD1306 OLEDs, an ILI9341 TFT, six blue LEDs, a green LED, two state-indicator LEDs (orange and yellow), three push-buttons and a slide switch](report/figures/circuito-wokwi.png)

**License:** CC0 1.0 Universal — see [`LICENSE`](LICENSE).