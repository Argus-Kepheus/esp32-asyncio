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

1. o piscar contínuo de um LED vermelho em intervalo fixo;
2. a leitura de um botão pulsador normalmente aberto e ativo em nível alto;
3. o controle de um LED verde segundo o estado do botão;
4. a alteração dinâmica de uma mensagem em OLED SSD1306 segundo o mesmo
   estado.

Os entregáveis obrigatórios são:

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

### RF-01 — LED vermelho

- Identificador no Wokwi: `red-led`;
- variável em Python: `red_led`;
- constante: `RED_LED_PIN`;
- GPIO: 26 (realocado do GPIO 2, originalmente fixo, a pedido explícito do
  usuário, por layout da placa — ver §16, registro de decisões);
- estado alternado a cada 500 ms;
- funcionamento contínuo;
- independente do botão, do LED verde e do OLED;
- implementação não bloqueante.

Interpretação temporal:

- ligado por aproximadamente 500 ms;
- desligado por aproximadamente 500 ms;
- período completo aproximado de 1 s.

### RF-02 — LED verde

- Identificador no Wokwi: `green-led`;
- variável em Python: `green_led`;
- constante: `GREEN_LED_PIN`;
- GPIO: 4;
- botão solto: LED apagado;
- botão pressionado: LED aceso.

### RF-03 — Botão pulsador

- Identificador no Wokwi: `push-button`;
- variável em Python: `push_button`;
- constante: `BUTTON_PIN`;
- GPIO: 17;
- tipo: normalmente aberto e momentâneo;
- botão solto: nível lógico baixo;
- botão pressionado: nível lógico alto;
- entrada configurada com `Pin.PULL_DOWN`;
- tratamento de antirrepique por software;
- ausência de filtro RC externo.

### RF-04 — Display OLED

- Identificador no Wokwi: `oled-display`;
- variável em Python: `oled_display`;
- controlador: SSD1306;
- resolução: 128 × 64 pixels;
- interface: I2C;
- endereço: `0x3C`;
- GPIO32: SCL (realocado do GPIO 25, originalmente fixo, a pedido
  explícito do usuário, por layout da placa — ver §16, registro de
  decisões);
- GPIO16: SDA;
- botão solto: exibir exatamente `Boa sorte!`;
- botão pressionado: exibir exatamente `Consegui`;
- atualizar a memória de quadro somente quando o estado estável do botão
  mudar.

### RF-05 — Coerência das saídas

| Estado estável do botão | GPIO17 | LED verde | OLED |
|---|---:|---|---|
| Solto | LOW | Apagado | `Boa sorte!` |
| Pressionado | HIGH | Aceso | `Consegui` |

O LED vermelho permanece piscando nos dois estados.

## 5. Arquitetura de software

### 5.1 Arquitetura assíncrona

O projeto utiliza exclusivamente `asyncio` do MicroPython. Cada comportamento
independente é organizado em uma corrotina cooperativa, por exemplo:

- tarefa de piscar o LED vermelho;
- tarefa de amostragem e antirrepique do botão;
- aplicação do estado estável ao LED verde e ao OLED.

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
- melhor tolerância a latências introduzidas por operações I2C do OLED.

A programação continua sendo cooperativa: uma função síncrona excessivamente
demorada ainda pode atrasar as outras tarefas. Por isso, a atualização do OLED
é reduzida ao mínimo necessário.

### 5.4 Temporizadores de hardware

Temporizadores de hardware não são necessários para o requisito de 500 ms. A
tolerância temporal da aplicação é compatível com `asyncio`, e a adoção de
interrupções ou funções de retorno de temporizador acrescentaria complexidade
sem benefício funcional relevante.

## 6. Projeto do circuito

### 6.1 LEDs e resistores

Cada LED possui resistor de 220 Ω em série.

```text
GPIO26 ── 220 Ω ── ânodo do LED vermelho
cátodo ── GND

GPIO4 ── 220 Ω ── ânodo do LED verde
cátodo ── GND
```

O LED vermelho foi realocado do GPIO2 (originalmente fixo) para o GPIO26 a
pedido explícito do usuário, por layout da placa — ver §16, registro de
decisões. O GPIO2, liberado por essa mudança, hoje aciona o
`scheduler_idle_led` (ver §17, funcionalidades estendidas); esse uso
continua aceitável porque o circuito externo (LED + resistor até o GND)
nunca impõe um nível inadequado durante a energização.

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

### 6.3 OLED, I2C e limitação predefinida dos pinos

O projeto determina previamente:

```text
GPIO32 = SCL
GPIO16 = SDA
```

Essa atribuição não foi escolhida por ser o mapeamento padrão do ESP32 nem por
um estudo de desempenho. Ela deve ser declarada explicitamente no código, no
circuito e na documentação. O SCL foi originalmente fixado no GPIO25 e
depois realocado para o GPIO32 a pedido explícito do usuário, por layout
da placa — ver §16, registro de decisões.

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
confirmação de que fosse necessário. A execução bem-sucedida de
`tests/05_oled_basic.py` e `tests/06_oled_full_diagnostic.py` no wokwi.com,
ambos com `machine.I2C` de hardware, confirmou que essa substituição era
desnecessária; consulte a §16.

O display também necessita de VCC e GND. Esses dois terminais são conexões de
alimentação, e não sinais de comunicação.

Alguns módulos SSD1306 físicos usam SPI, que pode exigir SCK, MOSI, CS, DC e
RST. SPI pode oferecer maior taxa de transferência, porém utiliza mais
terminais. Essa vantagem não é relevante neste projeto porque:

- o mapeamento I2C foi predefinido;
- o componente `board-ssd1306` do Wokwi utiliza I2C;
- as mensagens são curtas e estáticas;
- o display é atualizado somente nas transições do botão.

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

## 9. Estratégia de atualização dinâmica do OLED

O OLED não deve ser redesenhado continuamente.

A memória de quadro é enviada:

1. durante a inicialização;
2. quando o estado estável do botão muda.

Princípio lógico:

```python
if stable_button_state != previous_button_state:
    update_green_led(stable_button_state)
    update_oled_display(stable_button_state)
```

Benefícios:

- redução do tráfego I2C;
- menor ocupação do processador;
- menor latência introduzida pelas escritas no display;
- eliminação de redesenhos desnecessários;
- redução de cintilação;
- menor interferência nas demais tarefas.

## 10. Estrutura do repositório

```text
esp32-asyncio/
├── main.py
├── ssd1306.py
├── diagram.json
├── wokwi.toml
├── README.md
├── LICENSE
├── .gitignore
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
└── tests/
    └── README.md
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

O projeto no navegador deve conter `main.py`, `ssd1306.py` e `diagram.json`.
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
| Controlador do OLED | `ssd1306.py` |
| Circuito | `diagram.json` |
| Configuração local | `wokwi.toml` |
| Repositório | Endereço público do GitHub |
| Simulação | Endereço compartilhável do Wokwi |
| Documentação | README e documentos técnicos em `docs/EN/` e `docs/PT/` |
| Licença | `LICENSE`, CC0 1.0 Universal |

## 14. Plano de validação

### 14.1 Teste isolado do LED vermelho

Critérios:

- monitor serial indica alternância entre 0 e 1;
- LED acende e apaga a cada aproximadamente 500 ms;
- ligação GPIO26 → resistor → ânodo → cátodo → GND.

Atraso bloqueante pode ser usado somente neste teste temporário, pois o objetivo
é isolar o hardware.

### 14.2 Teste isolado do OLED

Critérios:

- `i2c.scan()` detecta o endereço `0x3C`;
- todos os pixels acendem e apagam;
- padrões quadriculados complementares são exibidos;
- linhas horizontais e verticais percorrem toda a tela;
- pixels, linhas, retângulos e texto são renderizados;
- inversão, contraste e controle de energia respondem.

### 14.3 Teste do botão e do LED verde

Critérios:

- botão solto: GPIO17 LOW e LED verde apagado;
- botão pressionado: GPIO17 HIGH e LED verde aceso;
- manter o botão pressionado não produz múltiplas transições;
- oscilações de contato não causam cintilação perceptível.

### 14.4 Teste integrado

Critérios:

- o LED vermelho continua piscando em todos os estados;
- o LED verde acompanha o botão;
- o OLED mostra a mensagem correta;
- a mudança ocorre após o estado estável;
- o OLED não é atualizado repetidamente enquanto o estado não muda;
- não há exceções no monitor serial.

Os três primeiros critérios sobre o OLED descrevem o comportamento
*original*; hoje ambos os OLEDs foram **substituídos** por gráficos de
uso de CPU/RAM ao vivo, não redesenhados só na mudança de estado do botão
(ver §17, funcionalidades estendidas).

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
| Barramento do OLED | `machine.I2C` (hardware); `SoftI2C` foi adotado defensivamente numa revisão anterior e revertido após confirmação em `tests/05_oled_basic.py` e `tests/06_oled_full_diagnostic.py` |
| Mapeamento OLED | GPIO32 = SCL (realocado do GPIO25 originalmente fixo); GPIO16 = SDA |
| `RED_LED_PIN` → GPIO26, `OLED_SCL_PIN` → GPIO32 | Realocados a pedido explícito do usuário, por layout da placa, à medida que o circuito cresceu. GPIO2 passou a acionar o `scheduler_idle_led`; GPIO25 passou a acionar o `white_led` (§17) |
| Atualização OLED | Somente na inicialização e nas transições estáveis |
| Versão do firmware no `diagram.json` | Não fixar `attrs.env`; usar a versão padrão/atual do Wokwi |
| Licença | CC0 1.0 Universal |
| Idioma do código | Inglês |
| Mensagens do OLED | Português, exatamente `Boa sorte!` e `Consegui` (substituídas pelos gráficos do §17 nos dois OLEDs) |
| Gráficos de uso de recursos nos dois OLEDs | Extensão pedida pelo usuário (§17.2). O valor de "CPU" é tempo real medido dentro das chamadas instrumentadas de desenho/transferência dos mostradores (desenho mais transferência I2C/SPI, não só o barramento), um substituto parcial e aproximado mantido porque o MicroPython no ESP32 bare-metal não expõe métrica de carga do escalonador do SO — ver §17.2 para o que ele cobre e o que não cobre |
| LEDs azuis com mesmo intervalo, seis tarefas separadas | Extensão pedida pelo usuário (§17.3). Cada LED continua sendo uma task `asyncio` independente, mesmo com todos no mesmo intervalo de 500 ms |

## 17. Funcionalidades estendidas (além do escopo original)

Esta seção documenta funcionalidades adicionadas, a pedido explícito do
usuário, depois que o entregável obrigatório original (§2–§14) já estava
completo e validado. Ela não substitui nem invalida os requisitos
funcionais das seções anteriores; a tabela do §16 traz a versão resumida
de cada decisão abaixo. O LED verde e o propósito original do OLED ainda
estão sendo revisados no momento desta escrita, então **não** foram
redocumentados aqui ainda — só o que já está definido foi registrado.

### 17.1 Segundo OLED, barramento I2C próprio

Um segundo display OLED SSD1306 (`oled-display-2` / `oled_display_2`)
roda em seu próprio barramento I2C de hardware, independente:
`machine.I2C(1)`, em GPIO15 (SCL) / GPIO22 (SDA) — separado do barramento
`I2C(0)` do primeiro OLED (GPIO32 SCL / GPIO16 SDA, conforme a
realocação de pinos registrada no §16). Os dois são endereçados ao mesmo
tempo, sem disputa de barramento.

### 17.2 Os dois OLEDs agora plotam gráficos de uso de recursos, ao vivo

O requisito original exigia que o (único) OLED mostrasse `Boa sorte!` /
`Consegui` conforme o estado do botão. Nenhum dos dois OLEDs faz mais
isso — ambos foram reaproveitados como gráficos de barras rolantes, no
estilo do Gerenciador de Tarefas do Windows, uma amostra por coluna de
pixel horizontal (até 128 amostras de histórico), redesenhados a cada
janela de amostragem:

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

O botão ainda liga/desliga o LED verde e imprime seu estado no monitor
serial (`apply_button_state()`) — só o retorno em texto no OLED foi
removido, já que nenhum dos dois OLEDs tem espaço sobrando para um
gráfico e uma mensagem de texto legível ao mesmo tempo num painel
monocromático de 128×64.

### 17.3 Seis LEDs, um intervalo compartilhado, seis tarefas independentes

Cinco LEDs adicionais (azul, amarelo, branco, laranja e um segundo
vermelho) se juntam ao LED vermelho original, todos pintados da mesma cor
na placa (`#0000FF`), mesmo que o `main.py` continue rastreando cada um
individualmente (ver `BLINKING_LEDS`). Cada um roda como sua própria task
`asyncio` independente (`blink_led()`) — o mesmo padrão já estabelecido
pelo LED vermelho original: mais um LED sempre significa mais uma task
concorrente, nunca mais lógica adicionada a um laço compartilhado.

Atualmente os seis piscam no mesmo intervalo-base de 500 ms — alternando
a cada 500 ms, ciclo completo de aproximadamente 1 s, igual à temporização
original do LED vermelho — funcionando como seis equipamentos idênticos e
independentes, em vez de seis frequências diferentes. Dois botões extras
(GPIO34 para diminuir, GPIO35 para aumentar — ambos com resistor de
pull-down físico externo, já que GPIO34/35 não têm pull-down interno)
escalam o intervalo de todos os LEDs pelo mesmo fator de potência de 2 ao
mesmo tempo, limitado entre 125 ms e 4 s, de forma que os seis sempre
fiquem sincronizados entre si.
