"""
FIN-BOT | Indicadores técnicos
Implementação pura em pandas (sem TA-Lib) — fácil de auditar e portar.
Todas as funções recebem o DataFrame OHLCV e retornam Series alinhadas ao índice.
"""
from __future__ import annotations

import pandas as pd


def sma(df: pd.DataFrame, window: int) -> pd.Series:
    return df["close"].rolling(window).mean()


def ema(df: pd.DataFrame, span: int) -> pd.Series:
    return df["close"].ewm(span=span, adjust=False).mean()


def rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """RSI de Wilder (suavização exponencial alpha=1/n)."""
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    rs = gain / loss.replace(0.0, float("nan"))
    out = 100 - (100 / (1 + rs))
    return out.fillna(100.0).rename("rsi")


def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9):
    """Retorna (linha_macd, linha_sinal, histograma)."""
    macd_line = ema(df, fast) - ema(df, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger(df: pd.DataFrame, window: int = 20, n_std: float = 2.0):
    """Retorna (banda_superior, média, banda_inferior, %B)."""
    mid = sma(df, window)
    std = df["close"].rolling(window).std()
    upper = mid + n_std * std
    lower = mid - n_std * std
    pct_b = (df["close"] - lower) / (upper - lower)
    return upper, mid, lower, pct_b


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Average True Range — proxy de volatilidade absoluta."""
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, adjust=False).mean().rename("atr")


def volume_ratio(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Volume atual / média de volume — >1.5 indica interesse anormal."""
    return (df["volume"] / df["volume"].rolling(window).mean()).rename("vol_ratio")


def drawdown_from_high(df: pd.DataFrame, lookback: int = 252) -> pd.Series:
    """Queda % em relação à máxima do período (52 semanas por padrão)."""
    rolling_max = df["close"].rolling(lookback, min_periods=1).max()
    return ((df["close"] / rolling_max) - 1).rename("drawdown")


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Anexa todos os indicadores ao DataFrame de preços."""
    out = df.copy()
    out["sma20"] = sma(df, 20)
    out["sma50"] = sma(df, 50)
    out["sma200"] = sma(df, 200)
    out["ema9"] = ema(df, 9)
    out["rsi14"] = rsi(df)
    out["macd"], out["macd_signal"], out["macd_hist"] = macd(df)
    out["bb_upper"], out["bb_mid"], out["bb_lower"], out["pct_b"] = bollinger(df)
    out["atr14"] = atr(df)
    out["atr_pct"] = out["atr14"] / out["close"]
    out["vol_ratio"] = volume_ratio(df)
    out["drawdown"] = drawdown_from_high(df)
    return out
