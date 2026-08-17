# esp32-asyncio

**Language / Idioma:** [English](../EN/README.md) | [Português](README.md)

Projeto pessoal com ESP32 (MicroPython) explorando processamento
assíncrono (`asyncio`), originalmente uma avaliação prática das
disciplinas de Instrumentação, Eletrônica e Lógica de Programação. Seis
LEDs piscando de forma independente, um botão pulsador acionando um LED
verde, dois LEDs indicadores de atividade, dois OLEDs SSD1306 plotando
gráficos de uso de CPU/RAM ao vivo, e um console de registro colorido em
uma tela TFT ILI9341 -- tudo simulado no [Wokwi](https://wokwi.com).

> **Status do projeto:** os requisitos e tabelas abaixo descrevem a
> avaliação obrigatória original. O comportamento do LED vermelho e do
> botão/LED verde continua exatamente como descrito; os números de pino
> abaixo são mantidos atualizados (ver nota em "Requisitos de
> hardware"). Já o comportamento das mensagens do OLED foi
> **substituído**, não só estendido: os dois OLEDs agora mostram
> gráficos de uso de recursos ao vivo, em vez de texto do botão. Desde
> que o escopo original foi concluído, o hardware e o `main.py` também
> foram estendidos, a pedido do usuário, com mais cinco LEDs, dois LEDs
> indicadores de atividade, um segundo OLED, um console na TFT e dois
> botões de velocidade — veja a seção "Funcionalidades estendidas" em
> [`technical-specification.md`](technical-specification.md) para o
> estado atual completo.

**Simulação no Wokwi:** <https://wokwi.com/projects/471528241540407297>

## Requisitos de hardware

| Componente | Identificador no Wokwi | Pino no ESP32 |
|---|---|---:|
| Placa — Espressif ESP32-DevKitC V4 | `board-esp32-devkit-c-v4` | — |
| LED vermelho (+ resistor de 220 Ω) | `red-led` | GPIO 26 |
| LED verde (+ resistor de 220 Ω) | `green-led` | GPIO 4 |
| Botão pulsador, normalmente aberto | `push-button` | GPIO 17 |
| Display OLED, SSD1306 128×64, I2C | `oled-display` | SCL = GPIO 32, SDA = GPIO 16 |

Os pinos do LED vermelho e do SCL do OLED foram realocados dos GPIO 2 e
GPIO 25 originalmente atribuídos, a pedido explícito do usuário, por
motivos de layout da placa (ver `technical-specification.md`, §16 —
registro de decisões); a tabela acima é mantida atualizada, não é um
registro histórico. Todos os componentes operam no barramento de 3,3 V da
placa e compartilham
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

A coluna do LED verde continua correta. A coluna da mensagem do OLED não
— foi **substituída**, não apenas estendida: nenhum dos dois OLEDs mostra
mais texto do botão, ambos são gráficos ao vivo de uso de CPU/RAM (ver
"Funcionalidades estendidas" em `technical-specification.md`).

O LED vermelho pisca continuamente a cada 500 ms, de forma independente
do botão, do LED verde e do OLED.

## Licença

Este projeto é dedicado ao domínio público sob a licença
**CC0 1.0 Universal**. Consulte o arquivo [`LICENSE`](../../LICENSE).
