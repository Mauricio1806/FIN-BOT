"""
FIN-BOT | Gerador de relatório Markdown
Salva em reports/AAAA-MM-DD_report.md — o agente Claude Code lê este
arquivo para escrever a análise qualitativa por cima.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .trends import Analysis

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

_TREND_EMOJI = {
    "ALTA_FORTE": "🟢🟢",
    "ALTA": "🟢",
    "LATERAL": "🟡",
    "BAIXA": "🔴",
    "BAIXA_FORTE": "🔴🔴",
}


def build_report(analyses: list[Analysis], plan: dict | None = None) -> str:
    today = date.today().isoformat()
    lines = [
        f"# FIN-BOT — Relatório de Mercado ({today})",
        "",
        "> Gerado automaticamente. Score = condição técnica relativa (0–100).",
        "> Não é recomendação de investimento.",
        "",
        "## Ranking da watchlist",
        "",
        "| # | Ticker | Preço | Tendência | Score | RSI | MACD | vs Máx 52s | ATR% | Vol x |",
        "|---|--------|-------|-----------|-------|-----|------|-----------|------|-------|",
    ]
    for i, a in enumerate(analyses, 1):
        emoji = _TREND_EMOJI.get(a.trend, "")
        lines.append(
            f"| {i} | **{a.ticker}** | {a.price:,.2f} | {emoji} {a.trend} "
            f"| {a.score} | {a.rsi} | {a.macd_state} "
            f"| {a.pct_from_high_52w}% | {a.atr_pct}% | {a.vol_ratio} |"
        )

    lines += ["", "## Sinais relevantes", ""]
    any_signal = False
    for a in analyses:
        for s in a.signals:
            lines.append(f"- **{a.ticker}**: {s}")
            any_signal = True
    if not any_signal:
        lines.append("- Nenhum sinal extremo no momento.")

    if plan:
        lines += ["", "## Sugestão de distribuição do aporte", "",
                  "| Ticker | Peso | Valor | Qtd aprox. | Score |",
                  "|--------|------|-------|-----------|-------|"]
        for t, info in plan.items():
            if t.startswith("_"):
                continue
            lines.append(
                f"| {t} | {info['peso_%']}% | {info['valor']:,.2f} "
                f"| {info['qtd_aprox']} | {info['score']} |"
            )
        excl = plan.get("_excluidos_no_mes")
        if excl:
            lines += ["", f"**Fora do aporte este mês:** {', '.join(excl['tickers'])} — {excl['motivo']}"]

    return "\n".join(lines) + "\n"


def save_report(content: str) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{date.today().isoformat()}_report.md"
    path.write_text(content, encoding="utf-8")
    return path
