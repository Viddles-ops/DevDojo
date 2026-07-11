# Launch the Jett Marketing Agent. Usage:  .\run.ps1
# Works from anywhere, with any Python on PATH — the launcher module
# always bootstraps and uses this project's own .venv.
Set-Location $PSScriptRoot
python -m marketer.launcher
