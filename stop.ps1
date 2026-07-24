# Stop DevDojo. Usage:  .\stop.ps1
# run.ps1 launches app.py as a child process; Ctrl-C in the launcher window
# leaves that child running and holding the port. This kills every DevDojo
# instance (launcher + app.py) and confirms the port is free, so the next
# run.ps1 starts clean instead of stacking a zombie on top.
Set-Location $PSScriptRoot

# DEVDOJO_PORT mirrors config.py (default 5057).
$port = if ($env:DEVDOJO_PORT) { [int]$env:DEVDOJO_PORT } else { 5057 }

# Match by command line: any python whose command line references DevDojo
# (covers `...\DevDojo\app.py` and `...\DevDojo\.venv\...python app.py`) or the
# launcher module (which can run under another project's venv, so its command
# line may not mention DevDojo at all).
$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'DevDojo' -or $_.CommandLine -match 'tutor\.launcher' }

if ($procs) {
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "stopped PID $($p.ProcessId)"
    }
} else {
    Write-Host "no DevDojo process running"
}

# Give sockets a moment to release, then confirm the port is actually free.
# Retry a few times so a socket still in teardown is not reported as stuck.
$listener = $null
foreach ($i in 1..6) {
    Start-Sleep -Milliseconds 500
    $listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $listener) { break }
}

if ($listener) {
    $owner = Get-Process -Id $listener.OwningProcess -ErrorAction SilentlyContinue
    Write-Warning ("port {0} still held by PID {1} ({2}). Not a DevDojo process - inspect before launching." -f $port, $listener.OwningProcess, $owner.ProcessName)
} else {
    Write-Host "port $port is free - safe to run .\run.ps1"
}
