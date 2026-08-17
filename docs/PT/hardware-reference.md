# Referência de hardware da ESP32-DevKitC V4

Este documento é a fonte principal para identificação da placa física, do
módulo, do mapeamento entre GPIOs e conectores e das restrições elétricas. As
justificativas comportamentais e de software — uso de `asyncio`, escolha de I2C
em vez de SPI, estratégia de antirrepique e atualização do OLED — estão em
[`technical-specification.md`](technical-specification.md) e não
são repetidas integralmente aqui. Os identificadores dos componentes no Wokwi
estão em
[`component-specifications.md`](component-specifications.md).

## 1. Placa selecionada

| Propriedade | Definição do projeto |
|---|---|
| Fabricante | Espressif Systems |
| Nome da placa | ESP32-DevKitC V4 |
| Identificador no Wokwi | `board-esp32-devkit-c-v4`, com identificador `esp32` em `diagram.json` |
| Disposição dos conectores | 38 terminais, 19 em cada lado, conectores J2 e J3 |
| Família do microcontrolador | ESP32 original |
| Módulo físico recomendado | ESP32-WROOM-32E |
| Firmware | MicroPython para ESP32 |
| Tensão lógica | 3,3 V; os GPIOs não são tolerantes a 5 V |

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

A placa não deve ser substituída por outro tipo sem uma revisão completa do
mapeamento apresentado na §3 e do registro de decisões da §16 de
`technical-specification.md`.

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

## 3. Mapeamento dos GPIOs nos conectores

Todas as referências no código e no circuito utilizam o **número do GPIO do
ESP32**, e não a posição física sequencial de um terminal no conector. Por
exemplo, `GPIO25` significa o sinal denominado GPIO25, e não o vigésimo quinto
terminal físico.

| Função | Identificador no Wokwi | Variável/constante em Python | GPIO | Terminal do conector |
|---|---|---|---:|---|
| Saída do LED vermelho | `red-led` | `red_led` / `RED_LED_PIN` | GPIO26 | J2-10 |
| Saída do LED verde | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Entrada do botão | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| Dados I2C do OLED | `oled-display` | `oled_display` / `OLED_SDA_PIN` | GPIO16 | J3-12 |
| Relógio I2C do OLED | `oled-display` | `oled_display` / `OLED_SCL_PIN` | GPIO32 | J2-7 |
| Alimentação do OLED e do botão | — | — | 3V3 | J2-1 |

Os pinos do LED vermelho e do SCL do OLED foram realocados dos GPIO2/GPIO25
originalmente atribuídos (registrados em `technical-specification.md`,
§16) a pedido explícito do usuário, por motivos de layout da placa. Esta
tabela reflete a fiação atual, não a atribuição original.

```python
RED_LED_PIN = 26
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SDA_PIN = 16
OLED_SCL_PIN = 32
```

Topologia de ligação:

```text
GPIO26 ── resistor de 220 Ω ── ânodo do LED vermelho
cátodo do LED vermelho ── GND

GPIO4  ── resistor de 220 Ω ── ânodo do LED verde
cátodo do LED verde ── GND

3V3 ── botão pulsador ── GPIO17
                       entrada ativa em nível alto

GPIO32 = OLED SCL
GPIO16 = OLED SDA
3V3    = OLED VCC
GND    = OLED GND
```

Todos os periféricos devem compartilhar o mesmo GND. O OLED e o botão utilizam
somente a alimentação de 3,3 V.

### 3.1 Mapeamento de hardware estendido nos conectores

Tudo que foi adicionado depois dos cinco sinais originais acima, a pedido
explícito do usuário (ver "Funcionalidades estendidas" em
`technical-specification.md` para a justificativa comportamental — esta
tabela cobre só a fiação física). Diferente da §3, esse hardware ainda
está em desenvolvimento ativo e esta tabela pode ficar atrás da última
iteração; as constantes de pino do `main.py` são a fonte definitiva.

| Função | Variável/constante em Python | GPIO | Terminal do conector |
|---|---|---:|---|
| Saída do LED azul | `blue_led` / `BLUE_LED_PIN` | GPIO14 | J2-12 |
| Saída do LED amarelo | `yellow_led` / `YELLOW_LED_PIN` | GPIO27 | J2-11 |
| Saída do LED branco | `white_led` / `WHITE_LED_PIN` | GPIO25 | J2-9 |
| Saída do LED laranja | `orange_led` / `ORANGE_LED_PIN` | GPIO33 | J2-8 |
| Saída do segundo LED vermelho | `red_led_2` / `RED_LED_2_PIN` | GPIO12 | J2-13 |
| Botão de diminuir intervalo | `decrease_speed_button` / `DECREASE_SPEED_BUTTON_PIN` | GPIO34 | J2-5 |
| Botão de aumentar intervalo | `increase_speed_button` / `INCREASE_SPEED_BUTTON_PIN` | GPIO35 | J2-6 |
| LED de barramento ocioso (laranja) | `bus_idle_led` / `BUS_IDLE_LED_PIN` | GPIO13 | J2-15 |
| LED de escalonador ocioso (amarelo) | `scheduler_idle_led` / `SCHEDULER_IDLE_LED_PIN` | GPIO2 | J3-15 |
| Relógio I2C do segundo OLED | `oled_display_2` / `OLED2_SCL_PIN` | GPIO15 | J3-16 |
| Dados I2C do segundo OLED | `oled_display_2` / `OLED2_SDA_PIN` | GPIO22 | J3-3 |
| Relógio SPI da TFT | `tft_display` / `TFT_SCK_PIN` | GPIO18 | J3-9 |
| Dados de saída SPI da TFT | `tft_display` / `TFT_MOSI_PIN` | GPIO23 | J3-2 |
| Seleção de chip da TFT | `tft_display` / `TFT_CS_PIN` | GPIO5 | J3-10 |
| Dado/comando da TFT | `tft_display` / `TFT_DC_PIN` | GPIO21 | J3-6 |
| Reset físico da TFT | `tft_display` / `TFT_RST_PIN` | GPIO19 | J3-8 |
| Chave deslizante de modo gravação | — (só no `diagram.json`, nenhum código do `main.py` a lê) | GPIO0 | J3-14 |

Notas específicas deste conjunto estendido:

- GPIO34/35 (os dois botões de velocidade) são pinos somente entrada, sem
  resistor de pull-down interno, diferente do `Pin.PULL_DOWN` do
  `BUTTON_PIN` — cada um precisa do próprio resistor externo de 10 kΩ
  até o GND (já presente no `diagram.json`; ver
  `tests/09_speed_buttons.py`).
- O GPIO2 agora hospeda o `scheduler_idle_led`, não mais o LED vermelho
  (que passou para o GPIO26, liberando o GPIO2) — ver a nota atualizada
  sobre inicialização na §5.
- O GPIO25, liberado pela mudança do SCL do OLED, agora é o pino do
  `white_led`.
- O segundo OLED usa um segundo barramento I2C de hardware, independente
  (`machine.I2C(1)`), não um segundo endereço no primeiro barramento, para
  rodar ao mesmo tempo que o primeiro OLED sem disputa.
- O GPIO0 (chave de modo gravação) é lido pelo bootloader ROM antes de
  qualquer script MicroPython rodar; nenhum código do `main.py` interage
  com ele. Ver §7.

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

## 5. GPIOs restritos ou reservados

| Restrição | Terminais | Motivo |
|---|---|---|
| Reservados para a memória flash SPI | `CLK`, `D0`, `D1`, `D2`, `D3`, `CMD` | Comunicação interna com a memória flash; usá-los como GPIO pode impedir a inicialização do firmware |
| Somente entrada | GPIO34 a GPIO39 | Não podem acionar saídas e não possuem resistores internos de elevação ou redução |
| Configuração de inicialização | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | Amostrados durante a inicialização para selecionar o modo de boot -- ver abaixo o papel de cada um neste projeto e por que não interfere |
| UART principal | GPIO1 e GPIO3 | Usados para programação, diagnóstico e monitor serial do Wokwi; não são usados pelos periféricos funcionais |

Notas por pino, específicas deste projeto (nenhum força um nível externo
contra o estado normal de boot do pino, mas o raciocínio difere por pino
-- não é uma única justificativa genérica para os cinco):

- **GPIO0** -- a chave deslizante de modo de gravação (§3.1). Não é lida
  por nenhum código de `main.py`; a própria chave é o mecanismo de
  seleção de modo de boot, usada deliberadamente durante uma gravação
  real, não durante a operação normal.
- **GPIO2** -- saída do `scheduler_idle_led`. Circuito simples de
  LED-mais-resistor para GND: só drena corrente depois que o firmware o
  configura como saída, nunca força um nível alto externo antes disso.
- **GPIO5** -- saída de seleção de circuito (CS) da TFT. Ligado apenas à
  entrada de alta impedância do controlador ILI9341, sem nenhum resistor
  externo disputando o nível do pino -- nada no circuito contraria o
  *pull* padrão do próprio ESP32 nesse pino durante o boot.
- **GPIO12** -- saída do `red_led_2`. Mesmo raciocínio do GPIO2: circuito
  simples de LED-mais-resistor, só drena corrente.
- **GPIO15** -- relógio I2C do segundo OLED (SCL), sinal bidirecional. Um
  barramento I2C em repouso fica em nível alto (via resistores de
  *pull-up*, internos ou no próprio módulo OLED), o que tende a
  concordar com, não contrariar, o estado padrão de boot deste pino --
  mas isso depende de o módulo OLED específico já estar energizado
  naquele instante exato. Trate este como o menos garantido dos cinco
  para uma montagem física; verifique diretamente se houver problemas de
  boot depois de ligar o segundo OLED.

Nota sobre GPIO1/GPIO3: mesmo sem nenhum LED ou botão ligado a eles no
`diagram.json`, esses pinos não estão "livres" ou ociosos. O `diagram.json`
conecta `esp32:TX` / `esp32:RX` ao `$serialMonitor` — o mesmo canal UART0
usado pelo REPL do MicroPython e por todo `print()` do código. Na prática,
é esse canal que exibe a linha periódica `"CPU: ...% | RAM: ...% | Blue
LEDs interval: ... ms"` do `print_status()` (e os diagnósticos de falha
de inicialização do OLED/TFT).

## 6. Características elétricas

- **Nível lógico:** 3,3 V. Nunca aplique 5 V diretamente a um GPIO.
- **Referência comum:** LEDs, botão e OLED devem compartilhar o mesmo GND.
- **Limitação de corrente:** cada LED deve possuir resistor de 220 Ω em série.
- **Interface do OLED:** I2C em GPIO32 para SCL e GPIO16 para SDA. Essa
  atribuição é uma predefinição do projeto, não uma otimização.
- **Botão:** ligado entre GPIO17 e 3V3; o nível em repouso é definido pelo
  `Pin.PULL_DOWN` interno.
- **Filtro de entrada:** não há filtro RC externo; o repique é tratado por
  software.

## 7. Lista de verificação para implementação física

Para uma futura montagem real:

- usar uma ESP32-DevKitC V4, ou equivalente comprovadamente compatível, com
  módulo WROOM e não WROVER;
- alimentar o OLED em 3,3 V;
- interligar todos os GNDs;
- instalar um resistor de 220 Ω em série com cada LED;
- ligar o LED vermelho ao GPIO26 e o LED verde ao GPIO4;
- ligar o botão entre GPIO17 e 3V3;
- não instalar resistor externo de elevação no GPIO17;
- ligar SDA do OLED ao GPIO16;
- ligar SCL do OLED ao GPIO32;
- não conectar periféricos a `CLK`, `D0`, `D1`, `D2`, `D3` ou `CMD`;
- não aplicar 5 V a nenhum GPIO.

Para o hardware estendido (§3.1) — ainda em evolução, então trate como um
ponto de partida, não uma lista final:

- os cinco LEDs extras têm cada um seu próprio resistor de 220 Ω em série;
- os dois botões de velocidade têm cada um seu próprio resistor externo
  de 10 kΩ até o GND (não há resistor interno disponível no GPIO34/35);
- o SCL/SDA do segundo OLED (GPIO15/22) estão ligados ao próprio
  barramento, não compartilhado com o GPIO32/16 do primeiro OLED;
- a linha RST da TFT (GPIO19) é fiada mesmo que algumas peças de TFT do
  Wokwi a marquem como inerte na simulação — um painel real precisa dela;
- confirme qual tipo de módulo ILI9341 está em mãos antes de ligar o VCC:
  o `diagram.json` deste projeto alimenta a TFT pelo pino de 5~V do ESP32,
  seguro apenas para um módulo com regulador de 3,3~V e conversão de
  nível embutidos (comum em placas de \textit{breakout}); um painel
  ILI9341 "nu", sem esses circuitos de suporte, deve ser alimentado em
  3,3~V. As cinco linhas de dados/controle (SCK, MOSI, CS, D/C, RST)
  permanecem em lógica de 3,3~V em ambos os casos, pois partem
  diretamente dos GPIOs do ESP32, não da própria alimentação da tela.

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

## 9. Declaração de identificação da placa

Texto recomendado para relatórios e documentação de entrega:

> O projeto utiliza a placa de desenvolvimento oficial Espressif
> ESP32-DevKitC V4, representada no Wokwi pelo componente
> `board-esp32-devkit-c-v4`. Uma implementação física deve utilizar,
> preferencialmente, uma ESP32-DevKitC V4 com módulo ESP32-WROOM-32E, para que
> GPIO16 e GPIO17 permaneçam disponíveis às conexões predefinidas do OLED e do
> botão. Todas as referências de pinagem utilizam números de GPIO do ESP32, e
> não posições físicas sequenciais dos conectores.
