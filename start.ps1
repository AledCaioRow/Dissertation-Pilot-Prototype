# One-step local launch for the study app (backend + frontend), for Windows.
# Runs in STUB mode out of the box (no API key needed). First run installs dependencies.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv")) {
  Write-Host "First run: setting up the Python virtualenv..."
  python -m venv .venv
  & ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
  & ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
}

if (-not (Test-Path "frontend\node_modules")) {
  Write-Host "First run: installing frontend dependencies..."
  Push-Location frontend; npm install; Pop-Location
}

Write-Host ""
Write-Host "Starting the study app..."
Write-Host "  backend  -> http://localhost:8000"
Write-Host "  frontend -> http://localhost:5173   (opens in your browser)"
Write-Host ""

# Backend in its own window
Start-Process -FilePath "powershell" -ArgumentList @(
  "-NoExit", "-Command",
  "Set-Location '$PSScriptRoot'; .\.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000"
)
# Frontend in its own window (Vite opens the browser via server.open)
Start-Process -FilePath "powershell" -ArgumentList @(
  "-NoExit", "-Command",
  "Set-Location '$PSScriptRoot\frontend'; npm run dev"
)

Write-Host "Two windows opened (backend + frontend). Close them to stop the app."
