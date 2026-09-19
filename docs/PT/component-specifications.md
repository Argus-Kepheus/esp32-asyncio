<!-- doc-id: component-specifications -->
<!-- language: PT -->
<!-- content-revision: 2 -->

# Especificações dos componentes — esp32-asyncio

Este documento apresenta uma ficha de especificação para cada componente
físico ou simulado utilizado em `diagram.json`. As fichas são mantidas
separadas das justificativas de projeto registradas em
`technical-specification.md`, para que a identidade, a função elétrica e
o identificador de cada peça no Wokwi possam ser consultados sem ambiguidade.

Cada ficha descreve o componente exatamente como ele é empregado neste
projeto, e não todas as capacidades que o componente real pode oferecer. Em
revisões futuras, amplie a ficha existente em vez de duplicá-la.

> GPIOs, barramentos, endereços, valores de resistores, configuração de pull e alimentação atuais são canônicos em `config/hardware.json` e apresentados em forma gerada em `hardware-reference.md`. Este documento deliberadamente não duplica esses valores.

Para consultar a posição física de cada GPIO nos conectores, os terminais
reservados, a compatibilidade entre módulos WROOM e WROVER, as características
elétricas e a lista de verificação da montagem física, consulte
[`hardware-reference.md`](hardware-reference.md).

<!-- section: microcontroller-board -->
## 1. Placa microcontroladora — ESP32-DevKitC V4

A identidade atual da placa, recomendação de módulo, disposição dos conectores, família de firmware e tensão lógica são geradas a partir de `config/hardware.json` em [`hardware-reference.md`](hardware-reference.md), §1.

A placa no Wokwi mantém `attrs.env` sem valor fixado. Uma revisão anterior fixava `"micropython-20240602-v1.23.0"`, o que provocava um ciclo infinito de reinicialização no wokwi.com; remover essa fixação não suportada restaurou a inicialização normal do MicroPython. A justificativa da seleção permanece em `technical-specification.md`, §3.1.

### Terminais usados neste projeto

O mapeamento completo e atual de GPIOs está em
[`hardware-reference.md`](hardware-reference.md), §3; este conjunto de
linhas é uma amostra representativa, não uma duplicata daquela tabela.

O mapa completo e atual de GPIOs nos conectores é a tabela gerada em [`hardware-reference.md`](hardware-reference.md), §3. Ele não é duplicado aqui.

<!-- section: displays -->
## 2. Mostradores — OLEDs SSD1306 e TFT ILI9341

### 2.1 OLED SSD1306 (×2)

| Campo | OLED0 de CPU | OLED1 de RAM |
|---|---|---|
| Nome do display | OLED monocromático SSD1306, 128 × 64 | OLED monocromático SSD1306, 128 × 64 |
| Identificador no Wokwi | `board-ssd1306` | `board-ssd1306` |
| Identificador em `diagram.json` | `oled0-display` | `oled1-display` |
| Interface utilizada | I2C (existem variantes físicas com SPI, não usadas aqui — ver `technical-specification.md`, §6.3) | I2C |
| Controlador de software | `ssd1306.py`, classe `SSD1306_I2C`, compartilhada pelos dois | (idem) |
| Papel em `main.py` | Gráfico de uso de "CPU" (`update_cpu_graph()`) | Gráfico de uso de "RAM" (`update_ram_graph()`) |

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
| Controlador de software | `ili9341.py` (classe `ILI9341` própria deste projeto) |
| Papel em `main.py` | Console de registro de atividade colorido e rolante (`console_log()`) |

Diagnósticos isolados atuais: `tests/12_tft_basic.py` (inicialização SPI,
preenchimentos sólidos), `tests/13_tft_text_diagnostic.py` (renderização
de texto, cores do console).

<!-- section: leds -->
## 3. LEDs

Nove LEDs no total. Os seis LEDs piscantes são todos fisicamente azuis
(`#0000FF`) em `diagram.json` e usam identificadores correspondentes numerados
de 1 a 6 no circuito e no código Python.

| Campo | LEDs piscantes (×6) | LED verde | LED de barramento ocioso | LED de escalonador ocioso |
|---|---|---|---|---|
| Identificador no Wokwi | `wokwi-led` | `wokwi-led` | `wokwi-led` | `wokwi-led` |
| Identificadores em `diagram.json` | `blue-led-1` a `blue-led-6` | `green-led` | `bus-idle-led` | `scheduler-idle-led` |
| Atributo de cor | `#0000FF` (todos os seis) | `green` | `orange` | `yellow` |
| Comportamento | Cada um alterna de forma independente no intervalo compartilhado (RF-01) | Reproduz o estado estável do botão (RF-02) | Aceso por padrão, apaga durante uma escrita instrumentada (RF-06) | Alterna a cada iteração de `scheduler_idle_task()` (RF-06) |

<!-- section: series-resistors -->
## 4. Resistores em série

| Campo | Resistores dos LEDs | Pull-downs dos botões de velocidade |
|---|---|---|
| Identificador no Wokwi | `wokwi-resistor` | `wokwi-resistor` |
| Finalidade | Limitação da corrente de cada LED no nível lógico de 3,3 V | Pull-down externo para os pinos somente de entrada dos botões de velocidade |

<!-- section: push-buttons -->
## 5. Botões pulsadores

| Campo | Botão principal | Botões de velocidade (×2) |
|---|---|---|
| Identificador no Wokwi | `wokwi-pushbutton` | `wokwi-pushbutton` |
| Identificador em `diagram.json` | `push-button` | `decrease-speed-button`, `increase-speed-button` |
| Tipo | Normalmente aberto, momentâneo, quatro terminais em dois pares eletricamente comuns | Igual |
| Nomes válidos dos terminais em `diagram.json` | `1.l`, `1.r` (um nó), `2.l`, `2.r` (outro nó) | Igual |
| Tecla de acionamento na simulação | `" "` (barra de espaço) | `"a"` (diminuir), `"s"` (aumentar) |

> **Observação:** uma versão preliminar do projeto utilizava `1.R` e `2.R`
> para identificar os terminais do botão. Essas formas possuem letras
> maiúsculas e lado incorreto, portanto o Wokwi não consegue resolvê-las. A
> ligação pode falhar silenciosamente e o botão nunca registrar o acionamento.
> Use sempre exatamente os nomes de terminais indicados acima.

<!-- section: flash-mode-switch -->
## 6. Chave deslizante de modo de gravação

| Campo | Valor |
|---|---|
| Identificador no Wokwi | `wokwi-slide-switch` |
| Identificador em `diagram.json` | `flash-mode-switch` |
| Papel | Seleção de modo de boot do bootloader ROM; nenhum código de `main.py` a lê — ver `hardware-reference.md`, §5 |
