# Especificações dos componentes — esp32-asyncio

Este documento apresenta uma ficha de especificação para cada componente
físico ou simulado utilizado em `diagram.json`. As fichas são mantidas
separadas das justificativas de projeto registradas em
`technical-specification.md`, para que a identidade, a função elétrica e
o identificador de cada peça no Wokwi possam ser consultados sem ambiguidade.

Cada ficha descreve o componente exatamente como ele é empregado neste
projeto, e não todas as capacidades que o componente real pode oferecer. Em
revisões futuras, amplie a ficha existente em vez de duplicá-la.

Para consultar a posição física de cada GPIO nos conectores, os terminais
reservados, a compatibilidade entre módulos WROOM e WROVER, as características
elétricas e a lista de verificação da montagem física, consulte
[`hardware-reference.md`](hardware-reference.md).

## 1. Placa microcontroladora — ESP32-DevKitC V4

| Campo | Valor |
|---|---|
| Nome da placa | Espressif ESP32-DevKitC V4 |
| Identificador do componente no Wokwi | `board-esp32-devkit-c-v4` |
| Identificador da peça em `diagram.json` | `esp32` |
| Família do microcontrolador | ESP32 |
| Perfil de módulo recomendado | ESP32-WROOM-32E |
| Disposição dos conectores | 38 terminais, 19 em cada lado |
| Firmware | MicroPython para ESP32 |
| Fixação da versão do firmware em `diagram.json` (`attrs.env`) | Nenhuma — usar `attrs: {}`. Uma revisão anterior fixava `"env": "micropython-20240602-v1.23.0"`, o que provocava um ciclo infinito de inicialização no wokwi.com, com repetidos `SW_RESET` e sem início do MicroPython. A fixação foi removida, e a placa passou a usar a versão padrão/atual do MicroPython fornecida pelo Wokwi. Consulte `technical-specification.md`, §16. |
| Convenção de numeração | Números dos GPIOs do ESP32, e não posições físicas sequenciais dos conectores |
| Nível lógico | 3,3 V |
| Justificativa da seleção | Consulte `technical-specification.md`, §3.1 |

### Terminais usados neste projeto

O mapeamento completo e atual de GPIOs está em
[`hardware-reference.md`](hardware-reference.md), §3; este conjunto de
linhas é uma amostra representativa, não uma duplicata daquela tabela.

| Terminal da placa | GPIO | Conectado a |
|---|---:|---|
| `26` | GPIO 26 | LED piscante 1, por meio de resistor de 220 Ω |
| `4` | GPIO 4 | LED verde, por meio de resistor de 220 Ω |
| `17` | GPIO 17 | Botão pulsador principal |
| `32` | GPIO 32 | SCL do OLED0 de CPU |
| `16` | GPIO 16 | SDA do OLED0 de CPU |
| `3V3` | — | Alimentação dos botões e dos OLEDs |
| `5V` | — | Alimentação da TFT |
| `GND.1` / `GND.2` | — | Cátodos dos LEDs, GND dos OLEDs e da TFT |
| `TX` / `RX` | — | `$serialMonitor`, somente para diagnóstico; não faz parte dos requisitos funcionais |

## 2. Mostradores — OLEDs SSD1306 e TFT ILI9341

### 2.1 OLED SSD1306 (×2)

| Campo | OLED0 de CPU | OLED1 de RAM |
|---|---|---|
| Nome do display | OLED monocromático SSD1306, 128 × 64 | OLED monocromático SSD1306, 128 × 64 |
| Identificador no Wokwi | `board-ssd1306` | `board-ssd1306` |
| Identificador em `diagram.json` | `oled0-display` | `oled1-display` |
| Interface utilizada | I2C (existem variantes físicas com SPI, não usadas aqui — ver `technical-specification.md`, §6.3) | I2C |
| Endereço I2C | `0x3C` | `0x3C` |
| Objeto de barramento no MicroPython | `machine.I2C(0, ...)` | `machine.I2C(1, ...)`, barramento independente |
| Alimentação | 3,3 V e GND | 3,3 V e GND |
| Controlador de software | `ssd1306.py`, classe `SSD1306_I2C`, compartilhada pelos dois | (idem) |
| Papel em `main.py` | Gráfico de uso de "CPU" (`update_cpu_graph()`) | Gráfico de uso de "RAM" (`update_ram_graph()`) |
| Terminais | SCL → GPIO 32, SDA → GPIO 16 | SCL → GPIO 15, SDA → GPIO 22 |

Diagnósticos isolados atuais: `tests/05_cpu_oled_basic.py` /
`tests/06_cpu_oled_full_diagnostic.py` (OLED0 de CPU),
`tests/11_ram_oled_basic.py` (OLED1 de RAM, testado isoladamente — não
prova operação simultânea dos dois barramentos).

### 2.2 TFT ILI9341

| Campo | Valor |
|---|---|
| Nome do display | TFT colorida ILI9341, 240 × 320 |
| Identificador no Wokwi | `wokwi-ili9341` |
| Identificador em `diagram.json` | `tft-display` |
| Interface utilizada | SPI genuíno de 4 fios (SCK, MOSI, CS, D/C) mais uma linha de reset em hardware |
| Profundidade de cor | RGB565, 16 bits |
| Alimentação | 5 V e GND (ver `hardware-reference.md`, §6, para a ressalva que isso implica numa montagem física) |
| Controlador de software | `ili9341.py` (classe `ILI9341` própria deste projeto) |
| Objeto de barramento no MicroPython | `machine.SPI(2, ...)` |
| Papel em `main.py` | Console de registro de atividade colorido e rolante (`console_log()`) |
| Terminais | SCK → GPIO 18, MOSI → GPIO 23, CS → GPIO 5, D/C → GPIO 21, RST → GPIO 19 |

Diagnósticos isolados atuais: `tests/12_tft_basic.py` (inicialização SPI,
preenchimentos sólidos), `tests/13_tft_text_diagnostic.py` (renderização
de texto, cores do console).

## 3. LEDs

Nove LEDs no total. Os seis LEDs piscantes são todos fisicamente azuis
(`#0000FF`) em `diagram.json` e usam identificadores correspondentes numerados
de 1 a 6 no circuito e no código Python.

| Campo | LEDs piscantes (×6) | LED verde | LED de barramento ocioso | LED de escalonador ocioso |
|---|---|---|---|---|
| Identificador no Wokwi | `wokwi-led` | `wokwi-led` | `wokwi-led` | `wokwi-led` |
| Identificadores em `diagram.json` | `blue-led-1` a `blue-led-6` | `green-led` | `bus-idle-led` | `scheduler-idle-led` |
| Atributo de cor | `#0000FF` (todos os seis) | `green` | `orange` | `yellow` |
| GPIO (ânodo via resistor) | 26, 14, 27, 25, 33, 12 | 4 | 13 | 2 |
| Cátodo conectado a | GND do ESP32 | GND do ESP32 | GND do ESP32 | GND do ESP32 |
| Comportamento | Cada um alterna de forma independente no intervalo compartilhado (RF-01) | Reproduz o estado estável do botão (RF-02) | Aceso por padrão, apaga durante uma escrita instrumentada (RF-06) | Alterna a cada iteração de `scheduler_idle_task()` (RF-06) |

## 4. Resistores em série

| Campo | Resistores dos LEDs | Pull-downs dos botões de velocidade |
|---|---|---|
| Identificador no Wokwi | `wokwi-resistor` | `wokwi-resistor` |
| Identificadores em `diagram.json` | um por LED (9 no total): `blue-led-1-resistor` a `blue-led-6-resistor`, `green-led-resistor`, `bus-idle-led-resistor`, `scheduler-idle-led-resistor` | `decrease-speed-button-pulldown`, `increase-speed-button-pulldown` |
| Resistência | 220 Ω | 10 kΩ |
| Finalidade | Limitação da corrente de cada LED no nível lógico de 3,3 V | Pull-down externo para GPIO34/35, que não têm um interno |

## 5. Botões pulsadores

| Campo | Botão principal | Botões de velocidade (×2) |
|---|---|---|
| Identificador no Wokwi | `wokwi-pushbutton` | `wokwi-pushbutton` |
| Identificador em `diagram.json` | `push-button` | `decrease-speed-button`, `increase-speed-button` |
| Tipo | Normalmente aberto, momentâneo, quatro terminais em dois pares eletricamente comuns | Igual |
| Nomes válidos dos terminais em `diagram.json` | `1.l`, `1.r` (um nó), `2.l`, `2.r` (outro nó) | Igual |
| Terminais usados neste projeto | `1.l` → `3V3`; `2.l` → GPIO 17 | `1.l` → `3V3`; `2.l` → GPIO 34 / GPIO 35, cada um por seu próprio pull-down externo de 10 kΩ |
| Tecla de acionamento na simulação | `" "` (barra de espaço) | `"a"` (diminuir), `"s"` (aumentar) |
| Função elétrica | Entrada ativa em nível alto, `Pin.PULL_DOWN` interno no GPIO 17 — ver `technical-specification.md`, §6.2 | Entrada ativa em nível alto, sem resistor interno de redução (pinos somente de entrada) — exige pull-down externo |

> **Observação:** uma versão preliminar do projeto utilizava `1.R` e `2.R`
> para identificar os terminais do botão. Essas formas possuem letras
> maiúsculas e lado incorreto, portanto o Wokwi não consegue resolvê-las. A
> ligação pode falhar silenciosamente e o botão nunca registrar o acionamento.
> Use sempre exatamente os nomes de terminais indicados acima.

## 6. Chave deslizante de modo de gravação

| Campo | Valor |
|---|---|
| Identificador no Wokwi | `wokwi-slide-switch` |
| Identificador em `diagram.json` | `flash-mode-switch` |
| Terminais usados neste projeto | um terminal → GPIO 0 do ESP32, o outro → GND |
| Papel | Seleção de modo de boot do bootloader ROM; nenhum código de `main.py` a lê — ver `hardware-reference.md`, §5 |
