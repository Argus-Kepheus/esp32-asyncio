<!-- doc-id: project-overview -->
<!-- language: ES -->
<!-- content-revision: 4 -->

# esp32-asyncio

**Idioma:** [English](../EN/README.md) | [Português](../PT/README.md) | [Español](README.md)

Proyecto personal con ESP32 y MicroPython para explorar procesamiento asíncrono
con `asyncio`, originado como evaluación práctica de Instrumentación,
Electrónica y Lógica de Programación. Incluye seis LED que parpadean de forma
independiente, un pulsador que controla un LED verde, dos LED de actividad,
dos OLED SSD1306 con gráficos en vivo de CPU/RAM y una TFT ILI9341 usada como
consola de eventos, todo simulado en Wokwi.

**Simulación Wokwi:** <https://wokwi.com/projects/471528241540407297>

<!-- section: hardware-requirements -->
## Requisitos de hardware

<!-- BEGIN GENERATED: hardware-overview -->
| Componente | Identificador de Wokwi | Pin del ESP32 |
|---|---|---:|
| Placa — ESP32-DevKitC V4 | board-esp32-devkit-c-v4 | — |
| Seis LED intermitentes (+ 220 Ω) | `blue-led-1` … `blue-led-6` | GPIO 26, 14, 27, 25, 33, 12 |
| LED verde (+ 220 Ω) | `green-led` | GPIO 4 |
| Pulsador principal | `push-button` | GPIO 17 |
| Dos pulsadores de velocidad (+ pull-down externo de 10000 Ω cada uno) | `decrease-speed-button`, `increase-speed-button` | GPIO 34, 35 |
| Dos LED indicadores de estado (+ 220 Ω cada uno) | `bus-idle-led`, `scheduler-idle-led` | GPIO 13, 2 |
| OLED0 de CPU, SSD1306 128×64, I2C(0) @ 0x3C | `oled0-display` | SCL = GPIO 32, SDA = GPIO 16 |
| OLED1 de RAM, SSD1306 128×64, I2C(1) @ 0x3C | `oled1-display` | SCL = GPIO 15, SDA = GPIO 22 |
| Pantalla TFT de registro, ILI9341 240×320, SPI | `tft-display` | SCK 18, MOSI 23, CS 5, D/C 21, RST 19 |
<!-- END GENERATED: hardware-overview -->

Los dos OLED y los tres pulsadores usan la alimentación de 3,3 V de la placa;
la TFT usa la alimentación definida en la configuración canónica. Todos los
componentes comparten GND. Los detalles eléctricos, conectores, pines
restringidos y lista de verificación física están en
[`hardware-reference.md`](hardware-reference.md); los identificadores y el
papel de cada componente están en
[`component-specifications.md`](component-specifications.md).

<!-- section: software-requirements -->
## Requisitos de software

- MicroPython para ESP32.
- `main.py` importa los valores canónicos de ejecución desde
  `lib/generated_config.py`; después de cambiar `config/`, regenere ese
  archivo con `tools/generate_config.py`.
- `main.py` ejecuta trece flujos concurrentes de `asyncio`: seis tareas
  para los LED intermitentes, el indicador del planificador, dos tareas OLED,
  una tarea de estado serial y tres monitores de pulsadores.
- La configuración eléctrica y de pull de los pulsadores es canónica en
  `config/hardware.json`; el antirrebote y los tiempos son canónicos en
  `config/runtime.json`.
- Los OLED usan I2C con `ssd1306.py`; la TFT usa SPI con el controlador
  propio `ili9341.py`.

Los requisitos completos y las decisiones de diseño están en
[`technical-specification.md`](technical-specification.md).

<!-- section: result -->
## Resultado

Los seis LED parpadean de forma independiente con un intervalo compartido y
ajustable mediante pulsadores; el pulsador principal controla el LED verde y
registra cada transición en la TFT y en la consola serial; los OLED muestran
gráficos de CPU y RAM; y los dos LED de estado reflejan actividad de los
buses de pantalla y del planificador.

<!-- section: license -->
## Licencia

El proyecto se dedica al dominio público mediante **CC0 1.0 Universal**.
Consulte [`LICENSE`](../../LICENSE).
