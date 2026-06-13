"""
FIN-BOT | Painel de controle (Streamlit)
Rode na raiz do projeto:  streamlit run dashboard.py

Abas: Ranking | Gráficos | Aporte | Backtest | Macro
Usa o mesmo motor do CLI (src/) — nada duplicado.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml
from plotly.subplots import make_subplots

from src.data import fetch_history
from src.indicators import enrich
from src.screener import allocate, screen
from src.trends import analyze

st.set_page_config(page_title="FIN-BOT", page_icon="📈", layout="wide")

TREND_COLOR = {
    "ALTA_FORTE": "#16a34a", "ALTA": "#4ade80", "LATERAL": "#eab308",
    "BAIXA": "#f87171", "BAIXA_FORTE": "#dc2626",
}


@st.cache_data(ttl=3600, show_spinner=False)
def load_config() -> dict:
    with open(Path(__file__).resolve().parent / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


@st.cache_data(ttl=3600, show_spinner="Buscando cotações...")
def cached_screen(tickers: tuple[str, ...], period: str, force: bool):
    return screen(list(tickers), period=period, force=force)


@st.cache_data(ttl=3600, show_spinner="Buscando histórico...")
def cached_history(ticker: str, period: str) -> pd.DataFrame:
    return fetch_history(ticker, period=period)


@st.cache_data(ttl=3600, show_spinner="Consultando Banco Central...")
def cached_macro() -> dict:
    from src.macro import get_macro
    return get_macro()


cfg = load_config()

# ---------------- Sidebar ----------------
st.sidebar.title("📈 FIN-BOT")
st.sidebar.caption("Painel de análise — não é recomendação de investimento.")
valor_aporte = st.sidebar.number_input("Valor do aporte (R$)", 100.0, 1_000_000.0, 2000.0, 100.0)
tilt = st.sidebar.slider("Tilt (0 = pesos-alvo · 1 = técnico)", 0.0, 1.0, 0.5, 0.05)
if st.sidebar.button("🔄 Atualizar cotações agora"):
    st.cache_data.clear()
    st.rerun()

analyses = cached_screen(tuple(cfg["watchlist"]), cfg.get("period", "2y"), False)

tab_rank, tab_chart, tab_aporte, tab_bt, tab_macro, tab_rf = st.tabs(
    ["🏆 Ranking", "📊 Gráficos", "💰 Aporte", "⏪ Backtest", "🌎 Macro", "🏦 Renda Fixa"]
)

# ---------------- Ranking ----------------
with tab_rank:
    st.subheader("Ranking da watchlist por condição técnica")
    df_rank = pd.DataFrame([{
        "Ticker": a.ticker, "Preço": a.price, "Tendência": a.trend,
        "Score": a.score, "RSI": a.rsi, "MACD": a.macd_state,
        "vs Máx 52s (%)": a.pct_from_high_52w, "ATR %": a.atr_pct, "Vol x": a.vol_ratio,
    } for a in analyses])

    def _style_trend(v):
        return f"color: {TREND_COLOR.get(v, '#888')}; font-weight: 700"

    st.dataframe(
        df_rank.style.map(_style_trend, subset=["Tendência"])
        .background_gradient(subset=["Score"], cmap="RdYlGn", vmin=0, vmax=100)
        .format({"Preço": "{:,.2f}", "vs Máx 52s (%)": "{:.1f}", "ATR %": "{:.2f}"}),
        use_container_width=True, hide_index=True, height=520,
    )
    sinais = [(a.ticker, s) for a in analyses for s in a.signals]
    if sinais:
        st.subheader("⚡ Sinais do dia")
        for t, s in sinais:
            st.markdown(f"- **{t}** — {s}")

# ---------------- Gráficos ----------------
with tab_chart:
    ticker = st.selectbox("Ativo", [a.ticker for a in analyses])
    df = enrich(cached_history(ticker, cfg.get("period", "2y")))
    janela = st.radio("Janela", ["6 meses", "1 ano", "Tudo"], horizontal=True, index=1)
    n = {"6 meses": 126, "1 ano": 252, "Tudo": len(df)}[janela]
    d = df.tail(n)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2],
                        vertical_spacing=0.03,
                        subplot_titles=(f"{ticker} — preço, médias e Bollinger", "RSI(14)", "MACD"))
    fig.add_trace(go.Candlestick(x=d.index, open=d["open"], high=d["high"],
                                 low=d["low"], close=d["close"], name="Preço"), 1, 1)
    for col, cor in [("sma20", "#60a5fa"), ("sma50", "#f59e0b"), ("sma200", "#a78bfa")]:
        fig.add_trace(go.Scatter(x=d.index, y=d[col], name=col.upper(),
                                 line=dict(width=1.3, color=cor)), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d["bb_upper"], name="BB sup",
                             line=dict(width=0.7, color="#64748b", dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d["bb_lower"], name="BB inf", fill="tonexty",
                             fillcolor="rgba(100,116,139,0.08)",
                             line=dict(width=0.7, color="#64748b", dash="dot")), 1, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d["rsi14"], name="RSI",
                             line=dict(color="#e879f9", width=1.5)), 2, 1)
    fig.add_hline(y=70, line_dash="dash", line_color="#f87171", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#4ade80", row=2, col=1)
    fig.add_trace(go.Bar(x=d.index, y=d["macd_hist"], name="Hist",
                         marker_color=["#16a34a" if v >= 0 else "#dc2626" for v in d["macd_hist"]]), 3, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d["macd"], name="MACD",
                             line=dict(color="#60a5fa", width=1.2)), 3, 1)
    fig.add_trace(go.Scatter(x=d.index, y=d["macd_signal"], name="Sinal",
                             line=dict(color="#f59e0b", width=1.2)), 3, 1)
    fig.update_layout(height=760, xaxis_rangeslider_visible=False,
                      legend=dict(orientation="h", y=1.04), margin=dict(t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

    a = next(x for x in analyses if x.ticker == ticker)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{a.score}/100")
    c2.metric("Tendência", a.trend)
    c3.metric("RSI(14)", a.rsi)
    c4.metric("vs Máx 52s", f"{a.pct_from_high_52w}%")

# ---------------- Aporte ----------------
with tab_aporte:
    st.subheader(f"Distribuição sugerida de R$ {valor_aporte:,.2f}")
    plan = allocate(analyses, valor_aporte, cfg.get("target_weights"),
                    tilt=tilt, min_score=cfg.get("min_score", 35))
    rows = [{"Ticker": t, **v} for t, v in plan.items() if not t.startswith("_")]
    if rows:
        df_plan = pd.DataFrame(rows)
        col_a, col_b = st.columns([1, 1])
        with col_a:
            fig_pie = go.Figure(go.Pie(labels=df_plan["Ticker"], values=df_plan["valor"],
                                       hole=0.45, textinfo="label+percent"))
            fig_pie.update_layout(height=420, margin=dict(t=10, b=10), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_b:
            st.dataframe(df_plan.rename(columns={
                "peso_%": "Peso %", "valor": "Valor R$", "qtd_aprox": "Qtd aprox.",
                "preco": "Preço", "score": "Score", "tendencia": "Tendência"}),
                use_container_width=True, hide_index=True, height=420)
        excl = plan.get("_excluidos_no_mes")
        if excl:
            st.warning(f"Fora do aporte este mês: **{', '.join(excl['tickers'])}** — {excl['motivo']}")
    st.caption("Sugestão matemática (pesos-alvo × condição técnica). A decisão é sua.")

# ---------------- Backtest ----------------
with tab_bt:
    st.subheader("Backtest: aportes mensais — estratégias vs CDI")
    meses = st.slider("Meses simulados", 6, 48, 24)
    if st.button("▶ Rodar backtest"):
        from src.backtest import run_backtest
        with st.spinner(f"Baixando {len(cfg['watchlist'])} ativos (5 anos) e simulando..."):
            price_data = {}
            for t in cfg["watchlist"]:
                try:
                    price_data[t] = fetch_history(t, period=cfg.get("backtest_period", "5y"))
                except Exception as exc:
                    st.warning(f"{t}: {exc}")
            results = run_backtest(price_data, amount=valor_aporte, months=meses,
                                   target_weights=cfg.get("target_weights"),
                                   min_score=cfg.get("min_score", 35),
                                   cdi_anual=cfg.get("cdi_anual", 0.105))
        df_bt = pd.DataFrame([{
            "Estratégia": r.label, "Total aportado": r.total_aportado,
            "Valor final": r.valor_final, "Retorno %": r.retorno_pct,
            "Max DD %": r.max_drawdown_pct,
        } for r in results])
        st.dataframe(df_bt.style.format({"Total aportado": "{:,.2f}", "Valor final": "{:,.2f}"}),
                     use_container_width=True, hide_index=True)
        fig_bt = go.Figure()
        for r in results:
            fig_bt.add_trace(go.Scatter(x=r.series.index, y=r.series.values,
                                        mode="lines", name=r.label))
        fig_bt.update_layout(height=440, title="Evolução do valor da carteira",
                             legend=dict(orientation="h", y=1.08), margin=dict(t=60))
        st.plotly_chart(fig_bt, use_container_width=True)
        st.caption("Sem custos, impostos ou dividendos. Passado não garante futuro — "
                   "serve para comparar REGRAS de alocação.")

# ---------------- Macro ----------------
with tab_macro:
    st.subheader("Cenário macro Brasil (Banco Central)")
    macro = cached_macro()

    def _val(key):
        return macro.get(key, {}).get("valor")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Selic (meta)", f"{_val('selic_meta_aa'):.2f}%" if _val("selic_meta_aa") else "—")
    m2.metric("CDI", f"{_val('cdi_aa'):.2f}%" if _val("cdi_aa") else "—")
    m3.metric("IPCA 12m", f"{_val('ipca_12m'):.2f}%" if _val("ipca_12m") else "—")
    m4.metric("Juro real", f"{_val('juro_real_aa'):.2f}%" if _val("juro_real_aa") else "—")
    m5.metric("Dólar PTAX", f"R$ {_val('dolar_ptax'):.2f}" if _val("dolar_ptax") else "—")

    jr = _val("juro_real_aa")
    if jr is not None:
        if jr >= 6:
            st.info(f"**Juro real de {jr:.1f}% a.a. é ALTO.** Renda fixa (Tesouro Selic/IPCA+, "
                    "CDB ≥100% CDI) compete forte com renda variável no risco-retorno. "
                    "A barra para a bolsa compensar está elevada.")
        elif jr >= 3:
            st.info(f"**Juro real de {jr:.1f}% a.a. é moderado** — equilíbrio entre classes.")
        else:
            st.info(f"**Juro real de {jr:.1f}% a.a. é baixo** — renda variável e ativos reais "
                    "tendem a ganhar atratividade relativa.")
    st.caption("Fonte: API SGS do Banco Central do Brasil. Leitura educativa, não recomendação.")


# ---------------- Renda Fixa ----------------
with tab_rf:
    st.subheader("Tesouro Direto (fonte oficial) + régua de ofertas")

    @st.cache_data(ttl=3600, show_spinner="Consultando Tesouro Direto...")
    def cached_tesouro():
        from src.renda_fixa import fetch_tesouro
        return fetch_tesouro()

    macro_rf = cached_macro()
    cdi_val = macro_rf.get("cdi_aa", {}).get("valor")
    cdi_aa = (cdi_val / 100) if cdi_val else cfg.get("cdi_anual", 0.105)

    try:
        titulos = cached_tesouro()
        df_td = pd.DataFrame([{
            "Título": t.nome, "Tipo": t.indexador,
            "Taxa de compra (% a.a.)": t.taxa_compra,
            "Vencimento": t.vencimento, "Mínimo (R$)": t.investimento_minimo,
        } for t in titulos])
        st.dataframe(df_td, use_container_width=True, hide_index=True)
        st.caption("Pós-fixados e IPCA+ pagam o indexador MAIS a taxa mostrada.")
    except Exception as exc:
        st.warning(f"API do Tesouro indisponível agora ({exc}). Tente atualizar em alguns minutos.")

    st.subheader(f"Régua de ofertas — CDI {cdi_aa*100:.2f}% a.a.")
    from src.renda_fixa import cdb_liquido_aa, lci_equivalente_pct_cdi
    anos_sel = st.radio("Prazo", [1, 2, 3], horizontal=True, format_func=lambda a: f"{a} ano(s)")
    df_regua = pd.DataFrame([{
        "Oferta": f"CDB {p}% CDI",
        "Líquido a.a. (após IR)": round(cdb_liquido_aa(p, cdi_aa, anos_sel), 2),
    } for p in (100, 105, 110, 115, 120, 130)] + [{
        "Oferta": f"LCI/LCA {p}% CDI (isenta)",
        "Líquido a.a. (após IR)": round(cdi_aa * 100 * p / 100, 2),
    } for p in (85, 90, 95)])
    st.dataframe(df_regua, use_container_width=True, hide_index=True)
    st.info("Recebeu uma oferta da corretora? Localize a linha equivalente: esse é o "
            "rendimento REAL no bolso. Compare com a taxa do Tesouro acima antes de decidir.")
    st.caption("IR regressivo: 22,5% (≤180d) · 20% (≤360d) · 17,5% (≤720d) · 15% (>720d). Educativo, não recomendação.")
