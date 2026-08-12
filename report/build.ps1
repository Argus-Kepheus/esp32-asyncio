<#
.SYNOPSIS
    Compiles a .tex document in this folder (relatorio.tex by default) into
    a PDF and cleans up LaTeX temporary/auxiliary files.

.DESCRIPTION
    Prefers `latexmk -lualatex` (handles however many passes are needed for
    the table of contents, references and page count to settle, and knows
    which files are its own temporary output). Falls back to two manual
    `lualatex` passes if `latexmk` is not installed, or if it fails at
    runtime (e.g. missing perl).

    Temporary files (.aux, .log, .out, .toc, .fls, .fdb_latexmk,
    .synctex.gz, .lof, .lot, .bbl, .blg, .run.xml, .bcf) are removed after a
    successful build by default. The resulting PDF is never deleted.

.PARAMETER Document
    Base name (without .tex) of the document to build, e.g. 'relatorio' or
    'apresentacao_mobile'. Defaults to 'relatorio'.

.PARAMETER Clean
    Only remove temporary files; do not compile.

.PARAMETER KeepTemp
    Compile, but skip the temporary-file cleanup step afterward (useful
    when debugging a LaTeX error from the .log file).

.PARAMETER Open
    Open the resulting PDF after a successful build.

.EXAMPLE
    .\build.ps1
    Compile relatorio.tex and clean up temporary files.

.EXAMPLE
    .\build.ps1 -Document apresentacao_mobile
    Compile apresentacao_mobile.tex and clean up temporary files.

.EXAMPLE
    .\build.ps1 -Clean
    Remove relatorio's leftover temporary files without compiling anything.

.EXAMPLE
    .\build.ps1 -Document apresentacao_mobile -Clean
    Remove apresentacao_mobile's leftover temporary files without compiling.

.EXAMPLE
    .\build.ps1 -KeepTemp -Open
    Compile relatorio, keep the .log/.aux files around for troubleshooting,
    and open the PDF.
#>

[CmdletBinding()]
param(
    [string]$Document = 'relatorio',
    [switch]$Clean,
    [switch]$KeepTemp,
    [switch]$Open
)

$ErrorActionPreference = 'Stop'

# Always operate relative to this script's own folder, regardless of the
# caller's current directory.
$ReportDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ReportDir

$BaseName = $Document
$TexFile = "$BaseName.tex"
$PdfFile = "$BaseName.pdf"

# Extensions latexmk/lualatex are expected to produce as byproducts of a
# build. Never includes .tex or .pdf.
$TempExtensions = @(
    '.aux', '.log', '.out', '.toc', '.fls', '.fdb_latexmk',
    '.synctex.gz', '.lof', '.lot', '.bbl', '.blg', '.run.xml', '.bcf',
    '.nav', '.snm', '.vrb'
)

function Remove-TempFiles {
    $removed = 0
    foreach ($ext in $TempExtensions) {
        $candidate = Join-Path $ReportDir "$BaseName$ext"
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            Remove-Item -LiteralPath $candidate -Force
            Write-Host "Removed $candidate"
            $removed++
        }
    }
    if ($removed -eq 0) {
        Write-Host 'No temporary files to remove.'
    }
}

if ($Clean) {
    Remove-TempFiles
    return
}

if (-not (Test-Path -LiteralPath $TexFile -PathType Leaf)) {
    Write-Error "Cannot find $TexFile in $ReportDir"
    exit 1
}

$latexmk = Get-Command latexmk -ErrorAction SilentlyContinue
$lualatex = Get-Command lualatex -ErrorAction SilentlyContinue

if (-not $latexmk -and -not $lualatex) {
    Write-Error 'Neither latexmk nor lualatex was found on PATH. Install a LaTeX distribution (e.g. MiKTeX or TeX Live) that provides LuaLaTeX.'
    exit 1
}

function Invoke-ManualLualatexPasses {
    for ($i = 1; $i -le 2; $i++) {
        Write-Host "lualatex pass $i/2 ..."
        & lualatex -interaction=nonstopmode -halt-on-error $TexFile
        if ($LASTEXITCODE -ne 0) {
            throw "lualatex exited with code $LASTEXITCODE on pass $i"
        }
    }
}

$buildSucceeded = $false

try {
    if ($latexmk) {
        Write-Host "Building $TexFile with latexmk -lualatex ..."
        & latexmk -lualatex -interaction=nonstopmode -halt-on-error $TexFile
        if ($LASTEXITCODE -ne 0) {
            if ($lualatex) {
                Write-Warning "latexmk failed (exit code $LASTEXITCODE) -- falling back to two manual lualatex passes. This usually means latexmk's script engine (perl) is missing; see https://miktex.org/kb/fix-script-engine-not-found."
                Invoke-ManualLualatexPasses
            }
            else {
                throw "latexmk exited with code $LASTEXITCODE, and no lualatex fallback is available"
            }
        }
    }
    else {
        Write-Host "latexmk not found; building $TexFile with two manual lualatex passes ..."
        Invoke-ManualLualatexPasses
    }

    if (-not (Test-Path -LiteralPath $PdfFile -PathType Leaf)) {
        throw "Build reported success but $PdfFile was not produced."
    }

    $buildSucceeded = $true
    Write-Host "Build succeeded: $PdfFile"
}
catch {
    Write-Error "Build failed: $_"
    Write-Host "Check $BaseName.log for details. Temporary files were kept for troubleshooting."
    exit 1
}

if ($buildSucceeded -and -not $KeepTemp) {
    Remove-TempFiles
}

if ($buildSucceeded -and $Open) {
    Invoke-Item $PdfFile
}
