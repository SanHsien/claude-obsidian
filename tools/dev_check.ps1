[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    $pythonExe = $venvPython
} else {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONDONTWRITEBYTECODE = "1"

function Invoke-PythonStep {
    param(
        [Parameter(Mandatory)]
        [string]$Label,
        [Parameter(Mandatory)]
        [string[]]$Arguments
    )

    Write-Host "==> $Label"
    & $script:pythonExe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

Invoke-PythonStep -Label "Compile fork Python" -Arguments @(
    "-m", "compileall", "-q", "tools"
)
Invoke-PythonStep -Label "Ruff (E9 + F)" -Arguments @(
    "-m", "ruff", "check", "--select", "E9,F", "--target-version", "py311", "tools"
)
Invoke-PythonStep -Label "Pytest overlay" -Arguments @("-m", "pytest", "tools", "-q")
Invoke-PythonStep -Label "Check fork Markdown links" -Arguments @(
    "tools\check_links.py"
)

$portableTests = @(
    "tests\test_package_validation.py",
    "tests\test_knowledge_contracts.py",
    "tests\test_contracts.py",
    "tests\test_benchmark_tools.py",
    "tests\test_windows_compat.py"
)
foreach ($testFile in $portableTests) {
    Invoke-PythonStep -Label "Portable product test $testFile" -Arguments @($testFile)
}

Invoke-PythonStep -Label "Package validate" -Arguments @(
    "scripts\claude-obsidian.py", "package", "validate"
)
Invoke-PythonStep -Label "Contracts check-only" -Arguments @(
    "scripts\claude-obsidian.py", "contracts", "--check-only"
)

Write-Host "WINDOWS DEV CHECK GREEN"
