# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## GitHub repository

Repositório: **https://github.com/vinicius-metrea/cotacao-moedas**

### Sincronização automática com GitHub

O script `watch-and-sync.ps1` monitora o diretório e envia alterações ao GitHub automaticamente após 3 segundos de inatividade:

```powershell
pwsh -File watch-and-sync.ps1
```

Para enviar manualmente:
```powershell
git add -A && git commit -m "mensagem" && git push origin master
```

## Running the project

```powershell
streamlit run app.py
```

O app abre automaticamente em `http://localhost:8501`. Requer Python 3.12+ e os pacotes abaixo instalados:

```powershell
pip install streamlit yfinance pandas plotly
```

## Architecture

O projeto é um **app Streamlit single-file** contido inteiramente em `app.py`, sem build step nem dependências npm.

### Stack

| Biblioteca | Função |
|---|---|
| `streamlit` | Framework web / UI |
| `yfinance` | Dados de câmbio (Yahoo Finance) |
| `plotly` | Gráficos interativos |
| `pandas` | Manipulação de dados |

### Data flow

```
app.py → yfinance (Yahoo Finance) → pandas DataFrame → plotly charts + st.dataframe
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
