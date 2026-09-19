<!-- doc-id: technical-specification -->
<!-- language: ES -->
<!-- content-revision: 6 -->

# Especificación técnica — esp32-asyncio

<!-- section: document-control -->
## 1. Control del documento

| Campo | Valor |
|---|---|
| Proyecto | Exploración personal de ESP32 MicroPython con asyncio |
| Asignaturas | Instrumentación, Electrónica y Lógica de Programación |
| Plataforma objetivo | ESP32 (MicroPython) |
| Plataforma de simulación | Wokwi |
| Ejecutable principal | `main.py` |
| Definición del circuito | `diagram.json` |
| Licencia | CC0 1.0 Universal |
| Idioma del documento | Español |
| Mensajes visibles en OLED | Portugués, según requisito explícito |

Este documento consolida requisitos y decisiones de ingeniería. Los comentarios
de otros colaboradores pueden integrarse en revisiones posteriores siempre que
se preserve el comportamiento obligatorio y la trazabilidad. El proceso de
revisión está descrito en §18.

<!-- section: objective -->
## 2. Objetivo

Desarrollar y simular una aplicación ESP32 MicroPython que, de forma
concurrente:

1. haga parpadear seis LED, cada uno en su propia tarea `asyncio`, todos con
   un intervalo compartido y ajustable;
2. lea un pulsador normalmente abierto y activo en HIGH y controle un LED
   verde con su estado;
3. lea dos pulsadores adicionales que aceleran o desaceleran simultáneamente
   los seis LED;
4. muestre gráficos en vivo de CPU y RAM en dos OLED SSD1306 independientes;
5. registre líneas coloreadas por subsistema en una consola TFT ILI9341,
   reflejándolas también en la consola serial; y
6. controle dos LED de estado asociados a actividad de buses de pantalla y del
   planificador.

Los entregables incluyen `main.py`, los controladores `ssd1306.py` e
`ili9341.py`, el paquete generado de runtime (`lib/__init__.py` y
`lib/generated_config.py`), el repositorio GitHub y un enlace compartible a
la simulación Wokwi.

<!-- section: simulation-platform -->
## 3. Decisión sobre la plataforma de simulación

Se utiliza Wokwi porque soporta ESP32, MicroPython, SSD1306 I2C, componentes
interactivos, `diagram.json` y proyectos compartibles desde el navegador.

Tinkercad Circuits se descartó para este entregable porque sus placas no
ejecutan directamente un script MicroPython como el requerido; esta decisión
no implica que Tinkercad carezca de utilidad educativa.

### 3.1 Selección de placa

La placa objetivo es `board-esp32-devkit-c-v4` (id `esp32` en
`diagram.json`). Se eligió por ser oficial de Espressif, estar soportada por
Wokwi, exponer los GPIO necesarios y disponer de documentación completa.
Las especificaciones por componente están en
[`component-specifications.md`](component-specifications.md) y el mapeo
GPIO→conector en [`hardware-reference.md`](hardware-reference.md).

<!-- section: functional-requirements -->
## 4. Requisitos funcionales

### FR-01 — Seis LED intermitentes

- IDs `blue-led-1` a `blue-led-6`; variables `blue_led_1` a
  `blue_led_6`.
- El mapeo GPIO/conector es canónico en `config/hardware.json` y se muestra
  en la tabla generada de `hardware-reference.md`, §3.
- Los seis son físicamente azules y conservan la misma numeración 1–6.
- Cada uno es una salida digital con su propia tarea `blink_led()`.
- Todos usan el intervalo base compartido de `config/runtime.json`,
  ajustable por FR-03.
- Ninguna tarea de LED llama o espera a otra; todas comparten únicamente el
  planificador cooperativo.

### FR-02 — Pulsador principal y LED verde

- IDs `push-button` y `green-led`; variables `push_button` y
  `green_led`.
- Cableado y pull son canónicos en `config/hardware.json`.
- El pulsador es normalmente abierto, `Pin.IN` con `Pin.PULL_DOWN`;
  liberado = LOW, pulsado = HIGH.
- Liberado → LED verde apagado; pulsado → LED verde encendido.
- Cada transición aceptada por antirrebote se registra en verde mediante
  `console_log()`.

### FR-03 — Pulsadores de velocidad

- IDs `decrease-speed-button` e `increase-speed-button`.
- GPIO y pull son canónicos en `config/hardware.json`.
- Cada pulsación modifica el intervalo de todos los LED mediante el paso
  exponencial configurado y respeta los límites de `config/runtime.json`.

### FR-04 — Dos gráficos OLED de recursos

- IDs `oled0-display` y `oled1-display`.
- Ambos usan SSD1306 sobre buses I2C de hardware independientes.
- Direcciones, buses y pines son canónicos en `config/hardware.json`.
- OLED0 representa la métrica aproximada "CPU"; OLED1 la métrica "RAM"
  descrita en §19.2.
- La cadencia de muestreo viene de `config/runtime.json`; el delay
  configurado es un piso, no un periodo exacto.

### FR-05 — Consola TFT

- ID `tft-display`, variable `tft_display`.
- ILI9341 sobre SPI de 4 hilos; bus y señales son canónicos en
  `config/hardware.json`.
- `console_log()` escribe una línea coloreada por evento y siempre la refleja
  en serial, exista o no una TFT operativa (§19.4).

### FR-06 — LED indicadores de estado

- `bus-idle-led`: encendido por defecto y apagado mientras una escritura de
  pantalla instrumentada está activa.
- `scheduler-idle-led`: alterna en cada iteración de
  `scheduler_idle_task()`; es una visualización aproximada de actividad, no
  una señal literal de prioridad/idle.

### FR-07 — Entregables

- `main.py`, `ssd1306.py`, `ili9341.py`,
  `lib/__init__.py` y `lib/generated_config.py`;
- `diagram.json` y `wokwi.toml`;
- README y documentación técnica;
- URL pública/compartible del repositorio GitHub;
- URL compartible del proyecto Wokwi.

<!-- section: naming-conventions -->
## 5. Convenciones de nombres

| Contexto | Convención | Ejemplos |
|---|---|---|
| IDs de componentes Wokwi | kebab-case | `blue-led-1`, `green-led`, `push-button` |
| Variables Python | snake_case | `blue_led_1`, `green_led`, `push_button` |
| Constantes Python | UPPER_SNAKE_CASE | `BLUE_LED_1_PIN`, `BUTTON_PIN` |
| Carpeta del repositorio | kebab-case | `esp32-asyncio` |

El código fuente y sus comentarios permanecen en inglés. La documentación
narrativa es multilingüe bajo `docs/metadata.json`; EN es la versión
narrativa canónica y ES/PT son traducciones mantenidas.

<!-- section: electrical-design -->
## 6. Diseño eléctrico

### 6.1 Tabla de conexiones

El mapa GPIO→conector completo está en
[`hardware-reference.md`](hardware-reference.md), §3, para evitar mantener
la misma tabla en varias especificaciones.

### 6.2 Acondicionamiento de la entrada del pulsador

El cableado y pull del pulsador principal son canónicos en
`config/hardware.json`. A nivel lógico, abierto = LOW y pulsado = HIGH.

El pulsador simulado de Wokwi es ideal y no modela rebote mecánico. Se mantiene
antirrebote de software para que el mismo código sea adecuado para hardware
real, donde también influyen cableado, longitud de conductores e interferencia.

### 6.3 Por qué I2C para OLED y SPI para TFT

Los dos OLED usan I2C independiente porque requieren pocas señales y la
variante SSD1306 de Wokwi utilizada es I2C. Su carga gráfica periódica no
justifica más pines para SPI.

La TFT ILI9341 usa SPI de 4 hilos porque el controlador del componente es SPI y
su cuadro de color mayor se beneficia de una tasa de transferencia superior.
Son decisiones independientes para periféricos distintos.

<!-- section: software-architecture -->
## 7. Arquitectura de software

### 7.1 Tareas asíncronas cooperativas

La aplicación usa `asyncio` para la planificación. Hay trece flujos:

- seis tareas `blink_led()`;
- una `scheduler_idle_task()`;
- `update_cpu_graph()` y `update_ram_graph()`;
- `print_status()`;
- dos `monitor_step_button()`;
- un `monitor_button()`, esperado directamente por `main()`.

### 7.2 Por qué se eligió `asyncio`

- separación clara de responsabilidades;
- extensión sencilla mediante nuevas tareas;
- pausas cooperativas explícitas con `await asyncio.sleep_ms()`.

`asyncio` no vuelve no bloqueante una escritura síncrona del controlador
SSD1306. `show()` sigue bloqueando durante su transferencia. La elección se
hizo por organización y escalabilidad, no para cambiar esa propiedad física.

### 7.3 Alternativas descartadas

- `time.sleep()`/ `time.sleep_ms()`: bloquearían todo el script;
- superloop manual con `ticks_ms()`: válido y más ligero a esta escala, pero
  menos limpio al crecer el número de comportamientos;
- `machine.Timer`: innecesario y no adecuado para realizar transferencias de
  pantalla desde callbacks.

### Resumen de parámetros de ejecución

<!-- BEGIN GENERATED: runtime-summary -->
| Parámetro de ejecución | Valor configurado |
|---|---:|
| Intervalo base de los LED intermitentes | 500 ms |
| Rango de pasos de velocidad | -2 … 3 |
| Intervalo de muestreo de pulsadores | 5 ms |
| Ventana estable de antirrebote | 30 ms |
| Piso de muestreo del gráfico de CPU | 250 ms |
| Piso de muestreo del gráfico de RAM | 250 ms |
| Intervalo del estado serial | 1000 ms |
| Limitación del registro de consola | 4 |
<!-- END GENERATED: runtime-summary -->

<!-- section: debounce-strategy -->
## 8. Estrategia de antirrebote

Aunque Wokwi no modela rebote, el monitor:

1. muestrea según `BUTTON_SAMPLE_INTERVAL_MS`;
2. identifica un estado candidato;
3. reinicia la marca temporal si cambia antes de aceptarse;
4. acepta solo tras permanecer estable durante `BUTTON_DEBOUNCE_MS`;
5. llama a `apply_button_state()` una vez aceptado.

No se usa un delay bloqueante.

<!-- section: oled-update-strategy -->
## 9. Estrategia de actualización de gráficos OLED

`update_cpu_graph()` y `update_ram_graph()` redibujan periódicamente en
bucles separados y después esperan su intervalo configurado. El tiempo real se
mide con `time.ticks_us()` porque `sleep_ms()` garantiza un mínimo, no un
periodo exacto.

Cada actualización limpia y redibuja el historial completo. Aunque
`framebuf.scroll()` existe y se prueba en un diagnóstico, el redibujado total
se mantiene deliberadamente. Los OLED forman parte de la carga que mide la
métrica "CPU" aproximada.

<!-- section: state-model -->
## 10. Modelo de estados

| Estado estable | Entrada | LED verde | Registro |
|---|---|---|---|
| Liberado | LOW | OFF | `Button released -> Green LED OFF` |
| Pulsado | HIGH | ON | `Button pressed -> Green LED ON` |

Las tareas de LED, OLED y TFT son ortogonales a este estado: no se pausan ni se
reinician con una transición del pulsador.

<!-- section: startup-failure -->
## 11. Inicio y comportamiento ante fallos

Antes de ejecutar `main()`, la aplicación configura salidas y entradas,
crea ambos buses OLED, escanea la dirección canónica y crea la interfaz SPI de
la TFT. Un OLED ausente produce diagnóstico serial y `None` para esa pantalla
sin detener el resto.

La TFT es diferente: su enlace es SPI solo de escritura. Un panel físicamente
ausente puede no generar `OSError`; por ello no existe detección fiable de
"TFT ausente". El espejo serial de `console_log()` se ejecuta siempre.

`main()` registra el arranque, aplica el estado inicial del pulsador, reinicia
el acumulador de bus ocupado, crea las doce tareas despachadas y espera
directamente el monitor del pulsador principal.

<!-- section: verification-plan -->
## 12. Plan de verificación

### TC-01 — Arranque con pulsador liberado
Esperado: los seis LED parpadean, LED verde apagado, ambos gráficos activos y
línea de arranque en TFT/serial.

### TC-02 — Pulsar
Mantener pulsado. Tras antirrebote: LED verde ON y línea
`Button pressed -> Green LED ON`; los demás flujos continúan.

### TC-03 — Liberar
Tras antirrebote: LED verde OFF y línea
`Button released -> Green LED OFF`; los LED continúan.

### TC-04 — Pulsaciones rápidas
No debe haber oscilación visible ni registros redundantes más allá de una
transición por cambio estable real.

### TC-05 — Independencia temporal
Pulsar en diferentes fases de los LED. La respuesta sigue siendo rápida y el
parpadeo mantiene su intervalo, sujeto a la latencia de escrituras síncronas
documentada en §19.2.

### TC-06 — OLED desconectado
Retirar temporalmente una conexión I2C. Debe diagnosticarse el OLED ausente y
los demás subsistemas deben seguir funcionando.

### TC-07 — Comprobación básica de arranque
Antes de depurar la aplicación, probar un script trivial de un GPIO. Un bucle
de banners `POWERON_RESET` / `SW_RESET` sin ejecutar MicroPython indica un
problema de firmware/placa, no de la aplicación. Revisar primero `attrs.env`
del componente `esp32`.

### TC-08 — Límites de los pulsadores de velocidad
Pulsar repetidamente en ambos sentidos. El intervalo debe detenerse en
`BLINK_SPEED_STEP_MIN` / `BLINK_SPEED_STEP_MAX` de
`config/runtime.json`.
**Ejecutado y aprobado en Wokwi web el 2026-08-18.**

### TC-09 — Tres pantallas simultáneas
Ejecutar durante varios minutos con ambos OLED y TFT activos. Ninguna pantalla
debe dejar de actualizarse mientras las otras continúan.
**Ejecutado y aprobado en Wokwi web el 2026-08-18.**

### TC-10 — Ruta de fallo de TFT
Desconectar SPI/GND de TFT. Debido a SPI solo de escritura, el fallo puede no
detectarse, pero todos los eventos deben seguir apareciendo en serial.
**Ejecutado y aprobado en Wokwi web el 2026-08-18.**

### TC-11 — Desincronización prolongada y latencia del pulsador
Ejecutar al menos 10–15 minutos y observar fase de los seis LED y respuesta del
pulsador. Se espera deriva relativa de fase y, ocasionalmente, mayor tiempo de
pulsación durante periodos cargados por pantallas.
**Ejecutado y aprobado en Wokwi web el 2026-08-18.**

<!-- section: workflow -->
## 13. Flujo Wokwi, VS Code y GitHub

GitHub es la fuente versionada. Wokwi ofrece:

1. **Wokwi Web**, para simulación interactiva y URL compartible;
2. **Wokwi para VS Code**, usando `diagram.json`, `wokwi.toml`,
   `firmware.bin` local no versionado y transferencia mediante
   `mpremote`.

El despliegue local debe incluir `main.py`, ambos controladores de pantalla
en la raíz y el paquete `lib/`, porque `main.py` importa
`lib.generated_config`.

<!-- section: repository-contents -->
## 14. Contenido del repositorio

| Ruta | Propósito |
|---|---|
| `main.py` | aplicación/orquestador ejecutable |
| `ssd1306.py` | controlador OLED I2C |
| `ili9341.py` | controlador TFT SPI |
| `lib/` | configuración generada consumida por `main.py` |
| `config/` | fuentes canónicas hardware/runtime |
| `diagram.json` | componentes y conexiones Wokwi |
| `wokwi.toml` | configuración de simulación local |
| `diagnostics/` | 13 diagnósticos manuales |
| `tests/` | reservado para pruebas automatizadas futuras |
| `docs/` | documentación multilingüe y metadatos de paridad |
| `tools/` | generación y validación |
| `report/` | snapshot académico en portugués |

<!-- section: acceptance-criteria -->
## 15. Criterios de aceptación

El proyecto se acepta cuando:

- la configuración canónica, firmware y circuito son coherentes;
- `main.py` inicia sin error en el entorno MicroPython/Wokwi previsto;
- los seis LED alternan sin bloqueos indebidos;
- el LED verde refleja el estado estable del pulsador;
- los pulsadores de velocidad respetan sus límites;
- ambos OLED y TFT se actualizan según las limitaciones documentadas;
- `main.py` no usa `time.sleep()` bloqueante;
- las URL de Wokwi y GitHub son compartibles;
- la documentación satisface el contrato multilingüe de
  `docs/metadata.json`.

<!-- section: decision-log -->
## 16. Registro de decisiones

Las decisiones principales son:

| Decisión | Motivo | Alternativa descartada |
|---|---|---|
| IDs numerados para los seis LED azules | preservan color físico y orden común | nombres por colores inexistentes |
| Wokwi frente a Tinkercad | ejecuta MicroPython y ofrece URL compartible | usar Tinkercad solo para esquema/C++ |
| ESP32-DevKitC V4 | placa oficial, reproducible y con GPIO suficientes | placas genéricas o con otro rotulado |
| tareas `asyncio` | separación y escalabilidad | superloop manual |
| I2C para OLED, SPI para TFT | equilibrio entre pines y tasa de transferencia | SPI también para OLED |
| pull-down interno del pulsador principal | HIGH al pulsar sin resistor externo | pull-down externo |
| antirrebote de software | preparación para hardware físico | omitirlo en simulación |
| gráficos OLED periódicos | muestran recursos variables | texto estático del pulsador |
| tiempos de muestreo y antirrebote configurables | evita valores codificados dispersos | un único polling grueso |
| `machine.I2C` | diagnósticos actuales confirmaron hardware I2C | `SoftI2C` como fallback |
| pines Wokwi `1.l` / `2.l` | nombres reales del componente | `1.R` / `2.R` inválidos |
| no fijar `attrs.env` | el valor histórico fijado provocaba reset infinito | fijar firmware inválido |
| CPU/RAM como gráficos | requisito consolidado y datos medidos/estimados reales | onda sintética |
| seis tareas LED con un intervalo compartido | conserva concurrencia independiente | una tarea única para todos |

<!-- section: future-work -->
## 17. Trabajo futuro — fase de hardware físico

- Mantener antirrebote para pulsadores mecánicos y considerar un filtro RC
  opcional.
- Reevaluar I2C frente a SPI si una implementación física dispone de más GPIO
  y necesita una frecuencia de actualización superior.

<!-- section: revision-guidance -->
## 18. Integración de revisiones

Los cambios deben entrar mediante commits revisados e indicar si afectan:

- requisitos obligatorios;
- supuestos eléctricos;
- temporización/concurrencia;
- compatibilidad del simulador;
- documentación; o
- una implementación física futura.

No deben cambiarse mapeos obligatorios ni mensajes requeridos sin actualizar
explícitamente los requisitos de evaluación.

<!-- section: implementation-notes -->
## 19. Notas de implementación

### 19.1 Dos buses I2C OLED independientes

OLED0 CPU y OLED1 RAM usan buses I2C de hardware separados, no dos direcciones
en un único bus. IDs, GPIO y direcciones son canónicos en
`config/hardware.json`.

### 19.2 Qué representan los gráficos OLED

Ambos son gráficos de barras desplazables tipo administrador de tareas, con una
muestra por columna horizontal.

- **OLED0 — "CPU".** ESP32 MicroPython no expone una métrica de carga de
  planificador equivalente a un sistema operativo. El valor es una
  aproximación parcial: fracción de la ventana de muestreo empleada dentro de
  llamadas síncronas instrumentadas de las tres pantallas, medida por
  `_bus_busy_begin()` / `_bus_busy_end()`. Incluye trabajo Python de
  dibujo y transferencia I2C/SPI; no cubre todo el uso de CPU.
- **OLED1 — "RAM".** Valor real basado en el heap gestionado por el recolector
  de MicroPython mediante `gc.mem_alloc()` / `gc.mem_free()`. No equivale
  a toda la RAM física ni incluye todas las asignaciones nativas.

El estado del pulsador se registra mediante `console_log()`, no como texto en
los OLED.

### 19.3 Seis LED, un intervalo compartido, seis tareas

Los seis LED intermitentes son azules y se siguen individualmente en
`BLINKING_LEDS`. Cada uno ejecuta su propia tarea `blink_led()`; añadir un
LED significa añadir otra tarea, no ampliar un bucle compartido.

### 19.4 Consola TFT, SPI solo de escritura y espejo serial

ILI9341 usa SPI de 4 hilos más reset. La TFT funciona como registro coloreado:
una línea por evento y vuelta a la parte superior al llenar la pantalla.

El enlace no tiene MISO y `ili9341.py` no lee ID ni estado. Por ello,
`create_tft_display()` solo devuelve `None` cuando la construcción del
objeto genera `OSError`; un panel físicamente ausente puede no ser detectable.

Para cubrir ese caso, `console_log()` imprime **siempre** cada línea en serial
y además la envía a la TFT cuando existe un objeto de pantalla.

El renderizado de texto fue optimizado: en vez de convertir cada glifo mediante
miles de llamadas individuales a píxeles, la implementación actual precalcula
por par de colores una tabla de 256 entradas que transforma cada byte del glifo
en sus 16 bytes RGB565 y reutiliza esa tabla por carácter.
