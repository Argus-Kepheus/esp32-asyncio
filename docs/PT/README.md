# esp32-asyncio

**Language / Idioma:** [English](../EN/README.md) | [Português](README.md)

Projeto pessoal com ESP32 (MicroPython) explorando processamento
assíncrono (`asyncio`), originalmente uma avaliação prática das
disciplinas de Instrumentação, Eletrônica e Lógica de Programação. Seis
LEDs piscando de forma independente, um botão pulsador acionando um LED
verde, dois LEDs indicadores de atividade, dois OLEDs SSD1306 plotando
gráficos de uso de CPU/RAM ao vivo, e um console de registro colorido em
uma tela TFT ILI9341 -- tudo simulado no [Wokwi](https://wokwi.com).

**Simulação no Wokwi:** <https://wokwi.com/projects/471528241540407297>

## Requisitos de hardware

| Componente | Identificador no Wokwi | Pino no ESP32 |
|---|---|---:|
| Placa — Espressif ESP32-DevKitC V4 | `board-esp32-devkit-c-v4` | — |
| Seis LEDs piscantes (+ resistor de 220 Ω cada) | `blue-led-1` a `blue-led-6` | GPIO 26, 14, 27, 25, 33, 12 |
| LED verde (+ resistor de 220 Ω) | `green-led` | GPIO 4 |
| Botão pulsador principal, normalmente aberto | `push-button` | GPIO 17 |
| Dois botões de velocidade (+ pull-down externo de 10 kΩ cada) | `decrease-speed-button`, `increase-speed-button` | GPIO 34, 35 |
| Dois LEDs indicadores de estado (+ resistor de 220 Ω cada) | `bus-idle-led` (laranja), `scheduler-idle-led` (amarelo) | GPIO 13, 2 |
| OLED0 de CPU, SSD1306 128×64, I2C(0) | `oled0-display` | SCL = GPIO 32, SDA = GPIO 16 |
| OLED1 de RAM, SSD1306 128×64, I2C(1) | `oled1-display` | SCL = GPIO 15, SDA = GPIO 22 |
| TFT, ILI9341 240×320, SPI | `tft-display` | SCK 18, MOSI 23, CS 5, D/C 21, RST 19 |

Os dois OLEDs e os três botões operam no barramento de 3,3 V da placa; a
TFT opera em 5 V (ver `hardware-reference.md`, §6, para a ressalva que
isso implica numa montagem física). Todos os componentes compartilham um
terra comum. O detalhamento elétrico completo (conectores, pinos
reservados, checklist de fiação) está em
[`hardware-reference.md`](hardware-reference.md); os identificadores
exatos de cada peça estão em
[`component-specifications.md`](component-specifications.md).

## Requisitos de software

- MicroPython para ESP32.
- O `main.py` executa treze fluxos concorrentes de `asyncio` -- seis
  tarefas de LED piscante, o indicador de atividade do escalonador, as
  duas tarefas de gráfico OLED, uma tarefa de status serial e três
  monitores de botão -- de forma que o piscar de nenhum LED é atrasado
  por uma atualização de mostrador além da própria escrita.
- O botão principal utiliza o resistor interno de redução
  (`Pin.PULL_DOWN`) do ESP32; os dois botões de velocidade precisam de seu
  próprio resistor externo (GPIO34/35 não têm um interno).
- Os dois OLEDs usam I2C (`machine.I2C`, um barramento cada) no endereço
  `0x3C`, controlados pelo `ssd1306.py`; a TFT usa SPI (`machine.SPI`),
  controlada pelo `ili9341.py` deste próprio projeto.

Os requisitos completos e as decisões de projeto estão em
[`technical-specification.md`](technical-specification.md).

## Resultado

Seis LEDs piscam de forma independente em um intervalo compartilhado e
ajustável pelos botões; o botão principal aciona um LED verde e registra
cada transição no console da TFT e no console serial; os dois OLEDs
plotam gráficos ao vivo de uso de CPU e RAM; e os dois LEDs indicadores
refletem, em tempo real, a atividade do barramento dos mostradores e do
escalonador.

## Licença

Este projeto é dedicado ao domínio público sob a licença
**CC0 1.0 Universal**. Consulte o arquivo [`LICENSE`](../../LICENSE).
