# Launch DevDojo. Usage:  .\run.ps1
# Works from anywhere, with any Python on PATH — the launcher module
# always bootstraps and uses DevDojo's own .venv (never another project's).
Set-Location $PSScriptRoot
python -m tutor.launcher
