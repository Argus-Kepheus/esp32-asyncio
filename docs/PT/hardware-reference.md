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
| Saída do LED vermelho | `red-led` | `red_led` / `RED_LED_PIN` | GPIO2 | J3-15 |
| Saída do LED verde | `green-led` | `green_led` / `GREEN_LED_PIN` | GPIO4 | J3-13 |
| Entrada do botão | `push-button` | `push_button` / `BUTTON_PIN` | GPIO17 | J3-11 |
| Dados I2C do OLED | `oled-display` | `oled_display` / `OLED_SDA_PIN` | GPIO16 | J3-12 |
| Relógio I2C do OLED | `oled-display` | `oled_display` / `OLED_SCL_PIN` | GPIO25 | J2-9 |
| Alimentação do OLED e do botão | — | — | 3V3 | J2-1 |

```python
RED_LED_PIN = 2
GREEN_LED_PIN = 4
BUTTON_PIN = 17
OLED_SDA_PIN = 16
OLED_SCL_PIN = 25
```

Topologia de ligação:

```text
GPIO2  ── resistor de 220 Ω ── ânodo do LED vermelho
cátodo do LED vermelho ── GND

GPIO4  ── resistor de 220 Ω ── ânodo do LED verde
cátodo do LED verde ── GND

3V3 ── botão pulsador ── GPIO17
                       entrada ativa em nível alto

GPIO25 = OLED SCL
GPIO16 = OLED SDA
3V3    = OLED VCC
GND    = OLED GND
```

Todos os periféricos devem compartilhar o mesmo GND. O OLED e o botão utilizam
somente a alimentação de 3,3 V.

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
| Configuração de inicialização | GPIO0, GPIO2, GPIO5, GPIO12, GPIO15 | São amostrados durante a inicialização. O GPIO2 é utilizado pelo LED vermelho por exigência do projeto; o conjunto LED/resistor não força externamente um nível lógico inadequado |
| UART principal | GPIO1 e GPIO3 | Usados para programação, diagnóstico e monitor serial do Wokwi; não são usados pelos periféricos funcionais |

## 6. Características elétricas

- **Nível lógico:** 3,3 V. Nunca aplique 5 V diretamente a um GPIO.
- **Referência comum:** LEDs, botão e OLED devem compartilhar o mesmo GND.
- **Limitação de corrente:** cada LED deve possuir resistor de 220 Ω em série.
- **Interface do OLED:** I2C em GPIO25 para SCL e GPIO16 para SDA. Essa
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
- ligar o LED vermelho ao GPIO2 e o LED verde ao GPIO4;
- ligar o botão entre GPIO17 e 3V3;
- não instalar resistor externo de elevação no GPIO17;
- ligar SDA do OLED ao GPIO16;
- ligar SCL do OLED ao GPIO25;
- não conectar periféricos a `CLK`, `D0`, `D1`, `D2`, `D3` ou `CMD`;
- não aplicar 5 V a nenhum GPIO.

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
