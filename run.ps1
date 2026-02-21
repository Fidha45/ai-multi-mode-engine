param(
    [ValidateSet("ollama", "openai")]
    [string]$Provider = "ollama",
    [string]$Model = "",
    [string]$OpenAIApiKey = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    Write-Host "Virtual environment Python not found at: $pythonPath" -ForegroundColor Red
    Write-Host "Create/install first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv"
    Write-Host "  .\venv\Scripts\python.exe -m pip install -r requirements.txt"
    exit 1
}

$env:AI_PROVIDER = $Provider

if ($Provider -eq "ollama") {
    $env:OLLAMA_MODEL = if ([string]::IsNullOrWhiteSpace($Model)) { "phi3:mini" } else { $Model }
} else {
    $env:OPENAI_MODEL = if ([string]::IsNullOrWhiteSpace($Model)) { "gpt-4o-mini" } else { $Model }
    if (-not [string]::IsNullOrWhiteSpace($OpenAIApiKey)) {
        $env:OPENAI_API_KEY = $OpenAIApiKey
    }
}

& $pythonPath (Join-Path $projectRoot "main.py")
