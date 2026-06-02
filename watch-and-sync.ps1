$root = "C:\Users\METREA-002\Desktop\ProjetoClaudeCode"
$debounceMs = 3000   # espera 3s após a última alteração antes de commitar

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $root
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName

$ignore = @('*.png', '*.jpg', '.git', 'watch-and-sync.ps1')

$timer = New-Object System.Timers.Timer
$timer.Interval = $debounceMs
$timer.AutoReset = $false

$syncJob = {
    param($root)
    Set-Location $root
    $status = git status --porcelain
    if (-not $status) { return }

    git add moedas.html server.ps1 CLAUDE.md .gitignore watch-and-sync.ps1 2>$null
    $staged = git diff --cached --name-only
    if (-not $staged) { return }

    $msg = "auto-sync: atualiza $($staged -join ', ') em $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    git commit -m $msg
    git push origin master
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Sincronizado: $($staged -join ', ')" -ForegroundColor Green
}

$elapsed = Register-ObjectEvent $timer -EventName Elapsed -Action {
    $timer.Stop()
    & $syncJob -root $root
}

$changed = Register-ObjectEvent $watcher -EventName Changed -Action {
    $file = $Event.SourceEventArgs.Name
    if ($file -match '\.(png|jpg)$' -or $file -eq 'watch-and-sync.ps1') { return }
    $timer.Stop()
    $timer.Start()
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Alteração detectada: $file — aguardando..." -ForegroundColor Yellow
}

$created = Register-ObjectEvent $watcher -EventName Created -Action {
    $file = $Event.SourceEventArgs.Name
    if ($file -match '\.(png|jpg)$' -or $file -eq 'watch-and-sync.ps1') { return }
    $timer.Stop()
    $timer.Start()
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Arquivo criado: $file — aguardando..." -ForegroundColor Yellow
}

$deleted = Register-ObjectEvent $watcher -EventName Deleted -Action {
    $file = $Event.SourceEventArgs.Name
    if ($file -match '\.(png|jpg)$') { return }
    $timer.Stop()
    $timer.Start()
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Arquivo removido: $file — aguardando..." -ForegroundColor Yellow
}

Write-Host "Monitorando '$root'" -ForegroundColor Cyan
Write-Host "Alterações serão enviadas ao GitHub automaticamente." -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar.`n" -ForegroundColor Yellow

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Unregister-Event $changed.Id
    Unregister-Event $created.Id
    Unregister-Event $deleted.Id
    Unregister-Event $elapsed.Id
    $watcher.Dispose()
    $timer.Dispose()
    Write-Host "`nMonitoramento encerrado." -ForegroundColor Red
}
