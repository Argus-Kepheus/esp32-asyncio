<!-- doc-id: hardware-reference -->
<!-- language: ES -->
<!-- content-revision: 3 -->

# Referencia de hardware ESP32-DevKitC V4

Esta es la vista humana autoritativa de placa, módulo, mapeo GPIO→conector y
restricciones eléctricas. La justificación de comportamiento/software vive en
[`technical-specification.md`](technical-specification.md), mientras que los
identificadores por componente están en
[`component-specifications.md`](component-specifications.md). Los valores
canónicos proceden de `config/hardware.json`.

<!-- section: selected-board -->
## 1. Placa seleccionada

<!-- BEGIN GENERATED: board-summary -->
| Propiedad | Definición del proyecto |
|---|---|
| Fabricante | Espressif Systems |
| Nombre de la placa | ESP32-DevKitC V4 |
| Identificador de Wokwi | `board-esp32-devkit-c-v4` (`diagram.json` id `esp32`) |
| Disposición de conectores | 38 pines, 19 por lado (J2, J3) |
| Familia del microcontrolador | ESP32 |
| Módulo físico recomendado | ESP32-WROOM-32E |
| Firmware | MicroPython for ESP32 |
| Tensión lógica | 3.3 V (GPIO no tolerantes a 5 V) |
<!-- END GENERATED: board-summary -->

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

No debe sustituirse por otro tipo de placa sin revisar el mapeo completo de §3
y el registro de decisiones de `technical-specification.md`, §16.

<!-- section: board-rationale -->
## 2. Por qué esta placa y por qué “ESP32” no es suficiente

La consigna requiere MicroPython para ESP32, no una placa específica. Se
eligió ESP32-DevKitC V4 porque es una placa oficial de Espressif, está soportada
por Wokwi, expone los GPIO necesarios y dispone de documentación completa.
Esto mejora la reproducibilidad y evita la ambigüedad de placas genéricas con
distinto número de pines, módulo o rotulado.

La placa portadora y el módulo de radio no son lo mismo: DevKitC V4 incluye
USB, regulador y conectores; el módulo metálico contiene el chip, flash y
antena. Una DevKitC V4 puede montar diferentes módulos; véase §4.

<!-- section: gpio-header-mapping -->
## 3. Mapeo GPIO→conector

Todas las referencias de código y circuito utilizan el número **GPIO del
ESP32**, no la posición secuencial del pin físico.

<!-- BEGIN GENERATED: gpio-map -->
| Función | Identificador de Wokwi | Variable/constante de Python | GPIO | Pin del conector |
|---|---|---|---:|---|
| Salida del LED intermitente 1 | `blue-led-1` | `blue_led_1` / `BLUE_LED_1_PIN` | GPIO26 | J2-10 |
| Salida del LED intermitente 2 | `blue-led-2` | `blue_led_2` / `BLUE_LED_2_PIN` | GPIO14 | J2-12 |
| Salida del LED intermitente 3 | `blue-led-3` | `blue_led_3` / `BLUE_LED_3_PIN` | GPIO27 | J2-11 |
| Salida del LED intermitente 4 | `blue-led-4` | `blue_led_4` / `BLUE_LED_4_PIN` | GPIO25 | J2-9 |
| Salida del LED intermitente 5 | `blue-led-5` | `blue_led_5` / `BLUE_LED_5_PIN` | GPIO33 | J2-8 |
| Salida del LED intermitente 6 | `blue-led-6` | `blue_led_6` / `BLUE_LED_6_PIN` | GPIO12 | J2-13 |
| Salida del LED verde | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Entrada del pulsador principal | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| Pulsador para disminuir velocidad | `decrease-speed-button` | `decrease_speed_button` / `DECREASE_SPEED_BUTTON_PIN` | GPIO34 | J2-5 |
| Pulsador para aumentar velocidad | `increase-speed-button` | `increase_speed_button` / `INCREASE_SPEED_BUTTON_PIN` | GPIO35 | J2-6 |
| LED de bus inactivo (naranja) | `bus-idle-led` | `bus_idle_led` / `BUS_IDLE_LED_PIN` | GPIO13 | J2-15 |
| LED de actividad del planificador (amarillo) | `scheduler-idle-led` | `scheduler_idle_led` / `SCHEDULER_IDLE_LED_PIN` | GPIO2 | J3-15 |
| Reloj I2C de OLED0 de CPU | `oled0-display` | `oled0_display` / `OLED0_SCL_PIN` | GPIO32 | J2-7 |
| Datos I2C de OLED0 de CPU | `oled0-display` | `oled0_display` / `OLED0_SDA_PIN` | GPIO16 | J3-12 |
| Reloj I2C de OLED1 de RAM | `oled1-display` | `oled1_display` / `OLED1_SCL_PIN` | GPIO15 | J3-16 |
| Datos I2C de OLED1 de RAM | `oled1-display` | `oled1_display` / `OLED1_SDA_PIN` | GPIO22 | J3-3 |
| Reloj SPI de la TFT | `tft-display` | `tft_display` / `TFT_SCK_PIN` | GPIO18 | J3-9 |
| Datos de salida SPI de la TFT | `tft-display` | `tft_display` / `TFT_MOSI_PIN` | GPIO23 | J3-2 |
| Selección de chip de la TFT | `tft-display` | `tft_display` / `TFT_CS_PIN` | GPIO5 | J3-10 |
| Dato/comando de la TFT | `tft-display` | `tft_display` / `TFT_DC_PIN` | GPIO21 | J3-6 |
| Reset físico de la TFT | `tft-display` | `tft_display` / `TFT_RST_PIN` | GPIO19 | J3-8 |
| Interruptor deslizante de modo de grabación | `flash-mode-switch` | — | GPIO0 | J3-14 |
| Alimentación de OLED/pulsadores | — | — | 3V3 | J2-1 |
<!-- END GENERATED: gpio-map -->

Los seis LED intermitentes son físicamente azules y mantienen la misma
numeración 1–6 en Wokwi y Python.

Topología conceptual:

```text
salida ESP32 ── resistencia limitadora ── LED ── GND
alimentación ── pulsador ── entrada ESP32
entrada ESP32 ── pull-down externo ── GND   (cuando corresponda)
señales de bus ESP32 ── interfaz de pantalla
```

Los GPIO concretos, resistencias, pull, buses, direcciones y alimentaciones no
se repiten en la prosa. Son canónicos en `config/hardware.json`; la geometría
de cableado de Wokwi permanece bajo autoridad de `diagram.json`.

<!-- section: module-compatibility -->
## 4. Compatibilidad de módulos — WROOM frente a WROVER

El proyecto necesita que los GPIO predefinidos para OLED y pulsador estén
disponibles como E/S general.

| Familia de módulo | Compatibilidad |
|---|---|
| ESP32-WROOM | recomendada |
| ESP32-WROOM-32E | objetivo físico preferido |
| ESP32-WROVER | **no recomendado**; algunos GPIO pueden estar destinados a PSRAM |

Una placa WROVER exigiría reasignar pines en configuración, firmware, circuito
y documentación; esa variante queda fuera del alcance actual.

<!-- section: restricted-gpios -->
## 5. GPIO restringidos o reservados

<!-- BEGIN GENERATED: gpio-constraints -->
| Restricción | Pines | Motivo |
|---|---|---|
| Reservados para la memoria flash SPI | `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` | Comunicación interna con la flash; no usar como GPIO del proyecto |
| Solo entrada | GPIO34, GPIO35, GPIO36, GPIO37, GPIO38, GPIO39 | No pueden accionar salidas y no tienen pull-up/pull-down interno |
| Arranque (bootstrapping) | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | Se muestrean durante el arranque; los usos del proyecto están documentados y validados |
| UART principal | GPIO1, GPIO3 | Usados para programación/diagnóstico serial; no son periféricos del proyecto |
<!-- END GENERATED: gpio-constraints -->

Las notas específicas del proyecto sobre pines de arranque y solo entrada se
mantienen en `config/hardware.json`, bajo `gpio_constraints.notes`. En una
implementación física, cada uso de pin de bootstrapping debe verificarse para
asegurar que el circuito externo no fuerza un nivel incompatible durante el
arranque.

<!-- section: electrical-characteristics -->
## 6. Características eléctricas

- Respete la tensión lógica indicada en el resumen generado.
- Todos los periféricos deben compartir GND.
- Cada LED requiere limitación de corriente; los valores son canónicos en
  `config/hardware.json`.
- Buses, pines, direcciones y frecuencia de OLED son canónicos en
  `config/hardware.json`; la justificación de I2C está en la especificación.
- Alimentación de TFT y mapeo SPI también son canónicos; antes de una
  implementación física debe verificarse el regulador/conversión de nivel del
  módulo ILI9341 concreto.
- La configuración de pull es hardware; el antirrebote es una política de
  software/runtime.

<!-- section: physical-checklist -->
## 7. Lista de verificación para implementación física

Para una futura implementación real:

- comprobar placa y módulo exactos;
- reproducir las señales desde el mapa GPIO generado;
- obtener resistencias, pull y alimentaciones desde `config/hardware.json`;
- mantener GND común;
- revisar pines de arranque, solo entrada y reservados;
- verificar características eléctricas reales de OLED e ILI9341;
- tratar `diagram.json` como netlist/layout de simulación, no como garantía
  de circuitos de protección del módulo físico;
- ejecutar nuevamente los diagnósticos manuales.

<!-- section: references -->
## 8. Referencias

**Espressif / MicroPython:**
- [Guía ESP32-DevKitC V4](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
- [Datasheet ESP32](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [Datasheet ESP32-WROOM-32E](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf)
- [Referencia rápida de MicroPython para ESP32](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [`machine.Pin`](https://docs.micropython.org/en/latest/library/machine.Pin.html) · [`machine.I2C`](https://docs.micropython.org/en/latest/library/machine.I2C.html) · [`asyncio`](https://docs.micropython.org/en/latest/library/asyncio.html)

**Wokwi:**
- [Componente `board-esp32-devkit-c-v4`](https://docs.wokwi.com/parts/board-esp32-devkit-c-v4)
- [Formato `diagram.json`](https://docs.wokwi.com/diagram-format)

<!-- section: board-identification -->
## 9. Declaración de identificación de la placa

> El proyecto tiene como objetivo la placa oficial de desarrollo Espressif
> ESP32-DevKitC V4, representada en Wokwi por
> `board-esp32-devkit-c-v4`. Para una implementación física se recomienda
> una ESP32-DevKitC V4 con módulo ESP32-WROOM-32E. Todas las referencias de
> pines usan números GPIO del ESP32 y no posiciones físicas secuenciales.
