# Relatório LaTeX

Esta pasta contém dois documentos do projeto CESS-UFF / SGIMP:

- `relatorio.tex` — relatório técnico completo.
- `apresentacao_mobile.tex` — versão resumida em formato de slides
  verticais (proporção 9:16), pensada para ser lida em tela de
  smartphone. Reaproveita as mesmas fontes (Latin Modern) e a mesma
  paleta de cores do relatório, e é fiel ao conteúdo dele — apenas
  condensado.

## Estrutura

```text
report/
├── relatorio.tex
├── relatorio.pdf
├── apresentacao_mobile.tex
├── apresentacao_mobile.pdf
├── build.ps1
├── README.md
└── figures/
    └── circuito-wokwi.png
```

## Compilação automatizada (PowerShell)

A partir da pasta `report/` (ou de qualquer lugar — o script sempre opera
na sua própria pasta):

```powershell
.\build.ps1                                   # compila relatorio.tex (padrão)
.\build.ps1 -Document apresentacao_mobile     # compila apresentacao_mobile.tex
```

Isso compila o documento escolhido em PDF e remove automaticamente os
arquivos temporários gerados (`.aux`, `.log`, `.out`, `.toc`, `.fls`,
`.fdb_latexmk`, `.synctex.gz`, etc.) ao final. O PDF resultante nunca é
apagado.

Usa `latexmk -lualatex` quando disponível (resolve sozinho quantas
passagens são necessárias); se `latexmk` não estiver instalado, ou falhar
por falta do interpretador `perl` (comum em instalações MiKTeX sem o
componente Perl), o script cai automaticamente para duas passagens
manuais de `lualatex`, que é o suficiente para os dois documentos.

Outras opções (combináveis com `-Document`):

```powershell
.\build.ps1 -Clean                              # só remove os temporários de relatorio, sem compilar
.\build.ps1 -Document apresentacao_mobile -Clean # idem, para a apresentação
.\build.ps1 -KeepTemp                           # compila mas mantém os temporários (útil para depurar o .log)
.\build.ps1 -Open                               # compila e abre o PDF resultante ao final
```

Se a compilação falhar, o script preserva os arquivos temporários (mesmo
sem `-KeepTemp`) para permitir inspecionar o `.log` correspondente.

## Compilação no TeXstudio

1. Abra o `.tex` desejado (`relatorio.tex` ou `apresentacao_mobile.tex`) no TeXstudio.
2. Em **Opções > Configurar TeXstudio > Compilação**, selecione **LuaLaTeX** como compilador padrão.
3. Compile o documento duas vezes para atualizar o sumário/rodapé, as referências internas e o número total de páginas.

Ambos os arquivos contêm a diretiva:

```tex
% !TeX program = lualatex
```

Em instalações nas quais o TeXstudio respeita diretivas mágicas, essa linha já seleciona o compilador correto.
