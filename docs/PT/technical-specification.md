# Especificação técnica — cess-uff

## 1. Controle do documento

| Campo | Valor |
|---|---|
| Projeto | Avaliação prática CESS-UFF com ESP32 e MicroPython |
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
- GPIO: 2;
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
- GPIO25: SCL;
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
GPIO2 ── 220 Ω ── ânodo do LED vermelho
cátodo ── GND

GPIO4 ── 220 Ω ── ânodo do LED verde
cátodo ── GND
```

O GPIO2 é um terminal de configuração de inicialização do ESP32. Seu uso é uma
exigência do projeto e é aceitável desde que o circuito externo não imponha
nível inadequado durante a energização.

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
GPIO25 = SCL
GPIO16 = SDA
```

Essa atribuição não foi escolhida por ser o mapeamento padrão do ESP32 nem por
um estudo de desempenho. Ela deve ser declarada explicitamente no código, no
circuito e na documentação.

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
cess-uff/
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
- ligação GPIO2 → resistor → ânodo → cátodo → GND.

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
| LED vermelho | GPIO2, alternância a cada 500 ms |
| LED verde | GPIO4, acompanha o estado estável do botão |
| OLED | SSD1306 128 × 64, endereço `0x3C` |
| Barramento do OLED | `machine.I2C` (hardware); `SoftI2C` foi adotado defensivamente numa revisão anterior e revertido após confirmação em `tests/05_oled_basic.py` e `tests/06_oled_full_diagnostic.py` |
| Mapeamento OLED | GPIO25 = SCL; GPIO16 = SDA, por predefinição |
| Atualização OLED | Somente na inicialização e nas transições estáveis |
| Versão do firmware no `diagram.json` | Não fixar `attrs.env`; usar a versão padrão/atual do Wokwi |
| Licença | CC0 1.0 Universal |
| Idioma do código | Inglês |
| Mensagens do OLED | Português, exatamente `Boa sorte!` e `Consegui` |
