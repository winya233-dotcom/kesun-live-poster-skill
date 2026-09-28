param(
    [switch]$SkipDependencies,
    [switch]$SkipFonts
)

$ErrorActionPreference = "Stop"
$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
    throw "Python was not found. Install Python 3.10 or 3.11 and run setup.ps1 again."
}

function Invoke-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-Checked { & $Python.Source (Join-Path $SkillDir "scripts\install_bundled_assets.py") }

if (-not $SkipDependencies) {
    Invoke-Checked { & $Python.Source -m pip install -r (Join-Path $SkillDir "scripts\requirements.txt") }
}

if (-not $SkipFonts) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $SkillDir "scripts\install_fonts.ps1")
}

Invoke-Checked { & $Python.Source (Join-Path $SkillDir "scripts\check_environment.py") }
