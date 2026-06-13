"""
FIN-BOT | Camada de insights técnicos
Lê as Analyses e gera leituras agregadas + recomendações de monitoramento.
"""
from __future__ import annotations
from collections import Counter
from .trends import Analysis


def market_breadth(analyses: list[Analysis]) -> dict:
    """Saúde do mercado: % em alta, score médio, dispersão."""
    n = len(analyses)
    if not n:
        return {}
    trends = Counter(a.trend for a in analyses)
    em_alta = trends.get("ALTA", 0) + trends.get("ALTA_FORTE", 0)
    em_baixa = trends.get("BAIXA", 0) + trends.get("BAIXA_FORTE", 0)
    scores = [a.score for a in analyses]
    breadth_pct = em_alta / n * 100
    return {
        "n": n,
        "em_alta": em_alta,
        "em_baixa": em_baixa,
        "laterais": trends.get("LATERAL", 0),
        "breadth_pct": breadth_pct,
        "score_medio": sum(scores) / n,
        "score_max": max(scores),
        "score_min": min(scores),
        "regime": (
            "EXPANSIVO" if breadth_pct >= 60
            else "MISTO" if breadth_pct >= 35
            else "DEFENSIVO"
        ),
    }


def insights_text(analyses: list[Analysis], breadth: dict) -> list[str]:
    """Gera bullets de leitura do mercado a partir dos dados."""
    out = []
    regime = breadth.get("regime", "")
    pct = breadth.get("breadth_pct", 0)

    if regime == "EXPANSIVO":
        out.append(f"📈 <b>Mercado expansivo</b>: {pct:.0f}% dos ativos em tendência de alta. "
                   "Cenário favorável para aportes em renda variável; foco em qualidade, não em barganha.")
    elif regime == "MISTO":
        out.append(f"⚖️ <b>Mercado misto</b>: {pct:.0f}% em alta, {breadth['em_baixa']} em baixa, "
                   f"{breadth['laterais']} laterais. Seletividade importa mais que timing.")
    else:
        out.append(f"🛡️ <b>Mercado defensivo</b>: apenas {pct:.0f}% em alta. "
                   "Aporte cauteloso, priorize ativos com score alto e tendência clara; "
                   "considere fortalecer caixa/renda fixa neste mês.")

    sobrevendidos = [a for a in analyses if a.rsi < 35 and a.trend not in ("BAIXA_FORTE",)]
    if sobrevendidos:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in sobrevendidos[:3])
        out.append(f"🎯 <b>Sobrevendidos em tendência sustentada</b>: {nomes}. "
                   "Recuo técnico em ativos saudáveis costuma ser ponto de entrada interessante "
                   "para quem aporta. Confirmar com volume e MACD.")

    sobrecomprados = [a for a in analyses if a.rsi > 70]
    if sobrecomprados:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in sobrecomprados[:3])
        out.append(f"⚠️ <b>Sobrecomprados (RSI > 70)</b>: {nomes}. "
                   "Aportar agora é pagar caro; reduzir peso destes neste mês ou aguardar recuo.")

    cross_alta = [a for a in analyses if "GOLDEN CROSS" in " ".join(a.signals)]
    cross_baixa = [a for a in analyses if "DEATH CROSS" in " ".join(a.signals)]
    if cross_alta:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in cross_alta[:3])
        out.append(f"🟢 <b>Golden Cross recente</b>: {nomes}. "
                   "Sinal clássico de virada estrutural — historicamente precede períodos de alta.")
    if cross_baixa:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in cross_baixa[:3])
        out.append(f"🔴 <b>Death Cross recente</b>: {nomes}. "
                   "Sinal de virada estrutural negativa — exigir cautela ou reduzir exposição.")

    volume_anomalo = [a for a in analyses if a.vol_ratio > 1.8]
    if volume_anomalo:
        nomes = ", ".join(f"<b>{a.ticker}</b> ({a.vol_ratio:.1f}x)" for a in volume_anomalo[:3])
        out.append(f"🔊 <b>Volume anormal</b>: {nomes}. "
                   "Movimento com convicção institucional — monitorar a notícia/fato relevante por trás.")

    descontos = [a for a in analyses if a.pct_from_high_52w < -25 and a.score >= 50]
    if descontos:
        nomes = ", ".join(f"<b>{a.ticker}</b> ({a.pct_from_high_52w:.0f}%)" for a in descontos[:3])
        out.append(f"💎 <b>Descontados vs máxima de 52 semanas</b>: {nomes}. "
                   "Score técnico ainda saudável apesar do recuo — candidatos a aporte por valor relativo.")

    top3 = sorted(analyses, key=lambda x: x.score, reverse=True)[:3]
    out.append(f"🏆 <b>Top 3 por condição técnica</b>: "
               + ", ".join(f"<b>{a.ticker}</b> (score {a.score})" for a in top3)
               + ". Não significa 'comprar agora' — significa que a estrutura técnica está mais saudável "
                 "que a média dos pares neste momento.")

    bottom3 = sorted(analyses, key=lambda x: x.score)[:3]
    out.append(f"🐌 <b>Piores condições técnicas</b>: "
               + ", ".join(f"<b>{a.ticker}</b> (score {a.score})" for a in bottom3)
               + ". Reavaliar tese fundamentalista ou reduzir peso neste mês.")

    return out
