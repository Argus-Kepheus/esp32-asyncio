<!-- doc-id: component-specifications -->
<!-- language: ES -->
<!-- content-revision: 4 -->

# Especificaciones de componentes — esp32-asyncio

Este documento reúne una ficha por componente físico/simulado usado en
`diagram.json`. Se mantiene separado de la justificación de diseño de
`technical-specification.md` para que identidad, función eléctrica e
identificador de Wokwi puedan consultarse sin ambigüedad.

Cada ficha describe el componente tal como se utiliza en este proyecto. Si una
revisión futura necesita más detalle, debe ampliarse la ficha existente en vez
de crear una fuente técnica paralela.

> Los GPIO, buses, direcciones, valores de resistencias, configuración de pull
> y alimentaciones actuales son canónicos en `config/hardware.json` y se
> presentan de forma generada en `hardware-reference.md`. Este documento no
> duplica deliberadamente esos valores.

Para la posición física de los GPIO en los conectores, pines reservados,
compatibilidad WROOM/WROVER, características eléctricas y lista de
verificación de montaje, consulte
[`hardware-reference.md`](hardware-reference.md).

<!-- section: microcontroller-board -->
## 1. Placa microcontroladora — ESP32-DevKitC V4

La identidad actual de la placa, módulo recomendado, disposición de conectores,
familia de firmware y tensión lógica se generan desde
`config/hardware.json` en [`hardware-reference.md`](hardware-reference.md),
§1.

La placa de Wokwi deja `attrs.env` sin fijar. Una revisión anterior fijaba
`"micropython-20240602-v1.23.0"`, lo que provocó un ciclo infinito de
reinicio en wokwi.com; retirar ese valor no soportado restauró el arranque
normal de MicroPython. La justificación de selección permanece en
`technical-specification.md`, §3.1.

### Pines usados en este proyecto

El mapa completo y actual GPIO→conector es la tabla generada de
[`hardware-reference.md`](hardware-reference.md), §3. No se duplica aquí.

<!-- section: displays -->
## 2. Pantallas — OLED SSD1306 y TFT ILI9341

### 2.1 OLED SSD1306 (×2)

| Campo | OLED0 CPU | OLED1 RAM |
|---|---|---|
| Pantalla | OLED monocromo SSD1306, 128 × 64 | OLED monocromo SSD1306, 128 × 64 |
| Identificador de Wokwi | `board-ssd1306` | `board-ssd1306` |
| id en `diagram.json` | `oled0-display` | `oled1-display` |
| Interfaz utilizada | I2C; existen variantes SPI que no se usan aquí (§6.3) | I2C |
| Controlador | `ssd1306.py` (clase `SSD1306_I2C`), compartido | el mismo |
| Función en `main.py` | gráfico de recurso "CPU" (`update_cpu_graph()`) | gráfico de recurso "RAM" (`update_ram_graph()`) |

Diagnósticos aislados actuales:
`diagnostics/05_cpu_oled_basic.py` /
`diagnostics/06_cpu_oled_full_diagnostic.py` para OLED0 y
`diagnostics/11_ram_oled_basic.py` para OLED1. Un diagnóstico aislado no
demuestra por sí solo el funcionamiento concurrente de ambos buses.

### 2.2 TFT ILI9341

| Campo | Valor |
|---|---|
| Pantalla | TFT en color ILI9341, 240 × 320 |
| Identificador de Wokwi | `wokwi-ili9341` |
| id en `diagram.json` | `tft-display` |
| Interfaz | SPI real de 4 hilos (SCK, MOSI, CS, D/C) más RST |
| Profundidad de color | RGB565 de 16 bits |
| Controlador | `ili9341.py`, clase propia `ILI9341` |
| Función en `main.py` | registro de actividad con desplazamiento lógico (`console_log()`) |

Diagnósticos aislados actuales: `diagnostics/12_tft_basic.py` y
`diagnostics/13_tft_text_diagnostic.py`.

<!-- section: leds -->
## 3. LED

Hay nueve LED. Los seis LED intermitentes son físicamente azules en
`diagram.json` y mantienen la numeración 1–6 en circuito y código.

| Campo | LED intermitentes (×6) | LED verde | LED bus inactivo | LED planificador |
|---|---|---|---|---|
| Identificador de Wokwi | `wokwi-led` | `wokwi-led` | `wokwi-led` | `wokwi-led` |
| ids en `diagram.json` | `blue-led-1` a `blue-led-6` | `green-led` | `bus-idle-led` | `scheduler-idle-led` |
| Color | `#0000FF` | `green` | `orange` | `yellow` |
| Comportamiento | cada uno alterna independientemente (FR-01) | refleja el estado antirrebote del pulsador (FR-02) | encendido por defecto y apagado durante escritura instrumentada (FR-06) | alterna en cada iteración de `scheduler_idle_task()` (FR-06) |

<!-- section: series-resistors -->
## 4. Resistencias

| Campo | Resistencias de LED | Pull-down de pulsadores de velocidad |
|---|---|---|
| Identificador de Wokwi | `wokwi-resistor` | `wokwi-resistor` |
| Finalidad | limitación de corriente | pull-down externo para entradas que lo requieren |

<!-- section: push-buttons -->
## 5. Pulsadores

| Campo | Pulsador principal | Pulsadores de velocidad (×2) |
|---|---|---|
| Identificador de Wokwi | `wokwi-pushbutton` | `wokwi-pushbutton` |
| id en `diagram.json` | `push-button` | `decrease-speed-button`, `increase-speed-button` |
| Tipo | normalmente abierto, momentáneo, cuatro terminales | igual |
| Nombres válidos de pines | `1.l`, `1.r`, `2.l`, `2.r` | igual |
| Tecla de simulación | espacio | `a` (disminuir), `s` (aumentar) |

> Una versión anterior utilizó `1.R` / `2.R`, nombres que Wokwi no
> resuelve. Deben emplearse exactamente los nombres de pines indicados arriba.

<!-- section: flash-mode-switch -->
## 6. Interruptor deslizante de modo de grabación

| Campo | Valor |
|---|---|
| Identificador de Wokwi | `wokwi-slide-switch` |
| id en `diagram.json` | `flash-mode-switch` |
| Función | selección del modo de arranque del bootloader ROM; `main.py` no lo lee (§5 de `hardware-reference.md`) |
