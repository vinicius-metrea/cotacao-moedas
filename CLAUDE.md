# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## GitHub repository

Repositório: **https://github.com/vinicius-metrea/cotacao-moedas**

### Sincronização automática com GitHub

O script `watch-and-sync.ps1` monitora o diretório e envia alterações ao GitHub automaticamente após 3 segundos de inatividade:

```powershell
pwsh -File watch-and-sync.ps1
```

Arquivos monitorados: `moedas.html`, `server.ps1`, `CLAUDE.md`, `.gitignore`, `watch-and-sync.ps1`. Imagens (`.png`, `.jpg`) são ignoradas.

Para enviar manualmente:
```powershell
git add -A && git commit -m "mensagem" && git push origin master
```

## Running the project

**Option 1 — abrir direto no browser (sem servidor):**
```
start moedas.html
```
Funciona para a maioria dos casos; as chamadas à API Frankfurter são feitas direto do browser.

**Option 2 — servidor local com proxy (recomendado para evitar CORS):**
```powershell
pwsh -File server.ps1
```
Acesse em `http://localhost:8080`. O servidor proxy redireciona `/api/*` → `https://api.frankfurter.app/*`.

## Architecture

O projeto é uma **single-page app** contida inteiramente em `moedas.html` (HTML + CSS + JS inline, sem build step, sem dependências npm).

### Data flow

```
Browser → Frankfurter API (api.frankfurter.app)
       OU
Browser → server.ps1 (/api/*) → Frankfurter API
```

O site faz **3 chamadas paralelas** ao carregar (via `Promise.all`):
- `/latest?from={base}` — cotações do dia
- `/2025-01-02?from={base}` — taxa no início do ano (para calcular variação % anual)
- `/2025-01-01..?from={base}&to={currencies}` — histórico 2025 para o gráfico de linha

### `server.ps1`

Servidor HTTP puro em PowerShell (sem dependências externas). Serve arquivos estáticos do diretório do projeto e atua como proxy reverso para a Frankfurter API via rotas `/api/*`. Útil quando o browser bloqueia CORS em `file://`.

### Charting

Usa **Chart.js 4.4.0** via CDN (`cdn.jsdelivr.net`). Três gráficos são criados/destruídos dinamicamente ao trocar a moeda base:
- `barChart` — comparativo de moedas vs base (bar)
- `donutChart` — distribuição por região (doughnut)
- `lineChart` — evolução em 2025 normalizada (base 100 = primeiro dia do ano)

### Moeda base

O seletor no header dispara `changeBase(value)`, que reinicia todo o ciclo de carregamento com a nova moeda base. A moeda base é excluída dos cards/tabela e dos datasets do gráfico de linha.
