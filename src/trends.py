"""
FIN-BOT | Análise de tendência e score composto
Classifica regime de mercado e gera um score 0-100 por ativo.

O score NÃO é recomendação de compra/venda — é um ranking relativo de
"condição técnica" para apoiar SUA decisão de aporte.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .indicators import enrich


@dataclass
class Analysis:
    ticker: str
    price: float
    trend: str                 # ALTA_FORTE | ALTA | LATERAL | BAIXA | BAIXA_FORTE
    score: float               # 0-100
    rsi: float
    macd_state: str            # cruzamento_alta | positivo | cruzamento_baixa | negativo
    pct_from_high_52w: float   # drawdown vs máxima 52s (negativo = abaixo da máxima)
    atr_pct: float             # volatilidade diária típica em % do preço
    vol_ratio: float
    signals: list[str] = field(default_factory=list)


def _classify_trend(last: pd.Series) -> tuple[str, float]:
    """Regime via empilhamento de médias + posição do preço. Retorna (label, pontos 0-40)."""
    price, s20, s50, s200 = last["close"], last["sma20"], last["sma50"], last["sma200"]

    if pd.isna(s200):  # histórico curto: usa só 20/50
        if price > s20 > s50:
            return "ALTA", 28.0
        if price < s20 < s50:
            return "BAIXA", 12.0
        return "LATERAL", 20.0

    if price > s20 > s50 > s200:
        return "ALTA_FORTE", 40.0
    if price > s50 > s200:
        return "ALTA", 32.0
    if price < s20 < s50 < s200:
        return "BAIXA_FORTE", 0.0
    if price < s50 < s200:
        return "BAIXA", 8.0
    return "LATERAL", 20.0


def _macd_state(df: pd.DataFrame) -> tuple[str, float]:
    """Estado do MACD + pontos (0-20)."""
    h_now, h_prev = df["macd_hist"].iloc[-1], df["macd_hist"].iloc[-2]
    if h_prev <= 0 < h_now:
        return "cruzamento_alta", 20.0
    if h_prev >= 0 > h_now:
        return "cruzamento_baixa", 2.0
    if h_now > 0:
        return "positivo", 14.0
    return "negativo", 6.0


def _rsi_points(rsi_val: float) -> float:
    """0-20 pontos. Para ESTRATÉGIA DE APORTE, RSI baixo em tendência ok = oportunidade."""
    if rsi_val < 30:
        return 16.0   # sobrevendido — possível ponto de entrada (confirmar tendência)
    if rsi_val < 45:
        return 18.0   # zona saudável de recuo
    if rsi_val < 60:
        return 14.0   # neutro
    if rsi_val < 70:
        return 10.0   # esticado
    return 4.0        # sobrecomprado — aporte tende a pagar caro


def _risk_points(atr_pct: float) -> float:
    """0-10 pontos. Penaliza volatilidade extrema (proteção do aporte)."""
    if atr_pct < 0.015:
        return 10.0
    if atr_pct < 0.025:
        return 8.0
    if atr_pct < 0.04:
        return 5.0
    return 2.0


def _volume_points(vol_ratio: float, trend: str) -> float:
    """0-10 pontos. Volume alto confirma alta; volume alto em queda é alerta."""
    if pd.isna(vol_ratio):
        return 5.0
    bullish = trend in ("ALTA", "ALTA_FORTE")
    if vol_ratio > 1.5:
        return 10.0 if bullish else 2.0
    if vol_ratio > 0.8:
        return 7.0
    return 4.0


def analyze(ticker: str, df: pd.DataFrame) -> Analysis:
    e = enrich(df).dropna(subset=["sma50", "rsi14", "macd_hist"])
    if len(e) < 5:
        raise ValueError(f"{ticker}: histórico insuficiente para análise")

    last = e.iloc[-1]
    trend, trend_pts = _classify_trend(last)
    macd_st, macd_pts = _macd_state(e)
    rsi_val = float(last["rsi14"])
    atr_pct = float(last["atr_pct"])
    vol_r = float(last["vol_ratio"]) if pd.notna(last["vol_ratio"]) else float("nan")

    score = (
        trend_pts
        + macd_pts
        + _rsi_points(rsi_val)
        + _risk_points(atr_pct)
        + _volume_points(vol_r, trend)
    )

    signals: list[str] = []
    if macd_st == "cruzamento_alta":
        signals.append("MACD cruzou para cima (momentum virando)")
    if macd_st == "cruzamento_baixa":
        signals.append("MACD cruzou para baixo (momentum enfraquecendo)")
    if rsi_val < 30:
        signals.append(f"RSI {rsi_val:.0f} — sobrevendido")
    if rsi_val > 70:
        signals.append(f"RSI {rsi_val:.0f} — sobrecomprado")
    if last["pct_b"] < 0.05:
        signals.append("Preço colado na banda inferior de Bollinger")
    if last["pct_b"] > 0.95:
        signals.append("Preço colado na banda superior de Bollinger")
    if pd.notna(last["sma200"]):
        s50_prev = e["sma50"].iloc[-6]
        s200_prev = e["sma200"].iloc[-6]
        if s50_prev <= s200_prev and last["sma50"] > last["sma200"]:
            signals.append("GOLDEN CROSS recente (SMA50 cruzou SMA200 p/ cima)")
        if s50_prev >= s200_prev and last["sma50"] < last["sma200"]:
            signals.append("DEATH CROSS recente (SMA50 cruzou SMA200 p/ baixo)")
    if last["drawdown"] < -0.20 and trend not in ("BAIXA", "BAIXA_FORTE"):
        signals.append(f"{last['drawdown']:.0%} abaixo da máx. 52s, mas tendência se sustenta")
    if not pd.isna(vol_r) and vol_r > 2.0:
        signals.append(f"Volume {vol_r:.1f}x acima da média — movimento com convicção")

    return Analysis(
        ticker=ticker,
        price=float(last["close"]),
        trend=trend,
        score=round(score, 1),
        rsi=round(rsi_val, 1),
        macd_state=macd_st,
        pct_from_high_52w=round(float(last["drawdown"]) * 100, 1),
        atr_pct=round(atr_pct * 100, 2),
        vol_ratio=round(vol_r, 2) if pd.notna(last["vol_ratio"]) else 0.0,
        signals=signals,
    )
