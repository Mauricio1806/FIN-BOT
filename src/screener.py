"""
FIN-BOT | Screener + Alocador de aporte
- screen(): roda a análise em toda a watchlist e ranqueia por score.
- allocate(): distribui um valor de aporte mensal entre os ativos,
  combinando pesos-alvo (config.yaml) com o score técnico do momento.

A alocação é uma SUGESTÃO MATEMÁTICA para apoiar sua análise,
não recomendação de investimento.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .data import fetch_history
from .trends import Analysis, analyze


def screen(tickers: list[str], period: str = "2y", force: bool = False) -> list[Analysis]:
    results: list[Analysis] = []
    errors: list[str] = []

    def _one(t: str):
        df = fetch_history(t, period=period, force=force)
        return analyze(t, df)

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_one, t): t for t in tickers}
        for fut in as_completed(futures):
            t = futures[fut]
            try:
                results.append(fut.result())
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{t}: {exc}")

    results.sort(key=lambda a: a.score, reverse=True)
    for err in errors:
        print(f"[aviso] {err}")
    return results


def allocate(
    analyses: list[Analysis],
    amount: float,
    target_weights: dict[str, float] | None = None,
    tilt: float = 0.5,
    min_score: float = 35.0,
) -> dict[str, dict]:
    """
    Divide `amount` entre os ativos analisados.

    peso_final = (1 - tilt) * peso_alvo + tilt * peso_por_score
    - tilt=0.0 -> ignora score, segue só os pesos-alvo (puro buy & hold)
    - tilt=1.0 -> ignora pesos-alvo, segue só a condição técnica
    - Ativos com score < min_score são excluídos do aporte do mês
      (o peso deles é redistribuído proporcionalmente).
    """
    eligible = [a for a in analyses if a.score >= min_score]
    if not eligible:
        return {}

    if target_weights:
        tw = {a.ticker: target_weights.get(a.ticker, 0.0) for a in eligible}
    else:
        tw = {a.ticker: 1.0 for a in eligible}
    tw_sum = sum(tw.values()) or 1.0
    tw = {k: v / tw_sum for k, v in tw.items()}

    score_sum = sum(a.score for a in eligible)
    sw = {a.ticker: a.score / score_sum for a in eligible}

    blended = {t: (1 - tilt) * tw[t] + tilt * sw[t] for t in tw}
    b_sum = sum(blended.values())
    blended = {k: v / b_sum for k, v in blended.items()}

    by_ticker = {a.ticker: a for a in eligible}
    plan: dict[str, dict] = {}
    for t, w in sorted(blended.items(), key=lambda kv: kv[1], reverse=True):
        a = by_ticker[t]
        value = round(amount * w, 2)
        plan[t] = {
            "peso_%": round(w * 100, 1),
            "valor": value,
            "qtd_aprox": round(value / a.price, 2) if a.price else 0,
            "preco": round(a.price, 2),
            "score": a.score,
            "tendencia": a.trend,
        }

    skipped = [a.ticker for a in analyses if a.score < min_score]
    if skipped:
        plan["_excluidos_no_mes"] = {
            "tickers": skipped,
            "motivo": f"score < {min_score} (condição técnica fraca)",
        }
    return plan
