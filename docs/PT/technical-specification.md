# Especificação técnica — esp32-asyncio

## 1. Controle do documento

| Campo | Valor |
|---|---|
| Projeto | Projeto pessoal de exploração do asyncio no ESP32 |
| Disciplinas | Instrumentação, Eletrônica e Lógica de Programação |
| Plataforma-alvo | ESP32 com MicroPython |
| Plataforma de simulação | Wokwi |
| Placa virtual | Espressif ESP32-DevKitC V4 |
| Executável principal | `main.py` |
| Controlador do OLED | `ssd1306.py` |
| Definição do circuito | `diagram.json` |
| Configuração do Wokwi para VS Code | `wokwi.toml` |
| Licença | CC0 1.0 Universal |
| Idioma desta versão | Português do Brasil |
| Mensagens exibidas no OLED | Português, conforme requisito explícito |

Este documento consolida os requisitos e as decisões de engenharia do
projeto. Comentários de outros projetistas podem ser incorporados em revisões futuras,
desde que o comportamento obrigatório e a rastreabilidade das decisões sejam
preservados. Consulte a §7.

## 2. Objetivo

Desenvolver e simular uma aplicação MicroPython para ESP32 que execute
concorrentemente:

1. o piscar de seis LEDs, cada um em sua própria tarefa `asyncio`, todos
   compartilhando um intervalo ajustável;
2. a leitura de um botão pulsador normalmente aberto e ativo em nível alto,
   acionando um LED verde;
3. a leitura de mais dois botões pulsadores que aceleram ou desaceleram
   todos os seis LEDs piscantes ao mesmo tempo;
4. gráficos ao vivo de uso de CPU e RAM em dois OLEDs SSD1306
   independentes;
5. um console de registro colorido, por subsistema, em uma TFT ILI9341,
   espelhado no console serial; e
6. dois LEDs indicadores de estado, refletindo a atividade do barramento
   dos mostradores e do escalonador.

Os entregáveis são:

- um arquivo `main.py` completo e executável;
- o código e a documentação publicados em um repositório GitHub;
- um endereço compartilhável do projeto no Wokwi, contendo o circuito
  executável.

## 3. Decisão sobre a plataforma de simulação

O Wokwi é a plataforma oficial deste projeto.

**Justificativa:** o Wokwi oferece suporte nativo à simulação de ESP32, ao
MicroPython com um `main.py` completo, ao display SSD1306 por I2C, à definição
do circuito em `diagram.json`, à interação com botões e LEDs e ao
compartilhamento do projeto por endereço público.

O Tinkercad Circuits foi descartado para esta atividade porque não executa o
mesmo `main.py` em MicroPython para ESP32 e, portanto, não atende diretamente
ao entregável de código-fonte estabelecido. Essa decisão não significa que o
Tinkercad não possua valor didático em outros contextos.

### 3.1 Seleção da placa

O circuito utiliza:

```json
{ "type": "board-esp32-devkit-c-v4", "id": "esp32" }
```

A ESP32-DevKitC V4 foi selecionada porque:

- é uma placa oficial da Espressif;
- é suportada nativamente pelo Wokwi;
- disponibiliza todos os GPIOs exigidos;
- possui documentação oficial de fabricante;
- reduz ambiguidades associadas a placas genéricas ou clones;
- oferece correspondência clara entre a simulação e uma futura montagem
  física.

A escolha não se deve a uma vantagem de desempenho específica. Outra placa
ESP32 poderia executar a lógica, mas exigiria revisão integral da pinagem, do
circuito e da documentação.

Para uma futura implementação física, recomenda-se uma ESP32-DevKitC V4 com
módulo ESP32-WROOM-32E. Variantes WROVER não são recomendadas porque GPIO16 e
GPIO17 podem estar reservados à PSRAM.

## 4. Requisitos funcionais

### RF-01 — Seis LEDs piscantes

- Identificadores no Wokwi: `red-led`, `blue-led`, `yellow-led`,
  `white-led`, `orange-led`, `red-led-2`;
- variáveis em Python: `red_led`, `blue_led`, `yellow_led`, `white_led`,
  `orange_led`, `red_led_2`;
- constantes: `RED_LED_PIN` (GPIO 26), `BLUE_LED_PIN` (14),
  `YELLOW_LED_PIN` (27), `WHITE_LED_PIN` (25), `ORANGE_LED_PIN` (33),
  `RED_LED_2_PIN` (12);
- todos fisicamente azuis (`#0000FF`) em `diagram.json`; os identificadores
  Python são apenas rótulos individuais, não descrições de cor;
- cada um em sua própria tarefa `asyncio` independente (`blink_led()`,
  a partir da lista `BLINKING_LEDS`);
- alternância em um intervalo-base de 500 ms, compartilhado e ajustável
  (RF-03);
- logicamente independentes entre si -- nenhum chama ou espera outro --,
  embora todos compartilhem o mesmo escalonador cooperativo (nota de
  engenharia da §5.3).

### RF-02 — Botão pulsador e LED verde

- Identificadores no Wokwi: `push-button`, `green-led`;
- variáveis em Python: `push_button`, `green_led`;
- constantes: `BUTTON_PIN` (GPIO 17), `GREEN_LED_PIN` (GPIO 4);
- botão: normalmente aberto e momentâneo, `Pin.IN` com `Pin.PULL_DOWN`
  interno; solto = LOW, pressionado = HIGH;
- LED verde: botão solto → apagado, botão pressionado → aceso;
- cada transição estável é registrada via `console_log()`, em verde
  (RF-05).

### RF-03 — Botões de velocidade

- Identificadores no Wokwi: `decrease-speed-button`,
  `increase-speed-button`;
- variáveis em Python: `decrease_speed_button`, `increase_speed_button`;
- constantes: `DECREASE_SPEED_BUTTON_PIN` (GPIO 34),
  `INCREASE_SPEED_BUTTON_PIN` (GPIO 35);
- pinos somente de entrada, sem resistor interno de redução -- cada um
  precisa de seu próprio resistor externo de 10 kΩ até o GND (já em
  `diagram.json`);
- cada pressão escala o intervalo de todos os LEDs piscantes pelo mesmo
  fator de potência de dois, limitado a [125 ms, 4 s]
  (`BLINK_SPEED_STEP_MIN`/`_MAX`).

### RF-04 — Dois gráficos de uso de recursos nos OLEDs

- Identificadores no Wokwi: `oled-display`, `oled-display-2`;
- variáveis em Python: `oled_display`, `oled_display_2`;
- controlador: SSD1306 · resolução: 128 × 64 pixels · endereço `0x3C` em
  ambos;
- primeiro OLED: `machine.I2C(0)`, SCL GPIO 32, SDA GPIO 16 -- plota o
  gráfico de "CPU" (§17.2);
- segundo OLED: `machine.I2C(1)`, SCL GPIO 15, SDA GPIO 22 -- barramento
  I2C de hardware próprio, independente; plota o gráfico de "RAM";
- ambos redesenhados a cada 250 ms no mínimo
  (`CPU_GRAPH_SAMPLE_INTERVAL_MS` / `RAM_GRAPH_SAMPLE_INTERVAL_MS`, um piso,
  não um período exato — §9).

### RF-05 — Console de registro na TFT

- Identificador no Wokwi: `tft-display`;
- variável em Python: `tft_display`;
- controlador: ILI9341 · SPI genuíno de 4 fios: SCK GPIO 18, MOSI GPIO 23,
  CS GPIO 5, D/C GPIO 21, RST GPIO 19;
- `console_log()` escreve uma linha colorida por evento do sistema (uma
  cor por subsistema), voltando ao topo da tela ao preenchê-la, e sempre
  espelha cada linha no console serial também, independente da presença
  da TFT (§17.4).

### RF-06 — LEDs indicadores de estado

- Identificadores no Wokwi: `bus-idle-led`, `scheduler-idle-led`;
- variáveis em Python: `bus_idle_led`, `scheduler_idle_led`;
- constantes: `BUS_IDLE_LED_PIN` (GPIO 13), `SCHEDULER_IDLE_LED_PIN`
  (GPIO 2);
- laranja (`bus_idle_led`): aceso por padrão, apaga apenas durante uma
  escrita instrumentada em algum mostrador -- leitura invertida de
  "barramento ocupado";
- amarelo (`scheduler_idle_led`): alterna a cada iteração de
  `scheduler_idle_task()` -- uma visualização grosseira de vazão do
  escalonador, não um sinal literal de ociosidade/prioridade (§17).

## 5. Arquitetura de software

### 5.1 Arquitetura assíncrona

O projeto utiliza exclusivamente `asyncio` do MicroPython. Treze fluxos
concorrentes rodam sob um único escalonador:

- `blink_led(entry)` -- seis tarefas independentes, uma por entrada de
  `BLINKING_LEDS`, cada uma alternando seu próprio LED no intervalo
  compartilhado (RF-01);
- `scheduler_idle_task()` -- uma tarefa, alternando o LED amarelo a cada
  iteração (RF-06);
- `update_cpu_graph()` / `update_ram_graph()` -- uma tarefa por OLED,
  redesenhando seu gráfico de recursos (RF-04);
- `print_status()` -- uma tarefa, imprimindo a linha periódica de status
  no serial;
- `monitor_step_button()` -- duas tarefas, uma por botão de velocidade
  (RF-03), cada uma criada com `asyncio.create_task()`;
- `monitor_button()` -- o monitor do botão principal (RF-02), a única das
  treze que `main()` aguarda (`await`) diretamente em vez de despachar com
  `create_task()`; como nunca retorna, `main()` nunca termina sozinha, mas
  isso não a distingue das outras doze em termos de comportamento de
  escalonamento.

As pausas são realizadas com:

```python
await asyncio.sleep_ms(...)
```

### 5.2 Rejeição de atrasos bloqueantes

Chamadas como:

```python
time.sleep(0.5)
time.sleep_ms(500)
```

interrompem a execução do interpretador durante o intervalo e podem impedir ou
atrasar:

- a leitura do botão;
- a resposta do LED verde;
- a atualização do display;
- a execução de futuras tarefas.

Por esse motivo, atrasos bloqueantes são permitidos apenas em programas
temporários de diagnóstico isolado, nunca no `main.py` entregue.

### 5.3 Rejeição do superlaço temporizado manualmente

Uma implementação com `time.ticks_ms()` e `time.ticks_diff()` pode ser leve e
adequada a sistemas muito pequenos. Entretanto, o projeto não adota essa
estrutura como arquitetura principal.

A solução com `asyncio` foi escolhida porque proporciona:

- separação mais clara de responsabilidades;
- melhor legibilidade;
- manutenção mais simples;
- expansão mais segura para novos sensores e atuadores;
- menor acoplamento entre temporizações;
- pausas cooperativas explícitas via `await asyncio.sleep_ms()`, de forma
  que nenhum LED trave esperando por outra tarefa ou por uma atualização
  de mostrador.

**Nota de engenharia -- o que o `asyncio` não resolve aqui:** os
drivers `ssd1306` e `ili9341` fazem escritas I2C/SPI síncronas e
bloqueantes dentro de `show()`/`fill_rect()`/`text()` (sem nenhum ponto
`await` interno). Essa escrita bloqueia a CPU pela mesma duração
independente de o código ao redor usar `asyncio`, um superlaço manual ou
nada. O `asyncio` foi adotado por escalabilidade e organização de código,
não para tornar a E/S dos mostradores não bloqueante -- documentado aqui
explicitamente para evitar essa suposição incorreta mais adiante (ver
§17.2 para o impacto medido dessas escritas).

### 5.4 Temporizadores de hardware

Temporizadores de hardware não são necessários para o requisito de 500 ms. A
tolerância temporal da aplicação é compatível com `asyncio`, e a adoção de
interrupções ou funções de retorno de temporizador acrescentaria complexidade
sem benefício funcional relevante.

## 6. Projeto do circuito

### 6.1 LEDs e resistores

Todos os nove LEDs (seis piscantes, o verde e os dois indicadores) possuem
resistor limitador de 220 Ω em série, com o cátodo ligado ao GND comum.

```text
GPIO26 ── 220 Ω ── ânodo do primeiro LED piscante
cátodo ── GND

GPIO4 ── 220 Ω ── ânodo do LED verde
cátodo ── GND
```

O GPIO2 aciona hoje o `scheduler_idle_led` (§17); esse uso é seguro porque
o circuito externo (LED + resistor até o GND) só drena corrente, nunca
impõe um nível externo durante a energização (ver `docs/PT/hardware-reference.md`,
§5, para a tabela completa dos pinos de *bootstrapping*).

### 6.2 Botão, resistor interno e antirrepique

O botão é ligado entre 3V3 e GPIO17:

```text
3V3 ── botão normalmente aberto ── GPIO17
```

A entrada utiliza:

```python
push_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
```

Assim:

- contato aberto: LOW;
- contato fechado: HIGH.

Não é instalado resistor externo de redução e não é empregado filtro RC. O
tratamento do repique é realizado por software, de maneira não bloqueante.

Estratégia adotada:

- amostragem aproximada a cada 5 ms;
- identificação de um estado candidato;
- aceitação da mudança somente após aproximadamente 30 ms de estabilidade;
- geração de uma única transição lógica por acionamento.

Esse intervalo é imperceptível ao usuário e evita oscilações no LED verde e
atualizações repetidas do OLED.

Os nomes dos terminais do botão em `diagram.json` devem respeitar exatamente:

```text
1.l, 1.r, 2.l, 2.r
```

### 6.3 Por que I2C nos dois OLEDs, e SPI na TFT

O projeto determina, para o primeiro OLED:

```text
GPIO32 = SCL
GPIO16 = SDA
```

e, para o segundo OLED, em um barramento `machine.I2C(1)` independente:

```text
GPIO15 = SCL
GPIO22 = SDA
```

Essa atribuição não foi escolhida por ser o mapeamento padrão do ESP32 nem
por um estudo de desempenho; é declarada explicitamente no código, no
circuito e na documentação, e repetida da mesma forma nos dois barramentos.

A versão consolidada utiliza `machine.I2C` (barramento de hardware), que
declara os sinais de forma explícita:

```python
i2c = I2C(
    0,
    scl=Pin(OLED_SCL_PIN),
    sda=Pin(OLED_SDA_PIN),
    freq=400_000,
)
```

Uma revisão anterior utilizava `machine.SoftI2C` de forma defensiva, sem
confirmação de que fosse necessário. Os diagnósticos vigentes,
`tests/05_cpu_oled_basic.py` e `tests/06_cpu_oled_full_diagnostic.py`, usam
GPIO32 (SCL) e GPIO16 (SDA) e foram aprovados no Wokwi web em 18/08/2026;
consulte a §16.

Os dois displays também necessitam de VCC e GND. Esses terminais são conexões
de alimentação, e não sinais de comunicação.

I2C foi mantido para os dois OLEDs porque:

- usa apenas dois sinais por barramento, mantendo baixo o total de pinos
  mesmo com dois displays;
- o componente `board-ssd1306` do Wokwi utiliza a variante I2C;
- o conteúdo de cada um -- um gráfico de barras redesenhado periodicamente
  -- não precisa da maior taxa de transferência do SPI para se manter
  responsivo num piso de atualização de 250 ms (§9).

O console da TFT (RF-05) é um caso à parte: usa SPI genuíno de 4 fios (SCK,
MOSI, CS, D/C, mais RST), porque o controlador ILI9341 usado aqui é uma
peça SPI e porque o quadro colorido maior (240×320) da tela se beneficia da
maior taxa de transferência do SPI. São duas decisões independentes para
dois displays diferentes, não uma única restrição de projeto.

## 7. Integração de comentários e revisões

Comentários complementares de outros projetistas podem ser integrados quando:

1. identificarem claramente o requisito ou decisão afetada;
2. não alterarem silenciosamente a pinagem obrigatória;
3. preservarem os identificadores do código e do Wokwi;
4. apresentarem justificativa técnica;
5. forem registrados por confirmação de alteração no Git;
6. atualizarem todos os documentos afetados.

Em caso de conflito, os requisitos obrigatórios da atividade têm precedência.
Uma alteração funcional deve atualizar, no mínimo:

- `main.py`;
- `diagram.json`;
- `README.md`;
- `component-specifications.md`;
- `hardware-reference.md`;
- `technical-specification.md`;
- testes e critérios de aceitação.

## 8. Convenções de nomes

### 8.1 Identificadores no Wokwi

```text
red-led
green-led
push-button
oled-display
```

### 8.2 Variáveis em Python

```python
red_led
green_led
push_button
oled_display
```

### 8.3 Constantes em Python

```python
RED_LED_PIN
GREEN_LED_PIN
BUTTON_PIN
OLED_SDA_PIN
OLED_SCL_PIN
```

Identificadores Python não podem conter hífen; por isso, usam sublinhado.

## 9. Estratégia de atualização dos gráficos OLED

Os dois OLEDs redesenham em uma janela de amostragem fixa --
`CPU_GRAPH_SAMPLE_INTERVAL_MS` / `RAM_GRAPH_SAMPLE_INTERVAL_MS`, hoje
250 ms cada -- não em um evento de mudança de estado do botão ou similar:

- `update_cpu_graph()` e `update_ram_graph()` rodam cada um seu próprio
  laço `while True`, redesenhando a cada iteração e então fazendo
  `await asyncio.sleep_ms(250)`;
- `asyncio.sleep_ms()` garante apenas um atraso mínimo, então a janela de
  amostragem é medida com `time.ticks_us()`, não assumida como exata --
  uma iteração mais lenta (por exemplo, uma escrita concorrente de
  `console_log()`) empurra o intervalo real além de 250 ms, e
  `update_cpu_graph()` leva isso em conta explicitamente ao calcular sua
  porcentagem (§17.2);
- cada redesenho faz um `fill()` completo e replota todo o histórico
  rolante, não só a coluna mais nova, já que `framebuf` não tem primitiva
  para deslocar pixels existentes para a esquerda.

Isto é redesenho periódico incondicional, não uma atualização orientada por
eventos: os dois OLEDs são, eles próprios, parte do que mantém o
processador ocupado (a medição de "CPU" do §17.2), então redesenhar
continuamente é intencional aqui, não algo a minimizar.

## 10. Estrutura do repositório

```text
esp32-asyncio/
├── main.py
├── ssd1306.py
├── ili9341.py
├── diagram.json
├── wokwi.toml
├── README.md
├── LICENSE
├── .gitignore
├── firmware.bin        (baixado localmente por cada dev; não versionado)
├── docs/
│   ├── EN/
│   │   ├── README.md
│   │   ├── component-specifications.md
│   │   ├── hardware-reference.md
│   │   └── technical-specification.md
│   └── PT/
│       ├── README.md
│       ├── component-specifications.md
│       ├── hardware-reference.md
│       └── technical-specification.md
├── tests/
│   ├── README.md
│   └── 01_blue_led_basic.py ... 13_tft_text_diagnostic.py  (13 scripts)
└── report/
    ├── README.md
    ├── build.ps1
    ├── relatorio.tex
    ├── relatorio.pdf
    └── figures/
        └── circuito-wokwi.png
```

A licença é CC0 1.0 Universal.

## 11. Simulação no Wokwi pelo navegador

O circuito é montado no arquivo `diagram.json`. Esse arquivo contém:

- tipo e identificador de cada componente;
- coordenadas visuais;
- atributos;
- conexões elétricas;
- cores e rotas gráficas dos fios.

Mover apenas o trajeto de um fio altera as instruções visuais de roteamento,
mas não muda a conexão elétrica enquanto as extremidades permanecerem iguais.

O projeto no navegador deve conter `main.py`, `ssd1306.py`, `ili9341.py` e
`diagram.json`.
Após a validação, deve ser salvo na conta do usuário e compartilhado por um
endereço público do Wokwi.

## 12. VS Code e GitHub

O GitHub é a fonte versionada do projeto. O Wokwi on-line é a apresentação
interativa e executável do circuito.

No VS Code:

- `wokwi.toml` define o firmware e a porta serial simulada;
- `firmware.bin` é obtido separadamente e não deve ser registrado no Git;
- `mpremote` envia `main.py` e `ssd1306.py` ao sistema de arquivos simulado;
- o sistema de arquivos da simulação pode ser recriado a cada sessão.

Os endereços do GitHub e do Wokwi devem ser apresentados separadamente.

## 13. Entregáveis

| Entregável | Conteúdo |
|---|---|
| Código-fonte | `main.py` completo e executável |
| Controlador dos OLEDs | `ssd1306.py` |
| Controlador da TFT | `ili9341.py` |
| Circuito | `diagram.json` |
| Configuração local | `wokwi.toml` |
| Testes de diagnóstico | `tests/` (treze scripts, não fazem parte do entregável) |
| Relatório técnico | `report/` (`relatorio.tex`, `relatorio.pdf`) |
| Repositório | Endereço público do GitHub |
| Simulação | Endereço compartilhável do Wokwi |
| Documentação | README e documentos técnicos em `docs/EN/` e `docs/PT/` |
| Licença | `LICENSE`, CC0 1.0 Universal |

## 14. Plano de validação

### 14.1 Teste isolado de um LED piscante

Critérios:

- monitor serial indica alternância entre 0 e 1;
- LED acende e apaga a cada aproximadamente 500 ms;
- ligação GPIO26 → resistor → ânodo → cátodo → GND.

Atraso bloqueante pode ser usado somente neste teste temporário, pois o objetivo
é isolar o hardware. Ver `tests/01_blue_led_basic.py` a
`tests/03_blue_led_asyncio.py` para a progressão completa até o idioma
`asyncio` usado em `main.py`.

### 14.2 Teste isolado de um OLED

Critérios:

- `i2c.scan()` detecta o endereço `0x3C` no barramento correspondente;
- todos os pixels acendem e apagam;
- padrões quadriculados complementares são exibidos;
- linhas horizontais e verticais percorrem toda a tela;
- pixels, linhas, retângulos e texto são renderizados;
- inversão, contraste e controle de energia respondem.

Ver `tests/05_cpu_oled_basic.py` / `tests/06_cpu_oled_full_diagnostic.py`
(primeiro OLED, `I2C(0)`) e `tests/11_ram_oled_basic.py` (segundo OLED,
`I2C(1)`, testado isoladamente -- não prova operação simultânea dos dois
barramentos, ver 14.6).

### 14.3 Teste do botão e do LED verde

Critérios:

- botão solto: GPIO17 LOW e LED verde apagado;
- botão pressionado: GPIO17 HIGH e LED verde aceso;
- manter o botão pressionado não produz múltiplas transições;
- oscilações de contato não causam cintilação perceptível.

### 14.4 Teste integrado

Critérios:

- os seis LEDs piscantes continuam alternando em todos os estados do
  botão, sem travar nem serem travados por outra tarefa além da latência
  de escrita documentada em 14.6/§17.2;
- o LED verde acompanha o botão, e a transição é registrada via
  `console_log()` (verde) tanto na TFT quanto no serial;
- os dois gráficos OLED continuam sendo redesenhados a cada janela de
  amostragem (§9), independentemente do estado do botão;
- não há exceções no monitor serial.

### 14.5 Limites de intervalo dos botões de velocidade

Critérios:

- pressionar repetidamente o botão de diminuir intervalo (GPIO~34) faz o
  intervalo dos LEDs piscantes parar de encolher ao atingir 125~ms
  (`BLINK_SPEED_STEP_MIN`);
- pressionar repetidamente o botão de aumentar intervalo (GPIO~35) faz o
  intervalo parar de crescer ao atingir 4~s (`BLINK_SPEED_STEP_MAX`);
- a linha serial de `print_status()` confirma o valor travado em ambos os
  extremos.

**Executado e aprovado em 18/08/2026 no Wokwi web.** O autor do projeto
confirmou os dois limites de intervalo e os valores correspondentes no
console serial, conforme os critérios acima.

### 14.6 Operação simultânea dos três mostradores

Critérios:

- os dois gráficos OLED continuam atualizando em seus barramentos I2C
  independentes enquanto o console da TFT também está ativo;
- nenhuma escrita em um mostrador trava visivelmente os demais por mais
  tempo do que uma única chamada de desenho/transferência instrumentada
  (§17.2);
- nenhum dos três mostradores para de atualizar silenciosamente enquanto
  os outros continuam.

**Executado e aprovado em 18/08/2026 no Wokwi web.** O autor do projeto
confirmou que os três mostradores permaneceram operando conforme o esperado.

### 14.7 Caminho de falha da TFT

Critérios:

- ao remover a fiação SPI (ou o GND) da TFT em `diagram.json` e rodar a
  simulação, não há garantia de falha detectada -- `tft_display` pode
  continuar sendo um objeto válido mesmo sem painel algum respondendo,
  pois o barramento SPI é somente de escrita (ver §17.4);
- em compensação, toda linha passada a `console_log()` continua sendo
  impressa no console serial, então nenhum evento é perdido mesmo que a
  própria TFT nunca mostre nada.

**Executado e aprovado em 18/08/2026 no Wokwi web.** O autor do projeto
confirmou o comportamento esperado do SPI somente de escrita e a preservação
de todas as mensagens no console serial.

### 14.8 Dessincronização de longa duração e latência do botão

Critérios:

- com `main.py` rodando continuamente por pelo menos 10-15 minutos, os
  seis LEDs piscantes -- nominalmente com o mesmo intervalo -- se
  dessincronizam visivelmente entre si ao longo da janela (ver a
  explicação de dessincronização em §4);
- ocasionalmente, uma pressão do botão principal precisa ser mantida por
  mais tempo que o nominal para ser registrada, sobretudo durante
  períodos de escrita intensa nos mostradores.

**Executado e aprovado em 18/08/2026 no Wokwi web.** O autor do projeto
confirmou a defasagem gradual dos LEDs e a latência do botão previstas nos
critérios acima.

## 15. Limitações e implementação física

A simulação valida lógica, pinagem e comportamento, mas não substitui todas as
verificações de hardware real.

Em uma montagem física devem ser considerados:

- tolerâncias dos resistores;
- corrente dos LEDs;
- qualidade da alimentação;
- resistores de elevação do barramento I2C presentes ou ausentes no módulo;
- comprimento e ruído dos fios;
- disponibilidade real de GPIO16 e GPIO17 no módulo instalado;
- comportamento de inicialização do GPIO2;
- diferenças entre clones de placas ESP32.

## 16. Registro de decisões técnicas

| Decisão | Registro |
|---|---|
| Plataforma | Wokwi adotado; Tinkercad descartado para este entregável |
| Placa | `board-esp32-devkit-c-v4` |
| Módulo físico recomendado | ESP32-WROOM-32E |
| Arquitetura | Apenas `asyncio`; sem superlaço temporizado como arquitetura principal |
| Atrasos | `await asyncio.sleep_ms()` no programa entregue |
| Temporizador de hardware | Não necessário |
| Botão | GPIO17, ativo em HIGH, `Pin.PULL_DOWN` |
| Antirrepique | Software, aproximadamente 30 ms; sem filtro RC |
| LED vermelho | GPIO26 (realocado do GPIO2 originalmente fixo — ver linha abaixo), alternância a cada 500 ms |
| LED verde | GPIO4, acompanha o estado estável do botão |
| OLED | SSD1306 128 × 64, endereço `0x3C` |
| Barramento do OLED | `machine.I2C` (hardware); diagnósticos atuais em `tests/05_cpu_oled_basic.py` e `tests/06_cpu_oled_full_diagnostic.py`, aprovados no Wokwi web em 18/08/2026 |
| Mapeamento OLED | GPIO32 = SCL (realocado do GPIO25 originalmente fixo); GPIO16 = SDA |
| `RED_LED_PIN` → GPIO26, `OLED_SCL_PIN` → GPIO32 | Realocados a pedido explícito do usuário, por layout da placa, à medida que o circuito cresceu. GPIO2 passou a acionar o `scheduler_idle_led`; GPIO25 passou a acionar o `white_led` (§17) |
| *(Substituída -- ver linha "Gráficos de uso de recursos" abaixo)* Atualização OLED | Decisão original: somente na inicialização e nas transições estáveis do botão. Não é mais como nenhum dos dois OLEDs se comporta (§9) |
| Versão do firmware no `diagram.json` | Não fixar `attrs.env`; usar a versão padrão/atual do Wokwi |
| Licença | CC0 1.0 Universal |
| Idioma do código | Inglês |
| Mensagens do OLED | Português, exatamente `Boa sorte!` e `Consegui` (substituídas pelos gráficos do §17 nos dois OLEDs) |
| Gráficos de uso de recursos nos dois OLEDs | Extensão pedida pelo usuário (§17.2). O valor de "CPU" é tempo real medido dentro das chamadas instrumentadas de desenho/transferência dos mostradores (desenho mais transferência I2C/SPI, não só o barramento), um substituto parcial e aproximado mantido porque o MicroPython no ESP32 bare-metal não expõe métrica de carga do escalonador do SO — ver §17.2 para o que ele cobre e o que não cobre |
| LEDs azuis com mesmo intervalo, seis tarefas separadas | Extensão pedida pelo usuário (§17.3). Cada LED continua sendo uma task `asyncio` independente, mesmo com todos no mesmo intervalo de 500 ms |

## 17. Notas de implementação

Esta seção detalha a implementação dos requisitos do §4, além do que cabe
em uma entrada RF individual. A tabela do §16 traz a versão resumida de
cada decisão abaixo.

### 17.1 Dois barramentos I2C independentes para os OLEDs

O primeiro OLED (`oled-display` / `oled_display`) roda em
`machine.I2C(0)`, GPIO32 (SCL) / GPIO16 (SDA). O segundo
(`oled-display-2` / `oled_display_2`) roda em seu próprio barramento I2C
de hardware, independente: `machine.I2C(1)`, GPIO15 (SCL) / GPIO22 (SDA)
— não um segundo endereço no primeiro barramento. Os dois são endereçados
ao mesmo tempo, sem disputa de barramento.

### 17.2 O que os dois gráficos OLED plotam

Os dois OLEDs são gráficos de barras rolantes, no estilo do Gerenciador de
Tarefas do Windows, uma amostra por coluna de pixel horizontal (até 128
amostras de histórico), redesenhados a cada janela de amostragem:

- **Primeiro OLED — rotulado "CPU".** O MicroPython no ESP32 puro não expõe
  nenhuma métrica de carga de escalonador em nível de sistema operacional,
  então o valor plotado é um substituto parcial e aproximado, não uma
  métrica completa de utilização de CPU: a fração de cada janela de
  amostragem de no mínimo 250 ms (um piso, não um período exato — ver o
  próprio comentário de temporização de `update_cpu_graph()`) gasta dentro
  das chamadas síncronas instrumentadas dos três mostradores, cronometradas
  por inteiro entre `_bus_busy_begin()` / `_bus_busy_end()`. Esse intervalo
  cobre tanto o trabalho de *framebuffer*/desenho em Python (o laço de até
  128 colunas em `draw_usage_graph()`, a conversão de glifo para pixels em
  `ili9341.py`) quanto a transferência I2C/SPI em si — não é uma medição
  pura de barramento. Também não cobre toda fonte de uso de CPU da
  aplicação: amostragem/antirrepique dos botões, a contabilidade de
  `scheduler_idle_task()`, a formatação de `print_status()` e o restante
  do código Python também consomem CPU fora dessa janela. O rótulo `CPU`
  foi mantido (em vez de renomeado para algo como `DISPLAY`) por já estar
  consolidado na linha de status serial, no esquema de cores do console da
  TFT e nesta documentação, e por caber na tela pequena do OLED — ver a
  docstring de `update_cpu_graph()` em `main.py` para a ressalva completa.
- **Segundo OLED — rotulado "RAM".** Um valor real e medido, não simulado,
  mas restrito às estatísticas de heap do coletor de lixo do MicroPython
  (`gc.mem_alloc()` / `gc.mem_free()`), amostradas a cada no mínimo 250 ms
  — não à RAM física total do ESP32. A pilha de execução, alocações
  nativas/C internas ao firmware e qualquer memória fora do heap gerenciado
  pelo coletor de lixo não estão incluídas. Ver `update_ram_graph()`.

O estado do botão é registrado via `console_log()` (§17.4), não uma
mensagem de texto em qualquer OLED, já que nenhum dos dois tem espaço
sobrando para um gráfico e uma mensagem de texto legível ao mesmo tempo
num painel monocromático de 128×64.

### 17.3 Seis LEDs, um intervalo compartilhado, seis tarefas independentes

Os seis LEDs (vermelho, azul, amarelo, branco, laranja e um segundo
vermelho) são todos pintados da mesma cor
na placa (`#0000FF`), mesmo que o `main.py` continue rastreando cada um
individualmente (ver `BLINKING_LEDS`). Cada um roda como sua própria task
`asyncio` independente (`blink_led()`) -- mais um LED sempre significa
mais uma task concorrente, nunca mais lógica adicionada a um laço
compartilhado.

### 17.4 Console de registro na TFT, SPI somente de escrita, e a decisão de espelhar no serial

A TFT ILI9341 usa SPI genuíno de 4 fios (SCK, MOSI, CS, D/C, mais uma
linha de reinicialização — GPIO~18/23/5/21/19). Diferentemente dos
gráficos dos dois OLEDs, a TFT
(`tft_display`, controlada por `ili9341.py`) funciona como um registro de
atividade colorido e rolante: `console_log()` escreve uma linha por
evento do sistema, uma cor por subsistema, voltando ao topo da tela ao
preenchê-la por completo (sem rolagem real).

Esse barramento SPI é somente de escrita: não tem linha MISO, e
`ili9341.py` nunca lê nada de volta do painel (sem consulta de
identificação, sem leitura de status). Por isso, `create_tft_display()`
só retorna `None` quando a própria construção do objeto `ILI9341` levanta
`OSError` — uma falha de driver/periférico, não uma detecção geral de
"TFT ausente". Um painel fisicamente desconectado, porém eletricamente
silencioso, muito provavelmente não levanta erro algum, deixando
`tft_display` como um objeto válido sem nenhuma tela real respondendo no
barramento.

Como essa detecção não é confiável, `console_log()` não condiciona seu
retorno ao serial a `tft_display is None`: toda linha é impressa no
console serial incondicionalmente, além de escrita na TFT quando esta
está presente. É o único mecanismo que de fato cobre um painel
fisicamente ausente porém eletricamente silencioso, que uma verificação
`is None` sozinha não cobre.

A renderização de texto de `console_log()` (`text()` em `ili9341.py`)
também passou por uma otimização de desempenho: a implementação inicial
convertia cada glifo em pixels individuais via
`framebuf.FrameBuffer.pixel()`, até ~1920 chamadas por linha de texto. A
versão atual pré-calcula, uma vez por combinação de cor de texto/fundo,
uma tabela de 256 entradas de byte para os 16 bytes RGB565 correspondentes
a essa fatia de 8 pixels do glifo, reutilizada a cada caractere
renderizado.
