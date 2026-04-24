$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $projectRoot

if (Test-Path ".\e2e_users.db") {
  Remove-Item ".\e2e_users.db" -Force
}

$env:DATABASE_URL = "sqlite:///./e2e_users.db"
$env:OTP_DEBUG_MODE = "true"
$env:E2E_FAKE_CHAT = "true"
$env:SMTP_HOST = ""
$env:PYTHONUNBUFFERED = "1"

.\myenv_gpu\Scripts\python.exe -m uvicorn api.app_server:app --host 127.0.0.1 --port 8000
