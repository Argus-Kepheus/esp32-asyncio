<!-- doc-id: technical-specification -->
<!-- language: PT -->
<!-- content-revision: 4 -->

# Especificação técnica — esp32-asyncio

<!-- section: document-control -->
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

<!-- section: objective -->
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

<!-- section: simulation-platform -->
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

<!-- section: functional-requirements -->
## 4. Requisitos funcionais

### RF-01 — Seis LEDs piscantes

- identificadores no Wokwi: `blue-led-1` a `blue-led-6`;
- variáveis em Python: `blue_led_1` a `blue_led_6`;
- o mapeamento canônico de GPIOs/conectores está na tabela gerada de
  `hardware-reference.md`, §3;
- todos fisicamente azuis (`#0000FF`) em `diagram.json`, com a mesma numeração
  de 1 a 6 usada de forma consistente no circuito e no código Python;
- cada um em sua própria tarefa `asyncio` independente (`blink_led()`,
  a partir da lista `BLINKING_LEDS`);
- alternância no intervalo-base compartilhado definido em
  `config/runtime.json`, ajustável conforme RF-03;
- logicamente independentes entre si -- nenhum chama ou espera outro --,
  embora todos compartilhem o mesmo escalonador cooperativo (nota de
  engenharia da §5.3).

### RF-02 — Botão pulsador e LED verde

- Identificadores no Wokwi: `push-button`, `green-led`;
- variáveis em Python: `push_button`, `green_led`;
- a ligação atual é definida em `config/hardware.json` e exibida em
  `hardware-reference.md`, §3;
- botão: normalmente aberto e momentâneo, `Pin.IN` com `Pin.PULL_DOWN`
  interno; solto = LOW, pressionado = HIGH;
- LED verde: botão solto → apagado, botão pressionado → aceso;
- cada transição estável é registrada via `console_log()`, em verde
  (RF-05).

### RF-03 — Botões de velocidade

- Identificadores no Wokwi: `decrease-speed-button`,
  `increase-speed-button`;
- variáveis em Python: `decrease_speed_button`, `increase_speed_button`;
- GPIOs e configuração de pull são canônicos em `config/hardware.json` e
  exibidos em `hardware-reference.md`, §3;
- cada pressão escala o intervalo de todos os LEDs piscantes pelo passo de
  potência de dois configurado, sujeito aos limites de `config/runtime.json`.

### RF-04 — Dois gráficos de uso de recursos nos OLEDs

- Identificadores no Wokwi: `oled0-display`, `oled1-display`;
- variáveis em Python: `oled0_display`, `oled1_display`;
- ambos usam controladores SSD1306 em barramentos I2C de hardware
  independentes; endereços, IDs de barramento e pinos atuais são canônicos em
  `config/hardware.json` e exibidos em `hardware-reference.md`, §3;
- o OLED0 plota o gráfico aproximado de "CPU" e o OLED1 plota o gráfico de
  "RAM" (§17.2);
- a cadência de amostragem é definida em `config/runtime.json`; o atraso
  configurado é um piso, não um período exato (§9).

### RF-05 — Console de registro na TFT

- Identificador no Wokwi: `tft-display`;
- variável em Python: `tft_display`;
- controlador: ILI9341 em SPI de 4 fios; o ID do barramento e o mapeamento
  atual de sinais são canônicos em `config/hardware.json` e exibidos em
  `hardware-reference.md`, §3;
- `console_log()` escreve uma linha colorida por evento do sistema (uma
  cor por subsistema), voltando ao topo da tela ao preenchê-la, e sempre
  espelha cada linha no console serial também, independente da presença
  da TFT (§17.4).

### RF-06 — LEDs indicadores de estado

- Identificadores no Wokwi: `bus-idle-led`, `scheduler-idle-led`;
- variáveis em Python: `bus_idle_led`, `scheduler_idle_led`;
- a ligação atual é definida em `config/hardware.json` e exibida em
  `hardware-reference.md`, §3;
- laranja (`bus_idle_led`): aceso por padrão, apaga apenas durante uma
  escrita instrumentada em algum mostrador -- leitura invertida de
  "barramento ocupado";
- amarelo (`scheduler_idle_led`): alterna a cada iteração de
  `scheduler_idle_task()` -- uma visualização grosseira de vazão do
  escalonador, não um sinal literal de ociosidade/prioridade (§17).

<!-- section: software-architecture -->

### RF-07 — Entregáveis

- `main.py` completo e executável, com os controladores `ssd1306.py` e `ili9341.py` de que depende;
- circuito Wokwi em `diagram.json`;
- configuração local do Wokwi em `wokwi.toml`;
- README e documentação técnica multilíngue;
- endereço público do repositório GitHub; e
- endereço compartilhável da simulação no Wokwi.

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

<!-- section: electrical-design -->
## 6. Projeto do circuito

### 6.1 LEDs e resistores

Todos os LEDs exigem limitação de corrente e GND comum. Os valores atuais dos
resistores, GPIOs e restrições de pinos são canônicos em
`config/hardware.json` e apresentados nas tabelas geradas de
`hardware-reference.md`. A topologia conceitual é saída ESP32 → resistor
limitador → LED → GND; os detalhes concretos não são duplicados aqui.

### Resumo dos parâmetros de execução

<!-- BEGIN GENERATED: runtime-summary -->
| Parâmetro de execução | Valor configurado |
|---|---:|
| Intervalo-base dos LEDs piscantes | 500 ms |
| Faixa de passos da velocidade | -2 … 3 |
| Intervalo de amostragem dos botões | 5 ms |
| Janela estável de antirrepique | 30 ms |
| Piso de amostragem do gráfico de CPU | 250 ms |
| Piso de amostragem do gráfico de RAM | 250 ms |
| Intervalo do status serial | 1000 ms |
| Throttling do registro no console | 4 |
<!-- END GENERATED: runtime-summary -->

<!-- section: debounce-strategy -->
### 6.2 Botão, resistor interno e antirrepique

A ligação e a configuração de pull do botão principal são canônicas em
`config/hardware.json` e exibidas em `hardware-reference.md`, §3. A entrada
usa `Pin.PULL_DOWN`: contato aberto resulta em LOW e contato fechado em HIGH.

O antirrepique é realizado por software, de maneira não bloqueante:

- amostragem no intervalo `BUTTON_SAMPLE_INTERVAL_MS`;
- identificação de um estado candidato;
- aceitação somente após a janela `BUTTON_DEBOUNCE_MS` estável;
- geração de uma única transição lógica por acionamento.

Os valores atuais desses parâmetros são gerados de `config/runtime.json` na
tabela de runtime acima.

Os nomes dos terminais do botão em `diagram.json` devem respeitar exatamente:

```text
1.l, 1.r, 2.l, 2.r
```

### 6.3 Por que I2C nos dois OLEDs, e SPI na TFT

Os dois OLEDs usam barramentos `machine.I2C` de hardware independentes. O
mapeamento atual de barramentos, GPIOs e frequência é canônico em
`config/hardware.json` e apresentado na tabela gerada de
`hardware-reference.md`, §3.

Uma revisão anterior utilizava `machine.SoftI2C` de forma defensiva, sem
confirmação de que fosse necessário. Os diagnósticos vigentes,
`tests/05_cpu_oled_basic.py` e `tests/06_cpu_oled_full_diagnostic.py`,
foram aprovados no Wokwi web em 18/08/2026; consulte a §16.

Os dois displays também necessitam de VCC e GND. Esses terminais são conexões
de alimentação, e não sinais de comunicação.

I2C foi mantido para os dois OLEDs porque:

- usa apenas dois sinais por barramento, mantendo baixo o total de pinos
  mesmo com dois displays;
- o componente `board-ssd1306` do Wokwi utiliza a variante I2C;
- o conteúdo de cada um -- um gráfico de barras redesenhado periodicamente
  -- não precisa da maior taxa de transferência do SPI na cadência de
  atualização configurada (§9).

O console da TFT (RF-05) é um caso à parte: usa SPI genuíno de 4 fios (SCK,
MOSI, CS, D/C, mais RST), porque o controlador ILI9341 usado aqui é uma
peça SPI e porque o quadro colorido maior (240×320) da tela se beneficia da
maior taxa de transferência do SPI. São duas decisões independentes para
dois displays diferentes, não uma única restrição de projeto.

<!-- section: revision-guidance -->
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

<!-- section: naming-conventions -->
## 8. Convenções de nomes

### 8.1 Identificadores no Wokwi

```text
blue-led-1
green-led
push-button
oled0-display
```

### 8.2 Variáveis em Python

```python
blue_led_1
green_led
push_button
oled0_display
```

### 8.3 Constantes em Python

```python
BLUE_LED_1_PIN
GREEN_LED_PIN
BUTTON_PIN
OLED0_SDA_PIN
OLED0_SCL_PIN
```

Identificadores Python não podem conter hífen; por isso, usam sublinhado.

<!-- section: oled-update-strategy -->
## 9. Estratégia de atualização dos gráficos OLED

Os dois OLEDs redesenham em janelas de amostragem fixas --
`CPU_GRAPH_SAMPLE_INTERVAL_MS` / `RAM_GRAPH_SAMPLE_INTERVAL_MS` -- cujos
valores atuais são gerados de `config/runtime.json` acima, e não em um evento
de mudança de estado do botão ou similar:

- `update_cpu_graph()` e `update_ram_graph()` rodam cada um seu próprio
  laço `while True`, redesenhando a cada iteração e então aguardando o intervalo de amostragem configurado correspondente;
- `asyncio.sleep_ms()` garante apenas um atraso mínimo, então a janela de
  amostragem é medida com `time.ticks_us()`, não assumida como exata --
  uma iteração mais lenta (por exemplo, uma escrita concorrente de
  `console_log()`) empurra o intervalo real além do piso configurado, e
  `update_cpu_graph()` leva isso em conta explicitamente ao calcular sua
  porcentagem (§17.2);
- cada redesenho faz um `fill()` completo e replota todo o histórico
  rolante, não só a coluna mais nova, ainda que `framebuf` tenha sim uma
  primitiva para deslocar pixels existentes para a esquerda (`scroll()`,
  exposta por `ssd1306.py` e exercitada por
  `tests/06_cpu_oled_full_diagnostic.py`) -- o redesenho do zero foi
  mantido pelo motivo abaixo, não por essa primitiva estar indisponível.

Isto é redesenho periódico incondicional, não uma atualização orientada por
eventos: os dois OLEDs são, eles próprios, parte do que mantém o
processador ocupado (a medição de "CPU" do §17.2), então redesenhar
continuamente é intencional aqui, não algo a minimizar.

<!-- section: repository-contents -->
<!-- section: state-model -->
## Modelo de estados

O estado estável do botão principal determina diretamente o LED verde:

| Estado estável | GPIO 17 | LED verde | Registro no console |
|---|---:|---|---|
| Solto | LOW | apagado | `Button released -> Green LED OFF` |
| Pressionado | HIGH | aceso | `Button pressed -> Green LED ON` |

As tarefas dos seis LEDs piscantes, dos dois gráficos OLED e do console TFT são ortogonais a esse estado: não são pausadas nem reiniciadas por uma transição do botão.

<!-- section: startup-failure -->
## Comportamento de inicialização e falhas

Antes de `main()` iniciar o laço assíncrono, a aplicação configura as saídas, entradas e barramentos; verifica os dois OLEDs pelo endereço canônico configurado; e tenta criar o objeto da TFT. A ausência de um OLED detectável mantém esse display indisponível sem impedir a inicialização dos demais subsistemas.

A TFT usa SPI somente de escrita. Por isso, uma tela fisicamente ausente pode não produzir erro detectável; `console_log()` espelha incondicionalmente todas as mensagens no serial para que os eventos não sejam perdidos nesse caso. As limitações e caminhos de falha detalhados permanecem documentados nas notas de implementação e no plano de validação.

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

<!-- section: workflow -->
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
- `mpremote` envia `main.py`, `ssd1306.py` e `ili9341.py` ao sistema de arquivos simulado;
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

<!-- section: verification-plan -->
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

- `oled0_i2c.scan()` ou `oled1_i2c.scan()` detecta o endereço canônico configurado no barramento correspondente;
- todos os pixels acendem e apagam;
- padrões quadriculados complementares são exibidos;
- linhas horizontais e verticais percorrem toda a tela;
- pixels, linhas, retângulos e texto são renderizados;
- inversão, contraste e controle de energia respondem.

Ver `tests/05_cpu_oled_basic.py` / `tests/06_cpu_oled_full_diagnostic.py`
(OLED0 de CPU, `I2C(0)`) e `tests/11_ram_oled_basic.py` (OLED1 de RAM,
`I2C(1)`, testado isoladamente -- não prova operação simultânea dos dois
barramentos, ver 14.6).

### 14.3 Teste do botão e do LED verde

Critérios:

- botão solto: entrada LOW e LED verde apagado;
- botão pressionado: entrada HIGH e LED verde aceso;
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

<!-- section: future-work -->
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

<!-- section: decision-log -->
<!-- section: acceptance-criteria -->
## Critérios de aceitação

O projeto é considerado coerente com esta especificação quando:

- a pinagem e os componentes correspondem à configuração canônica em `config/hardware.json`;
- `main.py` inicia sem erro no ambiente MicroPython/Wokwi previsto;
- os seis LEDs azuis piscam com intervalo compartilhado ajustável, mantendo tarefas independentes;
- o LED verde acompanha o estado estável do botão principal;
- os dois botões de velocidade respeitam os limites configurados;
- os dois OLEDs e o console TFT permanecem operacionais conforme suas limitações documentadas;
- o console serial preserva os registros mesmo quando a TFT não fornece confirmação de presença; e
- a documentação EN/PT satisfaz o contrato de paridade de `docs/metadata.json`.

Como trabalho futuro, uma montagem física deve manter o antirrepique de software para botões mecânicos (com filtro RC opcional) e pode reavaliar I2C versus SPI caso existam GPIOs disponíveis e uma taxa de atualização maior se torne requisito.

## 16. Registro de decisões técnicas

| Decisão | Registro |
|---|---|
| Plataforma | Wokwi adotado; Tinkercad descartado para este entregável |
| Placa | `board-esp32-devkit-c-v4` |
| Módulo físico recomendado | ESP32-WROOM-32E |
| Arquitetura | Apenas `asyncio`; sem superlaço temporizado como arquitetura principal |
| Atrasos | `await asyncio.sleep_ms()` no programa entregue |
| Temporizador de hardware | Não necessário |
| Botão | Ligação/pull definidos em `config/hardware.json`; ativo em HIGH com `Pin.PULL_DOWN` |
| Antirrepique | Software; intervalos definidos em `config/runtime.json`; sem filtro RC |
| LEDs azuis piscantes | Identificadores numerados de 1 a 6; GPIOs em `config/hardware.json` e intervalo-base em `config/runtime.json` |
| LED verde | Ligação em `config/hardware.json`; acompanha o estado estável do botão |
| OLED | SSD1306; dimensões/endereço atuais em `config/hardware.json` |
| Barramento do OLED | `machine.I2C` (hardware); diagnósticos atuais em `tests/05_cpu_oled_basic.py` e `tests/06_cpu_oled_full_diagnostic.py`, aprovados no Wokwi web em 18/08/2026 |
| Mapeamento OLED | Ver tabela gerada em `hardware-reference.md`, §3 |
| Identificadores dos seis LEDs azuis | `blue_led_1` a `blue_led_6` no Python, `BLUE_LED_1_PIN` a `BLUE_LED_6_PIN` nas constantes e `blue-led-1` a `blue-led-6` no Wokwi |
| *(Substituída -- ver linha "Gráficos de uso de recursos" abaixo)* Atualização OLED | Decisão original: somente na inicialização e nas transições estáveis do botão. Não é mais como nenhum dos dois OLEDs se comporta (§9) |
| Versão do firmware no `diagram.json` | Não fixar `attrs.env`; usar a versão padrão/atual do Wokwi |
| Licença | CC0 1.0 Universal |
| Idioma do código | Inglês |
| Mensagens do OLED | Português, exatamente `Boa sorte!` e `Consegui` (substituídas pelos gráficos do §17 nos dois OLEDs) |
| Gráficos de uso de recursos nos dois OLEDs | Extensão pedida pelo usuário (§17.2). O valor de "CPU" é tempo real medido dentro das chamadas instrumentadas de desenho/transferência dos mostradores (desenho mais transferência I2C/SPI, não só o barramento), um substituto parcial e aproximado mantido porque o MicroPython no ESP32 bare-metal não expõe métrica de carga do escalonador do SO — ver §17.2 para o que ele cobre e o que não cobre |
| LEDs azuis com mesmo intervalo, seis tarefas separadas | Extensão pedida pelo usuário (§17.3). Cada LED continua sendo uma task `asyncio` independente, mesmo com todos no mesmo intervalo de 500 ms |

<!-- section: implementation-notes -->
## 17. Notas de implementação

Esta seção detalha a implementação dos requisitos do §4, além do que cabe
em uma entrada RF individual. A tabela do §16 traz a versão resumida de
cada decisão abaixo.

### 17.1 Dois barramentos I2C independentes para os OLEDs

O OLED0 de CPU (`oled0-display` / `oled0_display`) e o OLED1 de RAM
(`oled1-display` / `oled1_display`) usam barramentos I2C de hardware
separados, e não dois endereços no mesmo barramento. IDs de barramento,
GPIOs e endereços atuais são canônicos em `config/hardware.json` e
apresentados em `hardware-reference.md`, §3.

### 17.2 O que os dois gráficos OLED plotam

Os dois OLEDs são gráficos de barras rolantes, no estilo do Gerenciador de
Tarefas do Windows, uma amostra por coluna de pixel horizontal (até 128
amostras de histórico), redesenhados a cada janela de amostragem:

- **OLED0 — rotulado "CPU".** O MicroPython no ESP32 puro não expõe
  nenhuma métrica de carga de escalonador em nível de sistema operacional,
  então o valor plotado é um substituto parcial e aproximado, não uma
  métrica completa de utilização de CPU: a fração de cada janela de
  janela de amostragem configurada (um piso, não um período exato — ver o
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
- **OLED1 — rotulado "RAM".** Um valor real e medido, não simulado,
  mas restrito às estatísticas de heap do coletor de lixo do MicroPython
  (`gc.mem_alloc()` / `gc.mem_free()`), amostradas na janela configurada
  — não à RAM física total do ESP32. A pilha de execução, alocações
  nativas/C internas ao firmware e qualquer memória fora do heap gerenciado
  pelo coletor de lixo não estão incluídas. Ver `update_ram_graph()`.

O estado do botão é registrado via `console_log()` (§17.4), não uma
mensagem de texto em qualquer OLED, já que nenhum dos dois tem espaço
sobrando para um gráfico e uma mensagem de texto legível ao mesmo tempo
num painel monocromático de 128×64.

### 17.3 Seis LEDs, um intervalo compartilhado, seis tarefas independentes

Os seis LEDs piscantes são azuis no circuito atual (`#0000FF`) e o
`main.py` continua rastreando cada um individualmente (ver `BLINKING_LEDS`). Cada um roda como sua própria task
`asyncio` independente (`blink_led()`) -- mais um LED sempre significa
mais uma task concorrente, nunca mais lógica adicionada a um laço
compartilhado.

### 17.4 Console de registro na TFT, SPI somente de escrita, e a decisão de espelhar no serial

A TFT ILI9341 usa SPI genuíno de 4 fios (SCK, MOSI, CS, D/C, mais reset);
o mapeamento concreto é gerado a partir de `config/hardware.json` em
`hardware-reference.md`, §3. Diferentemente dos
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
