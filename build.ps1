# Gera o executável CotacaoMoedas.exe
# Uso: pwsh -File build.ps1

Set-Location $PSScriptRoot

Write-Host "Instalando dependências..." -ForegroundColor Cyan
pip install pywebview pyinstaller --quiet

Write-Host "Gerando executável..." -ForegroundColor Cyan
pyinstaller `
    --onedir `
    --windowed `
    --name "CotacaoMoedas" `
    --add-data "app.py;." `
    --collect-all streamlit `
    --collect-all pywebview `
    --collect-all altair `
    --collect-all yfinance `
    --collect-all pandas `
    --collect-all plotly `
    --hidden-import "streamlit.web.bootstrap" `
    --hidden-import "streamlit.runtime.scriptrunner" `
    --hidden-import "streamlit.runtime.state" `
    --noconfirm `
    launcher.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nConcluído! Executável em: dist\CotacaoMoedas\CotacaoMoedas.exe" -ForegroundColor Green
} else {
    Write-Host "`nErro ao gerar o executável." -ForegroundColor Red
}
