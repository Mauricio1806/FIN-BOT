"""FIN-BOT | Página única multimercado com abas (todos mercados no index.html)."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .trends import Analysis
from .insights import market_breadth, insights_text

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

_TREND_BADGE = {
    "ALTA_FORTE": ("ALTA FORTE", "#16a34a"),
    "ALTA": ("ALTA", "#4ade80"),
    "LATERAL": ("LATERAL", "#eab308"),
    "BAIXA": ("BAIXA", "#f87171"),
    "BAIXA_FORTE": ("BAIXA FORTE", "#dc2626"),
}

_CSS = """
:root{color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0b1020;
  color:#e2e8f0;padding:20px;max-width:1100px;margin:0 auto;line-height:1.55}
h1{font-size:1.6rem;margin-bottom:4px}
h2{font-size:1.1rem;margin:24px 0 12px;color:#93c5fd}
.sub{color:#64748b;font-size:.85rem;margin-bottom:16px}
.live{display:inline-flex;align-items:center;gap:6px;font-size:.75rem;color:#86efac;
  background:#14532d33;padding:3px 10px;border-radius:99px;margin-left:8px}
.live::before{content:"";width:8px;height:8px;background:#22c55e;border-radius:50%;
  animation:pulse 1.6s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:18px 0 20px;position:sticky;top:0;
  background:#0b1020;padding:10px 0;z-index:10;border-bottom:1px solid #1e2a4a}
.tab{padding:10px 18px;border-radius:99px;background:#111a33;border:1px solid #1e2a4a;
  color:#cbd5e1;font-size:.9rem;font-weight:600;cursor:pointer;transition:all .15s}
.tab:hover{border-color:#3b82f6;color:#fff}
.tab.active{background:#3b82f6;color:#fff;border-color:#3b82f6}
.market{display:none}.market.active{display:block;animation:fade .2s}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.card{background:#111a33;border:1px solid #1e2a4a;border-radius:12px;padding:12px 14px}
.card .l{font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:.04em}
.card .v{font-size:1.3rem;font-weight:700;margin-top:3px}
.regime{display:inline-block;padding:4px 14px;border-radius:99px;font-size:.78rem;font-weight:700;
  margin-bottom:14px}
.regime.EXPANSIVO{background:#14532d;color:#86efac}
.regime.MISTO{background:#713f12;color:#fde047}
.regime.DEFENSIVO{background:#7f1d1d;color:#fca5a5}
.insight{background:#111a33;border:1px solid #1e2a4a;border-left:3px solid #3b82f6;
  border-radius:10px;padding:11px 15px;margin-bottom:9px;font-size:.9rem}
.insight b{color:#fff}
table{width:100%;border-collapse:collapse;background:#111a33;border-radius:12px;overflow:hidden;
  font-size:.87rem;margin-bottom:8px}
th{background:#16213f;text-align:left;padding:9px 11px;font-size:.7rem;color:#94a3b8;
  text-transform:uppercase;letter-spacing:.04em}
td{padding:9px 11px;border-top:1px solid #1e2a4a}
tr:hover td{background:#16213f}
.badge{display:inline-block;padding:2px 9px;border-radius:99px;font-size:.68rem;font-weight:700;color:#0b1020}
.bar{background:#1e2a4a;border-radius:99px;height:7px;width:90px;display:inline-block;vertical-align:middle}
.bar i{display:block;height:7px;border-radius:99px}
.sig{background:#111a33;border:1px solid #1e2a4a;border-left:3px solid #eab308;
  border-radius:10px;padding:9px 13px;margin-bottom:7px;font-size:.86rem}
.right{text-align:right}.num{font-variant-numeric:tabular-nums}
.disc{margin-top:28px;color:#475569;font-size:.76rem;line-height:1.5}
@media(max-width:640px){body{padding:12px}td,th{padding:7px 6px;font-size:.76rem}
  .bar{width:55px}h1{font-size:1.3rem}.tab{padding:8px 14px;font-size:.82rem}}
"""

_JS = """
function showMarket(key,el){
  document.querySelectorAll('.market').forEach(m=>m.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('m-'+key).classList.add('active');
  el.classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
}
// auto-refresh a cada 5 min (a página em si é regenerada a cada 15 min pelo workflow)
setTimeout(()=>location.reload(),300000);
"""


def _score_color(s: float) -> str:
    return "#16a34a" if s>=65 else "#eab308" if s>=50 else "#f97316" if s>=35 else "#dc2626"


def _macro_block(macro: dict | None) -> str:
    if not macro:
        return ""
    def v(k, suf="%", pre=""):
        x = macro.get(k, {}).get("valor")
        return f"{pre}{x:.2f}{suf}" if x is not None else "—"
    return f"""
    <h2>🌎 Macro Brasil (Banco Central)</h2>
    <div class="cards">
      <div class="card"><div class="l">Selic</div><div class="v">{v('selic_meta_aa')}</div></div>
      <div class="card"><div class="l">CDI</div><div class="v">{v('cdi_aa')}</div></div>
      <div class="card"><div class="l">IPCA 12m</div><div class="v">{v('ipca_12m')}</div></div>
      <div class="card"><div class="l">Juro real</div><div class="v">{v('juro_real_aa')}</div></div>
      <div class="card"><div class="l">Dólar</div><div class="v">{v('dolar_ptax','','R$ ')}</div></div>
    </div>"""


def _market_section(key: str, conf: dict, analyses: list[Analysis], plan: dict | None,
                    macro: dict | None, active: bool) -> str:
    moeda = conf.get("moeda", "")
    breadth = market_breadth(analyses)
    macro_block = _macro_block(macro) if key == "brasil" else ""

    insights_html = ""
    if breadth:
        regime = breadth["regime"]
        cards = f"""<div class="cards">
          <div class="card"><div class="l">Score médio</div><div class="v">{breadth['score_medio']:.0f}</div></div>
          <div class="card"><div class="l">Em alta</div><div class="v">{breadth['em_alta']}/{breadth['n']}</div></div>
          <div class="card"><div class="l">Em baixa</div><div class="v">{breadth['em_baixa']}/{breadth['n']}</div></div>
          <div class="card"><div class="l">Laterais</div><div class="v">{breadth['laterais']}/{breadth['n']}</div></div>
        </div>"""
        bullets = "".join(f'<div class="insight">{i}</div>' for i in insights_text(analyses, breadth, macro if key=='brasil' else None, key))
        insights_html = f"""<h2>🧠 Leitura do mercado</h2>
          <span class="regime {regime}">{regime}</span>{cards}
          <div style="margin-top:14px">{bullets}</div>"""

    rows = ""
    for i, a in enumerate(analyses, 1):
        lbl, color = _TREND_BADGE.get(a.trend, (a.trend, "#64748b"))
        sc = _score_color(a.score)
        rows += f"""<tr><td>{i}</td><td><b>{a.ticker}</b></td>
        <td class="right num">{moeda} {a.price:,.2f}</td>
        <td><span class="badge" style="background:{color}">{lbl}</span></td>
        <td><span class="bar"><i style="width:{a.score}%;background:{sc}"></i></span>
            <b class="num"> {a.score}</b></td>
        <td class="right num">{a.rsi}</td>
        <td class="right num">{a.pct_from_high_52w}%</td></tr>"""

    sigs = "".join(f'<div class="sig"><b>{a.ticker}</b> — {s}</div>'
                   for a in analyses for s in a.signals) or \
           '<div class="sig">Nenhum sinal extremo agora.</div>'

    plan_html = ""
    if plan:
        prows = "".join(
            f"<tr><td><b>{t}</b></td><td class='right num'>{v['peso_%']}%</td>"
            f"<td class='right num'>{moeda} {v['valor']:,.2f}</td>"
            f"<td class='right num'>{v['qtd_aprox']}</td><td class='right num'>{v['score']}</td></tr>"
            for t, v in plan.items() if not t.startswith("_"))
        excl = plan.get("_excluidos_no_mes")
        excl_html = (f"<p class='sub' style='margin-top:8px'>Fora do mês: "
                     f"{', '.join(excl['tickers'])} — {excl['motivo']}</p>") if excl else ""
        plan_html = f"""<h2>💰 Sugestão de distribuição do aporte</h2>
        <table><tr><th>Ticker</th><th class="right">Peso</th><th class="right">Valor</th>
        <th class="right">Qtd aprox.</th><th class="right">Score</th></tr>{prows}</table>{excl_html}"""

    cls = "market active" if active else "market"
    return f"""<div id="m-{key}" class="{cls}">
    {macro_block}
    {insights_html}
    <h2>🏆 Ranking</h2>
    <table><tr><th>#</th><th>Ticker</th><th class="right">Preço</th><th>Tendência</th>
    <th>Score</th><th class="right">RSI</th><th class="right">vs Máx 52s</th></tr>{rows}</table>
    <h2>⚡ Sinais técnicos</h2>{sigs}
    {plan_html}
    </div>"""


def build_full_page(market_data: dict, macro: dict | None = None) -> str:
    """market_data = {key: (conf, analyses, plan), ...}  — Brasil primeiro = aba ativa."""
    now = datetime.now(ZoneInfo("America/Bahia")).strftime("%d/%m/%Y %H:%M")
    keys = list(market_data.keys())
    tabs = "".join(
        f'<button class="tab{" active" if i==0 else ""}" onclick="showMarket(\'{k}\',this)">{market_data[k][0]["label"]}</button>'
        for i, k in enumerate(keys)
    )
    sections = "".join(
        _market_section(k, market_data[k][0], market_data[k][1], market_data[k][2], macro, i==0)
        for i, k in enumerate(keys)
    )
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="900">
<title>FIN-BOT — Painel global</title><style>{_CSS}</style></head><body>
<h1>📈 FIN-BOT <span class="live">AO VIVO</span></h1>
<p class="sub">Atualizado em {now} (horário de Salvador) · próx. atualização em até 15 min</p>
<div class="tabs">{tabs}</div>
{sections}
<p class="disc">Score 0–100 = condição técnica relativa (40 pts tendência, 20 MACD, 20 RSI,
10 risco/ATR, 10 volume), calibrado para aportes de longo prazo. Página gerada por pipeline
automático a cada 15 min em horário de pregão — <b>não é recomendação de investimento</b>.
Fontes: Yahoo Finance, Banco Central do Brasil, Tesouro Direto. Rentabilidade passada não
garante resultados futuros.</p>
<script>{_JS}</script>
</body></html>"""


def save_html(content: str, filename: str = "index.html") -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path = DOCS_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path
