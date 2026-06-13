"""
FIN-BOT | Camada de dados
Busca OHLCV via yfinance com cache local em SQLite (evita rate-limit do Yahoo).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finbot.db"
CACHE_HOURS = 12  # re-busca se o cache for mais velho que isso


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS prices (
            ticker TEXT, date TEXT, open REAL, high REAL, low REAL,
            close REAL, volume REAL,
            PRIMARY KEY (ticker, date)
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS fetch_log (
            ticker TEXT PRIMARY KEY, fetched_at TEXT
        )"""
    )
    return conn


def _cache_fresh(conn: sqlite3.Connection, ticker: str) -> bool:
    row = conn.execute(
        "SELECT fetched_at FROM fetch_log WHERE ticker = ?", (ticker,)
    ).fetchone()
    if not row:
        return False
    fetched = datetime.fromisoformat(row[0])
    return datetime.now() - fetched < timedelta(hours=CACHE_HOURS)


def _load_cache(conn: sqlite3.Connection, ticker: str) -> pd.DataFrame:
    df = pd.read_sql(
        "SELECT date, open, high, low, close, volume FROM prices "
        "WHERE ticker = ? ORDER BY date",
        conn,
        params=(ticker,),
        parse_dates=["date"],
    )
    return df.set_index("date") if not df.empty else df


def _save_cache(conn: sqlite3.Connection, ticker: str, df: pd.DataFrame) -> None:
    conn.execute("DELETE FROM prices WHERE ticker = ?", (ticker,))
    rows = [
        (
            ticker,
            idx.strftime("%Y-%m-%d"),
            float(row["open"]),
            float(row["high"]),
            float(row["low"]),
            float(row["close"]),
            float(row["volume"]),
        )
        for idx, row in df.iterrows()
    ]
    conn.executemany("INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?)", rows)
    conn.execute(
        "INSERT OR REPLACE INTO fetch_log VALUES (?, ?)",
        (ticker, datetime.now().isoformat()),
    )
    conn.commit()


def fetch_history(ticker: str, period: str = "2y", force: bool = False) -> pd.DataFrame:
    """Retorna DataFrame OHLCV (index=date, colunas: open/high/low/close/volume)."""
    conn = _conn()
    try:
        if not force and _cache_fresh(conn, ticker):
            cached = _load_cache(conn, ticker)
            if not cached.empty:
                return cached

        import yfinance as yf  # import tardio: permite rodar testes offline

        raw = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        if raw.empty:
            raise ValueError(f"Sem dados para {ticker} (ticker correto? B3 usa sufixo .SA)")

        df = raw.rename(
            columns={"Open": "open", "High": "high", "Low": "low",
                     "Close": "close", "Volume": "volume"}
        )[["open", "high", "low", "close", "volume"]]
        df.index = pd.to_datetime(df.index).tz_localize(None)
        _save_cache(conn, ticker, df)
        return df
    finally:
        conn.close()
