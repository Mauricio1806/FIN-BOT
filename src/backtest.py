"""
FIN-BOT | Backtest de estratégia de aporte (DCA mensal)
Simula aportes mensais nos últimos N meses comparando:
  - tilt 0.0  -> pesos-alvo puros (buy & hold disciplinado)
  - tilt 0.5  -> híbrido (pesos-alvo + condição técnica)
  - tilt 1.0  -> técnico puro
  - CDI       -> benchmark de renda fixa (taxa do config.yaml)

Sem lookahead: o score de cada mês usa apenas dados até aquela data.
Compra a preço de fechamento do 1º pregão do mês. Não considera custos,
impostos nem dividendos — é comparação RELATIVA entre estratégias.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .screener import allocate
from .trends import analyze


@dataclass
class BacktestResult:
    label: str
    total_aportado: float
    valor_final: float
    retorno_pct: float
    max_drawdown_pct: float
    series: pd.Series  # valor da carteira ao longo do tempo


def _month_starts(index: pd.DatetimeIndex, months: int) -> list[pd.Timestamp]:
    """Primeiro pregão de cada um dos últimos `months` meses do índice."""
    df = pd.Series(1, index=index)
    firsts = df.groupby([index.year, index.month]).apply(lambda s: s.index.min())
    return sorted(firsts.tolist())[-months:]


def _portfolio_series(
    shares_log: list[tuple[pd.Timestamp, dict[str, float]]],
    closes: pd.DataFrame,
) -> pd.Series:
    """Valor diário da carteira dado o histórico de compras acumuladas."""
    values = pd.Series(0.0, index=closes.index)
    cumulative: dict[str, float] = {}
    log_iter = iter(shares_log)
    next_buy = next(log_iter, None)
    for d in closes.index:
        while next_buy is not None and next_buy[0] <= d:
            for t, q in next_buy[1].items():
                cumulative[t] = cumulative.get(t, 0.0) + q
            next_buy = next(log_iter, None)
        if cumulative:
            values[d] = sum(
                q * closes.at[d, t]
                for t, q in cumulative.items()
                if t in closes.columns and pd.notna(closes.at[d, t])
            )
    return values[values > 0]


def _max_drawdown(series: pd.Series, contributions: pd.Series) -> float:
    """Drawdown sobre o valor RELATIVO ao total aportado até cada data
    (evita confundir aporte novo com 'recuperação')."""
    ratio = series / contributions.reindex(series.index).ffill()
    peak = ratio.cummax()
    return float(((ratio / peak) - 1).min() * 100)


def run_backtest(
    price_data: dict[str, pd.DataFrame],
    amount: float = 1000.0,
    months: int = 24,
    target_weights: dict[str, float] | None = None,
    min_score: float = 35.0,
    cdi_anual: float = 0.105,
    tilts: tuple[float, ...] = (0.0, 0.5, 1.0),
) -> list[BacktestResult]:
    closes = pd.DataFrame({t: df["close"] for t, df in price_data.items()}).sort_index()
    closes = closes.ffill()
    dates = _month_starts(closes.index, months)
    if len(dates) < 3:
        raise ValueError("Histórico insuficiente para backtest — use period: '5y'")

    # série de total aportado (degraus)
    contributions = pd.Series(0.0, index=closes.index)
    for i, d in enumerate(dates, 1):
        contributions[contributions.index >= d] = i * amount
    total = len(dates) * amount

    results: list[BacktestResult] = []

    for tilt in tilts:
        shares_log: list[tuple[pd.Timestamp, dict[str, float]]] = []
        for d in dates:
            analyses = []
            for t, df in price_data.items():
                hist = df.loc[:d]
                if len(hist) < 60:
                    continue
                try:
                    analyses.append(analyze(t, hist))
                except ValueError:
                    continue
            if not analyses:
                continue
            plan = allocate(analyses, amount, target_weights, tilt=tilt, min_score=min_score)
            buys = {
                t: info["valor"] / closes.at[d, t]
                for t, info in plan.items()
                if not t.startswith("_") and pd.notna(closes.at[d, t])
            }
            shares_log.append((d, buys))

        series = _portfolio_series(shares_log, closes.loc[dates[0]:])
        final = float(series.iloc[-1])
        label = {0.0: "Pesos-alvo (tilt 0.0)", 0.5: "Híbrido (tilt 0.5)",
                 1.0: "Técnico (tilt 1.0)"}.get(tilt, f"tilt {tilt}")
        results.append(BacktestResult(
            label=label,
            total_aportado=total,
            valor_final=round(final, 2),
            retorno_pct=round((final / total - 1) * 100, 2),
            max_drawdown_pct=round(_max_drawdown(series, contributions), 2),
            series=series,
        ))

    # benchmark CDI: cada aporte rende a taxa composta até o fim
    cdi_m = (1 + cdi_anual) ** (1 / 12) - 1
    n = len(dates)
    cdi_final = sum(amount * (1 + cdi_m) ** (n - i) for i in range(n))
    cdi_series = pd.Series(
        [sum(amount * (1 + cdi_m) ** (k - i) for i in range(min(k + 1, n)))
         for k in range(n)],
        index=dates,
    )
    results.append(BacktestResult(
        label=f"CDI {cdi_anual:.1%} a.a.",
        total_aportado=total,
        valor_final=round(cdi_final, 2),
        retorno_pct=round((cdi_final / total - 1) * 100, 2),
        max_drawdown_pct=0.0,
        series=cdi_series,
    ))

    results.sort(key=lambda r: r.valor_final, reverse=True)
    return results
