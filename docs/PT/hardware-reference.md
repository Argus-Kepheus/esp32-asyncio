<!-- doc-id: hardware-reference -->
<!-- language: PT -->
<!-- content-revision: 3 -->

# Referência de hardware da ESP32-DevKitC V4

Este documento é a fonte principal para identificação da placa física, do
módulo, do mapeamento entre GPIOs e conectores e das restrições elétricas. As
justificativas comportamentais e de software — uso de `asyncio`, escolha de I2C
em vez de SPI, estratégia de antirrepique e atualização do OLED — estão em
[`technical-specification.md`](technical-specification.md) e não
são repetidas integralmente aqui. Os identificadores dos componentes no Wokwi
estão em
[`component-specifications.md`](component-specifications.md).

<!-- section: selected-board -->
## 1. Placa selecionada

<!-- BEGIN GENERATED: board-summary -->
| Propriedade | Definição do projeto |
|---|---|
| Fabricante | Espressif Systems |
| Nome da placa | ESP32-DevKitC V4 |
| Identificador no Wokwi | `board-esp32-devkit-c-v4` (`diagram.json` id `esp32`) |
| Disposição dos conectores | 38 terminais, 19 em cada lado (J2, J3) |
| Família do microcontrolador | ESP32 |
| Módulo físico recomendado | ESP32-WROOM-32E |
| Firmware | MicroPython for ESP32 |
| Tensão lógica | 3,3 V (GPIOs não tolerantes a 5 V) |
<!-- END GENERATED: board-summary -->

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

A placa não deve ser substituída por outro tipo sem uma revisão completa do
mapeamento apresentado na §3 e do registro de decisões da §16 de
`technical-specification.md`.

<!-- section: board-rationale -->
## 2. Por que esta placa e por que “ESP32” não é suficiente

A atividade exige apenas “MicroPython para ESP32” e não determina uma placa
específica. A ESP32-DevKitC V4 foi selecionada porque:

- é uma placa oficial da Espressif;
- é suportada nativamente pelo Wokwi;
- disponibiliza todos os GPIOs exigidos pelo projeto;
- possui documentação técnica oficial;
- tem uma disposição de 38 terminais claramente definida;
- reduz ambiguidades associadas a placas genéricas e clones.

Placas denominadas genericamente “ESP32” podem variar na quantidade de
terminais, no módulo instalado, nos rótulos impressos e na disposição física.
Além disso, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, placas do tipo NodeMCU e
variantes WROVER não possuem necessariamente a mesma pinagem.

Por isso, o projeto deve ser identificado como:

```text
Espressif ESP32-DevKitC V4
Wokwi: board-esp32-devkit-c-v4
```

e não apenas como “ESP32” ou “ESP32 DevKit”.

A placa de desenvolvimento e o módulo de rádio são elementos distintos. A
DevKitC V4 é a placa portadora, com USB, regulador, botões e conectores. O
módulo metálico contém o circuito integrado ESP32, a memória flash, a antena e,
conforme a variante, PSRAM. Uma DevKitC V4 pode receber diferentes módulos.

<!-- section: gpio-header-mapping -->
## 3. Mapeamento dos GPIOs nos conectores

Todas as referências no código e no circuito utilizam o **número do GPIO do
ESP32**, e não a posição física sequencial de um terminal no conector. Por
exemplo, `GPIO25` significa o sinal denominado GPIO25, e não o vigésimo quinto
terminal físico.

<!-- BEGIN GENERATED: gpio-map -->
| Função | Identificador no Wokwi | Variável/constante em Python | GPIO | Terminal do conector |
|---|---|---|---:|---|
| Saída do LED piscante 1 | `blue-led-1` | `blue_led_1` / `BLUE_LED_1_PIN` | GPIO26 | J2-10 |
| Saída do LED piscante 2 | `blue-led-2` | `blue_led_2` / `BLUE_LED_2_PIN` | GPIO14 | J2-12 |
| Saída do LED piscante 3 | `blue-led-3` | `blue_led_3` / `BLUE_LED_3_PIN` | GPIO27 | J2-11 |
| Saída do LED piscante 4 | `blue-led-4` | `blue_led_4` / `BLUE_LED_4_PIN` | GPIO25 | J2-9 |
| Saída do LED piscante 5 | `blue-led-5` | `blue_led_5` / `BLUE_LED_5_PIN` | GPIO33 | J2-8 |
| Saída do LED piscante 6 | `blue-led-6` | `blue_led_6` / `BLUE_LED_6_PIN` | GPIO12 | J2-13 |
| Saída do LED verde | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Entrada do botão principal | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| Botão de diminuir intervalo | `decrease-speed-button` | `decrease_speed_button` / `DECREASE_SPEED_BUTTON_PIN` | GPIO34 | J2-5 |
| Botão de aumentar intervalo | `increase-speed-button` | `increase_speed_button` / `INCREASE_SPEED_BUTTON_PIN` | GPIO35 | J2-6 |
| LED de barramento ocioso (laranja) | `bus-idle-led` | `bus_idle_led` / `BUS_IDLE_LED_PIN` | GPIO13 | J2-15 |
| LED de escalonador ocioso (amarelo) | `scheduler-idle-led` | `scheduler_idle_led` / `SCHEDULER_IDLE_LED_PIN` | GPIO2 | J3-15 |
| Relógio I2C do OLED0 de CPU | `oled0-display` | `oled0_display` / `OLED0_SCL_PIN` | GPIO32 | J2-7 |
| Dados I2C do OLED0 de CPU | `oled0-display` | `oled0_display` / `OLED0_SDA_PIN` | GPIO16 | J3-12 |
| Relógio I2C do OLED1 de RAM | `oled1-display` | `oled1_display` / `OLED1_SCL_PIN` | GPIO15 | J3-16 |
| Dados I2C do OLED1 de RAM | `oled1-display` | `oled1_display` / `OLED1_SDA_PIN` | GPIO22 | J3-3 |
| Relógio SPI da TFT | `tft-display` | `tft_display` / `TFT_SCK_PIN` | GPIO18 | J3-9 |
| Dados de saída SPI da TFT | `tft-display` | `tft_display` / `TFT_MOSI_PIN` | GPIO23 | J3-2 |
| Seleção de chip da TFT | `tft-display` | `tft_display` / `TFT_CS_PIN` | GPIO5 | J3-10 |
| Dado/comando da TFT | `tft-display` | `tft_display` / `TFT_DC_PIN` | GPIO21 | J3-6 |
| Reset físico da TFT | `tft-display` | `tft_display` / `TFT_RST_PIN` | GPIO19 | J3-8 |
| Chave deslizante de modo de gravação | `flash-mode-switch` | — | GPIO0 | J3-14 |
| Alimentação dos OLEDs e dos botões | — | — | 3V3 | J2-1 |
<!-- END GENERATED: gpio-map -->

Os seis LEDs piscantes são todos fisicamente azuis (`#0000FF`) e usam a mesma numeração de 1 a 6 nos identificadores do Wokwi e do Python.

Topologia conceitual de ligação:

```text
saída ESP32 ── resistor limitador ── LED ── GND
alimentação ── botão ── entrada ESP32
entrada ESP32 ── pull-down externo ── GND   (quando necessário)
sinais de barramento ESP32 ── interface do mostrador
```

GPIOs concretos, valores de resistores, configuração de pull, IDs de barramento, endereços dos mostradores e alimentações não são repetidos na narrativa. Eles são canônicos em `config/hardware.json` e apresentados acima no mapa GPIO gerado. `diagram.json` continua sendo a autoridade para a geometria de roteamento no Wokwi.

<!-- section: module-compatibility -->
## 4. Compatibilidade dos módulos — WROOM e WROVER

O projeto necessita de GPIO16 e GPIO17 para o SDA do OLED e o botão.

| Família de módulo | Compatibilidade |
|---|---|
| ESP32-WROOM | Recomendada; GPIO16 e GPIO17 disponíveis para uso geral |
| ESP32-WROOM-32E | Alvo físico preferencial |
| ESP32-WROVER | **Não recomendada**; GPIO16 e GPIO17 podem ser usados internamente pela PSRAM |

Uma placa baseada em WROVER exigiria remapeamento de pinos em `main.py`,
`diagram.json`, na montagem e na documentação. Como GPIO16 e GPIO17 são
atribuições predefinidas do projeto, esse remapeamento está fora do escopo.

<!-- section: restricted-gpios -->
## 5. GPIOs restritos ou reservados

<!-- BEGIN GENERATED: gpio-constraints -->
| Restrição | Terminais | Motivo |
|---|---|---|
| Reservados para a memória flash SPI | `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` | Comunicação interna com a flash; não usar como GPIO do projeto |
| Somente entrada | GPIO34, GPIO35, GPIO36, GPIO37, GPIO38, GPIO39 | Não podem acionar saídas e não possuem pull-up/pull-down interno |
| Configuração de inicialização | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | Amostrados no boot; os usos do projeto são documentados e validados |
| UART principal | GPIO1, GPIO3 | Usados para programação/serial de diagnóstico; não são periféricos do projeto |
<!-- END GENERATED: gpio-constraints -->

A tabela gerada acima lista as categorias de restrição relevantes ao projeto. As observações específicas sobre pinos de inicialização e pinos somente de entrada são mantidas em `config/hardware.json`, em `gpio_constraints.notes`, evitando uma segunda lista manual que precisaria ser sincronizada quando um componente mudar de função.

Em uma montagem física, qualquer uso de pino de inicialização deve ser tratado como ponto de verificação: confirme que o circuito conectado não força um nível incompatível durante o boot. Os pinos da UART permanecem reservados para programação/REPL/diagnóstico serial, e não para periféricos normais do projeto.

<!-- section: electrical-characteristics -->
## 6. Características elétricas

- Respeite a tensão lógica da placa mostrada no resumo gerado; nunca alimente um GPIO a partir de uma régua de tensão superior.
- Todos os periféricos devem compartilhar a mesma referência de GND.
- Todo LED exige limitação de corrente; os valores atuais dos resistores são canônicos em `config/hardware.json`.
- Seleção de barramento, pinos, endereços e frequência dos OLEDs são canônicos em `config/hardware.json`; `technical-specification.md` explica por que I2C foi escolhido.
- A alimentação da TFT e o mapeamento SPI também são canônicos em `config/hardware.json`. Em hardware físico, confirme se o módulo ILI9341 específico possui o regulador/conversão de nível esperados pela ligação de alimentação antes de energizá-lo.
- A configuração de pull dos botões é canônica em `config/hardware.json`; o antirrepique é uma questão de runtime/software documentada em `technical-specification.md`.

<!-- section: physical-checklist -->
## 7. Lista de verificação para implementação física

Para uma futura montagem real (o projeto atual tem como alvo a simulação):

- confirme a placa/módulo exatos usando o resumo gerado e a seção de compatibilidade de módulos;
- reproduza todas as conexões de sinal a partir do mapa GPIO gerado, e não de exemplos narrativos;
- reproduza valores de resistores, configuração de pull e alimentações a partir de `config/hardware.json`;
- mantenha todos os GNDs comuns;
- revise todas as restrições de pinos de inicialização, somente entrada e reservados antes da montagem;
- confirme as características elétricas dos módulos OLED e ILI9341 realmente utilizados antes de energizar;
- trate `diagram.json` como netlist/layout da simulação, não como prova de que um módulo físico inclui circuitos de proteção/regulação;
- execute novamente os diagnósticos manuais após a montagem.

<!-- section: references -->
## 8. Referências

**Espressif e MicroPython:**

- [Guia da ESP32-DevKitC V4](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
- [Folha de dados do ESP32](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
- [Folha de dados do ESP32-WROOM-32E](https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf)
- [Referência rápida do MicroPython para ESP32](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [`machine.Pin`](https://docs.micropython.org/en/latest/library/machine.Pin.html)
- [`machine.I2C`](https://docs.micropython.org/en/latest/library/machine.I2C.html)
- [`asyncio`](https://docs.micropython.org/en/latest/library/asyncio.html)

**Wokwi:**

- [Componente `board-esp32-devkit-c-v4`](https://docs.wokwi.com/parts/board-esp32-devkit-c-v4)
- [Formato de `diagram.json`](https://docs.wokwi.com/diagram-format)

<!-- section: board-identification -->
## 9. Declaração de identificação da placa

Texto recomendado para relatórios e documentação de entrega:

> O projeto utiliza a placa de desenvolvimento oficial Espressif
> ESP32-DevKitC V4, representada no Wokwi pelo componente
> `board-esp32-devkit-c-v4`. Uma implementação física deve utilizar,
> preferencialmente, uma ESP32-DevKitC V4 com módulo ESP32-WROOM-32E, para que
> GPIO16 e GPIO17 permaneçam disponíveis às conexões predefinidas do OLED e do
> botão. Todas as referências de pinagem utilizam números de GPIO do ESP32, e
> não posições físicas sequenciais dos conectores.
