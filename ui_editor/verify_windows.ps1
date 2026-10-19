param(
    [ValidateSet('all', 'module', 'check')]
    [string]$Mode = 'all',
    [string]$TestModule = '',
    [ValidateSet('all', 'tests', 'compileall', 'ruff', 'wincompat')]
    [string]$Check = 'all'
)

$ErrorActionPreference = 'Stop'

# This script is intentionally ASCII-only for Windows PowerShell 5.1.
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$venv = Join-Path (Split-Path $repo -Parent) 'mxsj-venv'

$python = $null
$pythonSelector = @()
$pythonCandidates = @(
    (Join-Path $env:LocalAppData 'Programs\Python\Python314\python.exe'),
    (Join-Path $env:LocalAppData 'Programs\Python\Python313\python.exe'),
    (Join-Path $env:LocalAppData 'Programs\Python\Python312\python.exe'),
    (Join-Path $env:LocalAppData 'Programs\Python\Python311\python.exe'),
    (Join-Path $env:LocalAppData 'Programs\Python\Python310\python.exe')
)

foreach ($candidate in $pythonCandidates) {
    if (Test-Path -LiteralPath $candidate) {
        $python = $candidate
        break
    }
}

if (-not $python) {
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        $python = 'py.exe'
        $pythonSelector = @('-3')
    }
}

if (-not $python) {
    throw 'No Windows Python 3.10+ found.'
}

Write-Host "Using Python: $python"
& $python @pythonSelector --version
if ($LASTEXITCODE -ne 0) {
    throw 'Windows Python could not be started.'
}

$venvPython = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating virtual environment: $venv"
    & $python @pythonSelector -m venv $venv
    if ($LASTEXITCODE -ne 0) {
        throw 'Virtual environment creation failed.'
    }
}

Write-Host 'Upgrading pip.'
& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw 'pip upgrade failed.'
}

Write-Host 'Installing ui_editor and ruff.'
$packagePath = Join-Path $repo 'ui_editor'
& $venvPython -m pip install -e $packagePath ruff
if ($LASTEXITCODE -ne 0) {
    throw 'Dependency installation failed.'
}

Push-Location $repo
try {
    $env:PYTHONPATH = Join-Path $repo 'ui_editor\src'
    $env:QT_QPA_PLATFORM = 'offscreen'

    if ($Mode -eq 'module') {
        if ([string]::IsNullOrWhiteSpace($TestModule)) {
            throw 'TestModule is required when Mode is module.'
        }
        $modulePath = Join-Path 'ui_editor/tests' $TestModule
        if (-not (Test-Path -LiteralPath $modulePath)) {
            throw "Test module not found: $modulePath"
        }
        $testArguments = @('-m', 'unittest', 'discover', '-s', 'ui_editor/tests', '-p', $TestModule, '-v')
        $checksToRun = @([pscustomobject]@{
                Name = "unittest ($TestModule)"
                Args = $testArguments
            })
    } elseif ($Mode -eq 'check') {
        $checksToRun = @()
        if ($Check -eq 'all' -or $Check -eq 'tests') {
            $checksToRun += [pscustomobject]@{
                Name = 'unittest (all)'
                Args = @('-m', 'unittest', 'discover', '-s', 'ui_editor/tests', '-v')
            }
        }
        if ($Check -eq 'all' -or $Check -eq 'compileall') {
            $checksToRun += [pscustomobject]@{
                Name = 'compileall'
                Args = @('-m', 'compileall', '-q', 'ui_editor/src', 'ui_editor/tests')
            }
        }
        if ($Check -eq 'all' -or $Check -eq 'ruff') {
            $checksToRun += [pscustomobject]@{
                Name = 'ruff'
                Args = @('-m', 'ruff', 'check', 'ui_editor')
            }
        }
        if ($Check -eq 'all' -or $Check -eq 'wincompat') {
            $checksToRun += [pscustomobject]@{
                Name = 'windows compatibility'
                Args = @('tools/devkit/check_windows_compat.py', 'ui_editor', '--strict')
            }
        }
    } else {
        $checksToRun = @(
            [pscustomobject]@{
                Name = 'unittest (all)'
                Args = @('-m', 'unittest', 'discover', '-s', 'ui_editor/tests', '-v')
            },
            [pscustomobject]@{
                Name = 'compileall'
                Args = @('-m', 'compileall', '-q', 'ui_editor/src', 'ui_editor/tests')
            },
            [pscustomobject]@{
                Name = 'ruff'
                Args = @('-m', 'ruff', 'check', 'ui_editor')
            },
            [pscustomobject]@{
                Name = 'windows compatibility'
                Args = @('tools/devkit/check_windows_compat.py', 'ui_editor', '--strict')
            }
        )
    }

    $failed = $false
    foreach ($selectedCheck in $checksToRun) {
        Write-Host ""
        Write-Host "===== $($selectedCheck.Name) ====="
        & $venvPython @($selectedCheck.Args)
        if ($LASTEXITCODE -ne 0) {
            $failed = $true
            Write-Warning "$($selectedCheck.Name) failed with exit code $LASTEXITCODE"
        } else {
            Write-Host "$($selectedCheck.Name) passed"
        }
    }

    if ($failed) {
        exit 1
    }
    Write-Host ''
    Write-Host 'All checks passed.'
}
finally {
    Pop-Location
}
