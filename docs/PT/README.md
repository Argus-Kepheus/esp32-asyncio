# cess-uff

**Language / Idioma:** [English](../EN/README.md) | [Português](README.md)

Avaliação prática com ESP32 (MicroPython) para as disciplinas de
Instrumentação, Eletrônica e Lógica de Programação. Dois LEDs e um
display OLED SSD1306 reagem a um botão pulsador, simulados no
[Wokwi](https://wokwi.com).

**Simulação no Wokwi:** <https://wokwi.com/projects/471528241540407297>

## Requisitos de hardware

| Componente | Identificador no Wokwi | Pino no ESP32 |
|---|---|---:|
| Placa — Espressif ESP32-DevKitC V4 | `board-esp32-devkit-c-v4` | — |
| LED vermelho (+ resistor de 220 Ω) | `red-led` | GPIO 2 |
| LED verde (+ resistor de 220 Ω) | `green-led` | GPIO 4 |
| Botão pulsador, normalmente aberto | `push-button` | GPIO 17 |
| Display OLED, SSD1306 128×64, I2C | `oled-display` | SCL = GPIO 25, SDA = GPIO 16 |

Todos os componentes operam no barramento de 3,3 V da placa e compartilham
um terra comum. O detalhamento elétrico completo (conectores, pinos
reservados, checklist de fiação) está em
[`hardware-reference.md`](hardware-reference.md); os identificadores
exatos de cada peça estão em
[`component-specifications.md`](component-specifications.md).

## Requisitos de software

- MicroPython para ESP32.
- O `main.py` executa o piscar do LED vermelho, a lógica do botão/LED verde
  e a atualização do OLED como tarefas concorrentes de `asyncio`, de forma
  que o piscar do LED vermelho nunca é atrasado por uma atualização do OLED.
- O botão utiliza o resistor interno de redução (`Pin.PULL_DOWN`) do ESP32;
  nenhum resistor externo é necessário.
- O OLED usa I2C (`machine.I2C`) no endereço `0x3C`, controlado pelo
  `ssd1306.py`.

Os requisitos completos e as decisões de projeto estão em
[`technical-specification.md`](technical-specification.md).

## Resultado

| Estado do botão | LED verde | Mensagem no OLED |
|---|---|---|
| Solto | Apagado | `Boa sorte!` |
| Pressionado | Aceso | `Consegui` |

O LED vermelho pisca continuamente a cada 500 ms, de forma independente
do botão, do LED verde e do OLED.

## Licença

Este projeto é dedicado ao domínio público sob a licença
**CC0 1.0 Universal**. Consulte o arquivo [`LICENSE`](../../LICENSE).
