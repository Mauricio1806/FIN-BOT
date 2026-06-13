"""
FIN-BOT | Indicadores macro (API aberta do Banco Central — SGS)
Sem chave de API. Séries usadas:
  432  - Meta Selic (% a.a.)
  4389 - CDI anualizado (% a.a.)
  433  - IPCA mensal (%)
  13522- IPCA acumulado 12 meses (%)
  1    - Dólar PTAX venda

Isso responde a pergunta-chave do aporte: "renda fixa está pagando quanto
vs. o risco da bolsa?". Selic alta = Tesouro Selic/CDB competitivos;
juro real alto (Selic - IPCA) = renda fixa muito atrativa.
"""
from __future__ import annotations

import json
import urllib.request

SERIES = {
    "selic_meta_aa": 432,
    "cdi_aa": 4389,
    "ipca_mensal": 433,
    "ipca_12m": 13522,
    "dolar_ptax": 1,
}

_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados/ultimos/1?formato=json"


def _fetch_last(code: int) -> tuple[str, float]:
    req = urllib.request.Request(_URL.format(code=code), headers={"User-Agent": "fin-bot/2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    last = data[-1]
    return last["data"], float(last["valor"])


def get_macro() -> dict[str, dict]:
    """Retorna {nome: {data, valor}} + juro real calculado. Falhas viram None."""
    out: dict[str, dict] = {}
    for name, code in SERIES.items():
        try:
            d, v = _fetch_last(code)
            out[name] = {"data": d, "valor": v}
        except Exception as exc:  # noqa: BLE001
            out[name] = {"data": None, "valor": None, "erro": str(exc)}

    selic = out.get("selic_meta_aa", {}).get("valor")
    ipca12 = out.get("ipca_12m", {}).get("valor")
    if selic is not None and ipca12 is not None:
        juro_real = ((1 + selic / 100) / (1 + ipca12 / 100) - 1) * 100
        out["juro_real_aa"] = {"data": out["ipca_12m"]["data"], "valor": round(juro_real, 2)}
    return out


def format_macro(macro: dict) -> str:
    labels = {
        "selic_meta_aa": "Selic (meta)        ",
        "cdi_aa": "CDI                 ",
        "ipca_12m": "IPCA 12 meses       ",
        "ipca_mensal": "IPCA último mês     ",
        "juro_real_aa": "JURO REAL (Selic-IPCA)",
        "dolar_ptax": "Dólar PTAX          ",
    }
    lines = ["\n=== MACRO BRASIL (Banco Central) ==="]
    for key, label in labels.items():
        info = macro.get(key)
        if not info or info.get("valor") is None:
            lines.append(f"{label}  indisponível")
            continue
        unit = "" if key == "dolar_ptax" else "%"
        prefix = "R$ " if key == "dolar_ptax" else ""
        lines.append(f"{label}  {prefix}{info['valor']:.2f}{unit}  ({info['data']})")
    lines.append("")
    lines.append("Leitura rápida:")
    jr = macro.get("juro_real_aa", {}).get("valor")
    if jr is not None:
        if jr >= 6:
            lines.append(f"  • Juro real de {jr:.1f}% a.a. é ALTO — renda fixa (Tesouro IPCA+/Selic,")
            lines.append("    CDB ≥100% CDI) compete forte com renda variável no risco-retorno.")
        elif jr >= 3:
            lines.append(f"  • Juro real de {jr:.1f}% a.a. é moderado — equilíbrio entre classes.")
        else:
            lines.append(f"  • Juro real de {jr:.1f}% a.a. é baixo — renda variável e ativos reais")
            lines.append("    tendem a ficar relativamente mais atrativos.")
    return "\n".join(lines)
