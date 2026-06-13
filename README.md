# FIN-BOT 📈

Pipeline de análise técnica multimercado (Brasil 🇧🇷 / EUA 🇺🇸 / Europa 🇪🇺 / China 🇨🇳)
com **página web ao vivo** atualizada a cada 15 min em horário de pregão, agente
Claude Code para análise qualitativa e dashboard local interativo.

> ⚠️ Ferramenta de apoio à análise. **Não é recomendação de investimento.**

## URL ao vivo
`https://mauricio1806.github.io/FIN-BOT/` — após configurar o GitHub Pages.

## Setup

```bash
git clone https://github.com/Mauricio1806/FIN-BOT.git
cd FIN-BOT
pip install -r requirements.txt
```

## Uso

```bash
python finbot.py html              # gera docs/index.html com os 4 mercados (página ao vivo)
python finbot.py screen            # ranqueia todos os ativos no terminal
python finbot.py analyze WEGE3.SA  # deep dive em 1 ativo
python finbot.py aporte 2000       # distribuição sugerida do aporte
python finbot.py backtest 1000     # backtest de DCA vs CDI (24 meses)
python finbot.py macro             # Selic, CDI, IPCA, juro real (BCB)
python finbot.py ofertas           # Tesouro Direto + régua de CDB/LCI
```

**Dashboard interativo local** (gráficos candlestick, RSI, MACD, simulador):
```bash
streamlit run dashboard.py
```
Ou clique duplo em `FIN-BOT.bat`.

## Atualização automática (GitHub Actions)

O workflow `.github/workflows/daily-report.yml` roda a cada 15 min em horário
de pregão (cobre B3 + NYSE + Europa + Ásia), regenera a página e dá push.

Setup: GitHub → Settings → Pages → Branch `main` / pasta `/docs` → Save.

## Mercados configurados (`config.yaml`)

- 🇧🇷 **Brasil**: ETFs (BOVA11, SMAL11, IVVB11, B5P211), blue chips, FIIs, BTC
- 🇺🇸 **EUA**: VOO, QQQ, Mag 7, SCHD, JPM, XOM, JNJ
- 🇪🇺 **Europa**: MSCI Europe, DAX, ASML, SAP, Nestlé, Roche, Shell
- 🇨🇳 **China & Ásia**: MCHI, KWEB, BABA, TSMC, Índia, Taiwan, Hong Kong

## Score técnico (0–100)

| Componente | Pontos |
|------------|--------|
| Tendência (SMA 20/50/200) | 40 |
| MACD | 20 |
| RSI(14) | 20 |
| Risco (ATR%) | 10 |
| Volume | 10 |

Calibrado para **aportes de longo prazo**: recuo em tendência saudável pontua bem.

## Insights automáticos

Cada página tem:
- **Regime de mercado** (EXPANSIVO / MISTO / DEFENSIVO) baseado em breadth
- Detecção de sobrevendidos em tendência sustentada (oportunidade)
- Sobrecomprados (cautela)
- Golden Cross / Death Cross recentes
- Volume anormal (movimento com convicção)
- Top/bottom 3 por condição técnica

## Testes (offline, sem rede)

```bash
python tests/test_offline.py
```
