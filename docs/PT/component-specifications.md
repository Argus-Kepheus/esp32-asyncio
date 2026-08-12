# Especificações dos componentes — cess-uff

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

| Terminal da placa | GPIO | Conectado a |
|---|---:|---|
| `2` | GPIO 2 | LED vermelho, por meio de resistor de 220 Ω |
| `4` | GPIO 4 | LED verde, por meio de resistor de 220 Ω |
| `17` | GPIO 17 | Botão pulsador |
| `25` | GPIO 25 | SCL do OLED |
| `16` | GPIO 16 | SDA do OLED |
| `3V3` | — | Alimentação do botão e VCC do OLED |
| `GND.2` | — | Cátodos dos LEDs e GND do OLED |
| `TX` / `RX` | — | `$serialMonitor`, somente para diagnóstico; não faz parte dos requisitos funcionais |

## 2. Display — OLED SSD1306

| Campo | Valor |
|---|---|
| Nome do display | OLED monocromático SSD1306, 128 × 64 |
| Identificador do componente no Wokwi | `board-ssd1306` |
| Identificador da peça em `diagram.json` | `oled-display` |
| Circuito integrado controlador | SSD1306 |
| Resolução | 128 × 64 pixels, monocromático |
| Interface utilizada | I2C. Existem variantes físicas com SPI, que não são usadas neste projeto; consulte `technical-specification.md`, §6.3 |
| Endereço I2C | `0x3C`, definido pelo atributo `i2cAddress` em `diagram.json` |
| Alimentação | 3,3 V e GND |
| Controlador de software | `ssd1306.py`, classe `SSD1306_I2C` |
| Objeto de barramento no MicroPython | `machine.I2C(0, ...)` (hardware) — confirmado em funcionamento no wokwi.com por `tests/05_oled_basic.py` e `tests/06_oled_full_diagnostic.py`; consulte o registro de decisões em `technical-specification.md`, §16 |

### Terminais usados neste projeto

| Terminal do display | Conectado a |
|---|---|
| `VCC` | `3V3` do ESP32 |
| `GND` | `GND.2` do ESP32 |
| `SCL` | GPIO 25 do ESP32 |
| `SDA` | GPIO 16 do ESP32 |

## 3. LEDs

| Campo | LED vermelho | LED verde |
|---|---|---|
| Identificador do componente no Wokwi | `wokwi-led` | `wokwi-led` |
| Identificador da peça em `diagram.json` | `red-led` | `green-led` |
| Atributo de cor | `red` | `green` |
| Ânodo (`A`) conectado a | Resistor de 220 Ω `red-led-resistor`, ligado ao GPIO 2 | Resistor de 220 Ω `green-led-resistor`, ligado ao GPIO 4 |
| Cátodo (`C`) conectado a | `GND.2` do ESP32 | `GND.2` do ESP32 |
| Comportamento | Alterna de estado a cada 500 ms, continuamente | Reproduz o estado estável e tratado do botão |

## 4. Resistores em série

| Campo | Valor |
|---|---|
| Identificador do componente no Wokwi | `wokwi-resistor` |
| Identificadores em `diagram.json` | `red-led-resistor`, `green-led-resistor` |
| Resistência | 220 Ω |
| Finalidade | Limitação da corrente de cada LED no nível lógico de 3,3 V |

## 5. Botão pulsador

| Campo | Valor |
|---|---|
| Identificador do componente no Wokwi | `wokwi-pushbutton` |
| Identificador da peça em `diagram.json` | `push-button` |
| Tipo | Normalmente aberto, momentâneo, com quatro terminais organizados em dois pares eletricamente comuns |
| Nomes válidos dos terminais em `diagram.json` | `1.l`, `1.r` para um nó; `2.l`, `2.r` para o outro nó |
| Terminais usados neste projeto | `1.l` → `3V3` do ESP32; `2.l` → GPIO 17 do ESP32 |
| Tecla de acionamento na simulação | `" "`, atributo `key`; corresponde literalmente ao valor `KeyboardEvent.key` da barra de espaço |
| Função elétrica | Entrada ativa em nível alto, com `Pin.PULL_DOWN` interno no GPIO 17; consulte `technical-specification.md`, §6.2 |

> **Observação:** uma versão preliminar do projeto utilizava `1.R` e `2.R`
> para identificar os terminais do botão. Essas formas possuem letras
> maiúsculas e lado incorreto, portanto o Wokwi não consegue resolvê-las. A
> ligação pode falhar silenciosamente e o botão nunca registrar o acionamento.
> Use sempre exatamente os nomes de terminais indicados acima.
