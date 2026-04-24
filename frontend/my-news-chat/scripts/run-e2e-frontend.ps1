$ErrorActionPreference = "Stop"

$frontendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $frontendRoot

npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
