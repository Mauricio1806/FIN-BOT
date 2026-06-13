"""Testes offline com dados sintéticos — valida indicadores, score e alocação sem rede."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from src.indicators import enrich, rsi
from src.trends import analyze
from src.screener import allocate


def synthetic(trend="up", n=400, seed=42):
    rng = np.random.default_rng(seed)
    drift = {"up": 0.0008, "down": -0.0008, "flat": 0.0}[trend]
    rets = rng.normal(drift, 0.012, n)
    close = 100 * np.exp(np.cumsum(rets))
    dates = pd.bdate_range(end="2026-06-10", periods=n)
    df = pd.DataFrame({
        "open": close * (1 + rng.normal(0, 0.002, n)),
        "high": close * (1 + abs(rng.normal(0, 0.006, n))),
        "low": close * (1 - abs(rng.normal(0, 0.006, n))),
        "close": close,
        "volume": rng.integers(1e6, 5e6, n).astype(float),
    }, index=dates)
    return df


def main():
    up, down, flat = synthetic("up"), synthetic("down", seed=7), synthetic("flat", seed=3)

    # 1. indicadores não explodem e RSI fica em [0, 100]
    e = enrich(up)
    r = rsi(up).dropna()
    assert r.between(0, 100).all(), "RSI fora de [0,100]"
    assert not e[["sma20", "macd", "atr14"]].iloc[-1].isna().any()

    # 2. tendência de alta pontua mais que tendência de baixa
    a_up = analyze("UP.TEST", up)
    a_down = analyze("DOWN.TEST", down)
    a_flat = analyze("FLAT.TEST", flat)
    assert a_up.score > a_down.score, f"score alta ({a_up.score}) <= baixa ({a_down.score})"
    assert a_up.trend in ("ALTA", "ALTA_FORTE")
    assert a_down.trend in ("BAIXA", "BAIXA_FORTE")

    # 3. alocação soma o valor e exclui score fraco
    plan = allocate([a_up, a_flat, a_down], amount=1000, tilt=0.5, min_score=35)
    total = sum(v["valor"] for k, v in plan.items() if not k.startswith("_"))
    assert abs(total - 1000) < 1.0, f"alocação não soma 1000: {total}"

    # 4. tilt=0 com pesos-alvo iguais => pesos iguais
    plan_eq = allocate([a_up, a_flat], amount=1000, target_weights=None, tilt=0.0, min_score=0)
    pesos = [v["peso_%"] for k, v in plan_eq.items() if not k.startswith("_")]
    assert all(abs(p - 50.0) < 0.2 for p in pesos), pesos

    print("✅ Todos os testes offline passaram")
    print(f"   UP:   trend={a_up.trend:<11} score={a_up.score}")
    print(f"   FLAT: trend={a_flat.trend:<11} score={a_flat.score}")
    print(f"   DOWN: trend={a_down.trend:<11} score={a_down.score}")
    print(f"   Plano de aporte (1000): { {k: v['valor'] for k, v in plan.items() if not k.startswith('_')} }")




def test_backtest():
    from src.backtest import run_backtest

    data = {
        "UP.T": synthetic("up", n=900, seed=42),
        "DOWN.T": synthetic("down", n=900, seed=7),
        "FLAT.T": synthetic("flat", n=900, seed=3),
    }
    results = run_backtest(data, amount=1000, months=12, cdi_anual=0.105,
                           target_weights={"UP.T": 0.4, "DOWN.T": 0.3, "FLAT.T": 0.3})
    labels = [r.label for r in results]
    assert len(results) == 4, labels  # 3 tilts + CDI
    for r in results:
        assert abs(r.total_aportado - 12000) < 0.01, r
        assert r.valor_final > 0, r
        assert r.max_drawdown_pct <= 0.01, r  # drawdown nunca positivo
    # CDI a 10.5% por ~1 ano sobre aportes parcelados: retorno entre 4% e 7%
    cdi = next(r for r in results if "CDI" in r.label)
    assert 3 < cdi.retorno_pct < 8, cdi.retorno_pct
    print("✅ Backtest ok:")
    for r in results:
        print(f"   {r.label:<26} final={r.valor_final:>10,.2f}  ret={r.retorno_pct:>6.2f}%  dd={r.max_drawdown_pct:>6.1f}%")


if __name__ == "__main__":
    main()
    test_backtest()
