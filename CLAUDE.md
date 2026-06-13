# FIN-BOT — Contexto do projeto para Claude Code

Pipeline de análise técnica multimercado + página web ao vivo + dashboard local.

## Arquitetura
- `finbot.py` — CLI (html | screen | analyze | aporte | backtest | macro | ofertas | report)
- `dashboard.py` — painel Streamlit local (gráficos candlestick, RSI, MACD, simulador)
- `FIN-BOT.bat` — atalho 1-clique para abrir o dashboard
- `src/data.py` — yfinance + cache SQLite 12h
- `src/indicators.py` — SMA/EMA/RSI/MACD/Bollinger/ATR/volume
- `src/trends.py` — classificação de regime + score 0-100
- `src/screener.py` — ranking + alocador de aporte
- `src/insights.py` — breadth, regime de mercado, bullets automáticos
- `src/html_report.py` — página única multimercado com abas
- `src/backtest.py` — DCA mensal sem lookahead vs CDI
- `src/macro.py` — Selic/CDI/IPCA via API SGS do BCB
- `src/renda_fixa.py` — Tesouro Direto + régua CDB/LCI
- `src/report.py` — markdown em reports/
- `config.yaml` — 4 mercados com watchlists e pesos
- `.github/workflows/daily-report.yml` — atualização 15min em horário de pregão
- `.claude/agents/fin-bot.md` — agente analista

## Convenções
- Tickers Yahoo Finance (B3 com `.SA`; cripto `XXX-USD`)
- Score otimizado para aporte, não trade
- Nada é recomendação — manter disclaimers

## Comandos
```bash
python finbot.py html             # regenera docs/index.html
python finbot.py screen
python finbot.py analyze BOVA11.SA
python finbot.py aporte 2000
streamlit run dashboard.py        # ou clique duplo em FIN-BOT.bat
```

## Regras
- Não tocar em `src/` sem pedido; ajustes em `config.yaml`
- Testes: `python tests/test_offline.py`
