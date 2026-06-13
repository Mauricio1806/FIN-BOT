#!/usr/bin/env python3
"""
FIN-BOT — CLI de análise de mercado e apoio a aportes.

Uso:
  python finbot.py analyze PETR4.SA              # análise profunda de 1 ativo
  python finbot.py screen                        # ranqueia toda a watchlist
  python finbot.py aporte 2000                   # sugere distribuição de R$2000
  python finbot.py aporte 2000 --tilt 0.7        # mais peso na condição técnica
  python finbot.py report                        # screen + aporte + salva .md
  python finbot.py screen --force                # ignora cache de 12h
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from src.screener import allocate, screen
from src.report import build_report, save_report
from src.data import fetch_history
from src.trends import analyze
from src.backtest import run_backtest
from src.macro import get_macro, format_macro
from src.renda_fixa import fetch_tesouro, format_tesouro, regua_ofertas
from src.html_report import build_full_page, save_html

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_analyze(args, cfg):
    df = fetch_history(args.ticker, period=cfg.get("period", "2y"), force=args.force)
    a = analyze(args.ticker, df)
    print(f"\n=== {a.ticker} ===")
    print(f"Preço:            {a.price:,.2f}")
    print(f"Tendência:        {a.trend}")
    print(f"Score técnico:    {a.score}/100")
    print(f"RSI(14):          {a.rsi}")
    print(f"MACD:             {a.macd_state}")
    print(f"vs máx. 52 sem.:  {a.pct_from_high_52w}%")
    print(f"Volatilidade ATR: {a.atr_pct}% ao dia")
    print(f"Volume ratio:     {a.vol_ratio}x")
    if a.signals:
        print("\nSinais:")
        for s in a.signals:
            print(f"  • {s}")
    print()


def cmd_screen(args, cfg):
    results = screen(cfg.get("watchlist") or cfg.get("markets", {}).get("brasil", {}).get("watchlist", []), period=cfg.get("period", "2y"), force=args.force)
    print(f"\n{'#':<3}{'TICKER':<12}{'PREÇO':>10}  {'TENDÊNCIA':<12}{'SCORE':>6}{'RSI':>6}")
    print("-" * 52)
    for i, a in enumerate(results, 1):
        print(f"{i:<3}{a.ticker:<12}{a.price:>10,.2f}  {a.trend:<12}{a.score:>6}{a.rsi:>6}")
    print()
    return results


def cmd_aporte(args, cfg):
    results = screen(cfg.get("watchlist") or cfg.get("markets", {}).get("brasil", {}).get("watchlist", []), period=cfg.get("period", "2y"), force=args.force)
    plan = allocate(
        results,
        amount=args.valor,
        target_weights=cfg.get("target_weights") or cfg.get("markets", {}).get("brasil", {}).get("target_weights"),
        tilt=args.tilt,
        min_score=cfg.get("min_score", 35),
    )
    print(f"\nDistribuição sugerida para {args.valor:,.2f} (tilt={args.tilt}):\n")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    print("\n⚠ Sugestão matemática para apoiar SUA decisão — não é recomendação.")
    return results, plan


def cmd_report(args, cfg):
    results = screen(cfg.get("watchlist") or cfg.get("markets", {}).get("brasil", {}).get("watchlist", []), period=cfg.get("period", "2y"), force=args.force)
    plan = None
    if args.valor:
        plan = allocate(
            results,
            amount=args.valor,
            target_weights=cfg.get("target_weights") or cfg.get("markets", {}).get("brasil", {}).get("target_weights"),
            tilt=args.tilt,
            min_score=cfg.get("min_score", 35),
        )
    path = save_report(build_report(results, plan))
    print(f"Relatório salvo em: {path}")


def cmd_backtest(args, cfg):
    print(f"Baixando histórico de {len(cfg['watchlist'])} ativos (period={cfg.get('backtest_period', '5y')})...")
    price_data = {}
    for t in cfg.get("watchlist") or cfg.get("markets", {}).get("brasil", {}).get("watchlist", []):
        try:
            price_data[t] = fetch_history(t, period=cfg.get("backtest_period", "5y"), force=args.force)
        except Exception as exc:
            print(f"[aviso] {t}: {exc}")
    results = run_backtest(
        price_data,
        amount=args.valor,
        months=args.meses,
        target_weights=cfg.get("target_weights") or cfg.get("markets", {}).get("brasil", {}).get("target_weights"),
        min_score=cfg.get("min_score", 35),
        cdi_anual=cfg.get("cdi_anual", 0.105),
    )
    total = results[0].total_aportado
    print(f"\n=== BACKTEST: aporte de {args.valor:,.2f}/mês por {args.meses} meses "
          f"(total {total:,.2f}) ===\n")
    print(f"{'ESTRATÉGIA':<26}{'VALOR FINAL':>14}{'RETORNO':>10}{'MAX DD':>9}")
    print("-" * 59)
    for r in results:
        print(f"{r.label:<26}{r.valor_final:>14,.2f}{r.retorno_pct:>9.2f}%{r.max_drawdown_pct:>8.1f}%")
    print("\nNotas: sem custos, impostos ou dividendos — comparação RELATIVA entre")
    print("estratégias. Passado não garante futuro. Max DD = queda máxima vs. aportado.")


def cmd_macro(args, cfg):
    print(format_macro(get_macro()))


def cmd_ofertas(args, cfg):
    macro = get_macro()
    cdi = macro.get("cdi_aa", {}).get("valor")
    cdi_aa = (cdi / 100) if cdi else cfg.get("cdi_anual", 0.105)
    try:
        titulos = fetch_tesouro()
        print(format_tesouro(titulos))
    except Exception as exc:
        print(f"[aviso] API do Tesouro Direto indisponível agora: {exc}")
        print("Tente novamente em alguns minutos — a API oficial oscila fora do horário de pregão.")
    print(regua_ofertas(cdi_aa))
    print("\n⚠ Dados oficiais + matemática de IR. Não é recomendação de investimento.")


def cmd_html(args, cfg):
    """Gera uma página HTML por mercado em docs/. Brasil vira docs/index.html."""
    try:
        macro = get_macro()
    except Exception as exc:
        print(f"[aviso] macro indisponível: {exc}")
        macro = None
    markets = cfg.get("markets", {})
    if not markets:  # fallback compat. com config antigo
        markets = {"brasil": {"label": "🇧🇷 Brasil", "moeda": "R$",
                              "watchlist": cfg.get("watchlist", []),
                              "target_weights": cfg.get("target_weights") or cfg.get("markets", {}).get("brasil", {}).get("target_weights")}}
    valor = args.valor if args.valor else cfg.get("aporte_mensal")
    for key, conf in markets.items():
        print(f"\n--- Mercado: {conf['label']} ---")
        try:
            results = screen(conf["watchlist"], period=cfg.get("period", "2y"), force=args.force)
        except Exception as exc:
            print(f"[erro] {key}: {exc}")
            continue
        plan = None
        if valor and conf.get("target_weights"):
            plan = allocate(results, amount=valor, target_weights=conf.get("target_weights"),
                            tilt=args.tilt, min_score=cfg.get("min_score", 35))
        html = build_html(key, conf, results, macro, plan, markets)
        filename = _MARKET_FILES.get(key, f"{key}.html")
        path = save_html(html, filename)
        print(f"  ✅ {path}")


def main():
    p = argparse.ArgumentParser(description="FIN-BOT — análise de mercado")
    p.add_argument("--force", action="store_true", help="ignora o cache de 12h")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("analyze", help="análise profunda de um ticker")
    pa.add_argument("ticker")

    sub.add_parser("screen", help="ranqueia a watchlist por score")

    pp = sub.add_parser("aporte", help="sugere distribuição de um aporte")
    pp.add_argument("valor", type=float)
    pp.add_argument("--tilt", type=float, default=0.5,
                    help="0=só pesos-alvo, 1=só condição técnica (default 0.5)")

    pr = sub.add_parser("report", help="gera relatório markdown em reports/")
    pr.add_argument("--valor", type=float, default=None)
    pr.add_argument("--tilt", type=float, default=0.5)

    pb = sub.add_parser("backtest", help="simula aportes mensais: estratégias vs CDI")
    pb.add_argument("valor", type=float, help="valor do aporte mensal simulado")
    pb.add_argument("--meses", type=int, default=24)

    sub.add_parser("macro", help="Selic, CDI, IPCA, juro real e dólar (Banco Central)")

    sub.add_parser("ofertas", help="taxas oficiais do Tesouro Direto + régua de CDB/LCI")

    ph = sub.add_parser("html", help="gera docs/index.html (página do GitHub Pages)")
    ph.add_argument("--valor", type=float, default=None)
    ph.add_argument("--tilt", type=float, default=0.5)

    args = p.parse_args()
    cfg = load_config()

    {"analyze": cmd_analyze, "screen": cmd_screen,
     "aporte": cmd_aporte, "report": cmd_report,
     "backtest": cmd_backtest, "macro": cmd_macro,
     "ofertas": cmd_ofertas, "html": cmd_html}[args.cmd](args, cfg)


if __name__ == "__main__":
    sys.exit(main())
