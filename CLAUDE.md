# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## GitHub repository

Repositório: **https://github.com/vinicius-metrea/cotacao-moedas**

### Sincronização automática com GitHub

O Claude Code possui um hook `Stop` configurado em `.claude/settings.local.json` que faz commit e push automaticamente ao final de cada resposta.

Para enviar manualmente:
```powershell
git add -A && git commit -m "mensagem" && git push origin master
```

## Running the project

**Modo web (desenvolvimento):**
```powershell
streamlit run app.py
```
O app abre em `http://localhost:8501`. Requer Python 3.12+:
```powershell
pip install streamlit yfinance pandas plotly
```

**Modo desktop (executável):**
```
dist\CotacaoMoedas\CotacaoMoedas.exe
```
O executável abre o app numa janela nativa via `pywebview`, sem precisar de navegador ou terminal. Para rebuild:
```powershell
pwsh -File build.ps1
```
Requer adicionalmente: `pip install pywebview pyinstaller`

## Architecture

O projeto tem dois modos de execução: **web** (`streamlit run app.py`) e **desktop** (executável PyInstaller).

### Arquivos principais

| Arquivo | Função |
|---|---|
| `app.py` | App Streamlit — toda a UI e lógica de dados |
| `launcher.py` | Entry point do executável desktop (inicia Streamlit em thread e abre janela pywebview) |
| `build.ps1` | Script PowerShell que gera `dist\CotacaoMoedas\CotacaoMoedas.exe` via PyInstaller |
| `CotacaoMoedas.spec` | Spec do PyInstaller (gerado automaticamente pelo build.ps1) |

### Stack

| Biblioteca | Função |
|---|---|
| `streamlit` | Framework web / UI |
| `yfinance` | Dados de câmbio (Yahoo Finance) |
| `plotly` | Gráficos interativos |
| `pandas` | Manipulação de dados |
| `pywebview` | Janela nativa para o modo desktop |
| `pyinstaller` | Empacotamento do executável (build apenas) |

### Data flow

```
app.py → yfinance (Yahoo Finance) → pandas DataFrame → plotly charts + st.dataframe
```

**Modo desktop:**
```
launcher.py → thread: Streamlit (porta 8501) → pywebview (janela nativa apontando para localhost:8501)
```

Os dados são buscados via `yf.download()` com tickers no formato `{BASE}{TARGET}=X` (ex: `USDBRL=X`), cobrindo `2025-01-01` até hoje. O cache é de **1 hora** via `@st.cache_data(ttl=3600)`.

### Estrutura do app (`app.py`)

1. **Header** — título + seletor de moeda base (`USD/EUR/BRL/GBP/JPY`) + botão ↺ Atualizar
2. **Cards** — grid 5 colunas com flag, código, taxa atual e variação % no ano (verde/vermelho/cinza)
3. **Gráfico de barras** — comparativo das principais moedas vs base
4. **Gráfico donut** — distribuição das moedas por região geográfica
5. **Gráfico de linha** — evolução normalizada em 2025 (Jan 2025 = 100) para 6 moedas
6. **Tabela** — todas as moedas com taxa direta, inversa e variação no ano

### Moedas monitoradas (20 total)

`USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, BRL, MXN, INR, KRW, SGD, NOK, SEK, NZD, ZAR, HKD, DKK, ARS`

### Moeda base

O `st.selectbox` no header altera a variável `base`, que é passada para `fetch_data(base)`. Trocar a base limpa o cache e rebusca todos os dados com a nova moeda de referência. A moeda base é excluída dos cards, gráficos e tabela.
