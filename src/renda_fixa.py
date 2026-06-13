"""
FIN-BOT | Renda fixa — coletor do Tesouro Direto + comparador de ofertas
Fonte: API oficial do Tesouro Direto (B3). Ela bloqueia requisições que não
parecem navegador, então usamos curl_cffi com impersonação de Chrome
(já instalado como dependência do yfinance).

Além das taxas oficiais, gera a "RÉGUA DE OFERTAS": tabela de rendimento
LÍQUIDO de CDBs (% do CDI, com IR regressivo) e equivalência LCI/LCA
(isentas) — para você julgar em segundos qualquer oferta da sua corretora.

Educativo, não é recomendação de investimento.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

TESOURO_URL = (
    "https://www.tesourodireto.com.br/json/br/com/b3/"
    "tesourodireto/service/api/treasurybondsinfo.json"
)

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm",
}


@dataclass
class Titulo:
    nome: str
    indexador: str          # SELIC | IPCA | PREFIXADO | desconhecido
    taxa_compra: float | None   # % a.a. (parte fixa, p/ IPCA+ é o juro real)
    preco_unitario: float | None
    investimento_minimo: float | None
    vencimento: str


def _classify(nome: str) -> str:
    n = nome.upper()
    if "SELIC" in n:
        return "SELIC"
    if "IPCA" in n or "IGPM" in n:
        return "IPCA"
    if "PREFIXADO" in n or "LTN" in n:
        return "PREFIXADO"
    return "OUTRO"


def fetch_tesouro(timeout: int = 20) -> list[Titulo]:
    """Busca títulos DISPONÍVEIS PARA COMPRA na API oficial do Tesouro Direto."""
    try:
        from curl_cffi import requests as creq
        resp = creq.get(TESOURO_URL, headers=_HEADERS, timeout=timeout,
                        impersonate="chrome")
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        # fallback: requests puro (às vezes passa; se não, erro claro)
        import requests
        resp = requests.get(
            TESOURO_URL, timeout=timeout,
            headers={**_HEADERS, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"},
        )
        resp.raise_for_status()
        data = resp.json()

    bonds = (data.get("response") or {}).get("TrsrBdTradgList") or []
    titulos: list[Titulo] = []
    for item in bonds:
        bd = item.get("TrsrBd") or {}
        nome = bd.get("nm") or ""
        if not nome:
            continue
        taxa = bd.get("anulInvstmtRate")
        preco = bd.get("untrInvstmtVal")
        # taxa/preço de compra zerados = título só disponível p/ resgate
        if not taxa and not preco:
            continue
        titulos.append(Titulo(
            nome=nome,
            indexador=_classify(nome),
            taxa_compra=float(taxa) if taxa else None,
            preco_unitario=float(preco) if preco else None,
            investimento_minimo=float(bd.get("minInvstmtAmt") or 0) or None,
            vencimento=(bd.get("mtrtyDt") or "")[:10],
        ))
    titulos.sort(key=lambda t: (t.indexador, t.vencimento))
    return titulos


# ---------------- Comparador de ofertas (a "régua") ----------------

def ir_aliquota(anos: float) -> float:
    """Tabela regressiva de IR sobre renda fixa."""
    dias = anos * 365
    if dias <= 180:
        return 0.225
    if dias <= 360:
        return 0.20
    if dias <= 720:
        return 0.175
    return 0.15


def cdb_liquido_aa(pct_cdi: float, cdi_aa: float, anos: float) -> float:
    """Rendimento líquido anualizado de um CDB a `pct_cdi`% do CDI, após IR."""
    bruto_total = (1 + cdi_aa * pct_cdi / 100) ** anos - 1
    liquido_total = bruto_total * (1 - ir_aliquota(anos))
    return ((1 + liquido_total) ** (1 / anos) - 1) * 100


def lci_equivalente_pct_cdi(pct_cdi_lci: float, cdi_aa: float, anos: float) -> float:
    """A quantos % do CDI um CDB precisaria pagar para empatar com uma
    LCI/LCA isenta que paga `pct_cdi_lci`% do CDI."""
    alvo_liquido = (1 + cdi_aa * pct_cdi_lci / 100) ** anos - 1
    bruto_necessario = alvo_liquido / (1 - ir_aliquota(anos))
    taxa_aa = (1 + bruto_necessario) ** (1 / anos) - 1
    return taxa_aa / cdi_aa * 100


def regua_ofertas(cdi_aa: float) -> str:
    """Tabela texto: líquido de CDBs e equivalências de LCI por prazo."""
    linhas = [
        f"\n=== RÉGUA DE OFERTAS (CDI {cdi_aa * 100:.2f}% a.a.) ===",
        "Rendimento LÍQUIDO anualizado após IR regressivo:",
        "",
        f"{'OFERTA':<18}{'1 ano':>9}{'2 anos':>9}{'3 anos':>9}",
        "-" * 45,
    ]
    for pct in (100, 105, 110, 115, 120, 130):
        vals = [cdb_liquido_aa(pct, cdi_aa, a) for a in (1, 2, 3)]
        linhas.append(f"CDB {pct}% CDI{'':<6}" + "".join(f"{v:>8.2f}%" for v in vals))
    linhas += ["", "LCI/LCA (ISENTAS) — equivalência em CDB:"]
    for pct in (85, 90, 95, 100):
        eq = [lci_equivalente_pct_cdi(pct, cdi_aa, a) for a in (1, 2, 3)]
        linhas.append(
            f"LCI {pct}% CDI  = CDB " + " / ".join(f"{e:.0f}%" for e in eq)
            + "  (1/2/3 anos)"
        )
    linhas += [
        "",
        "Como usar: a corretora te oferece um CDB de 110% CDI por 2 anos?",
        "Olhe a linha correspondente — esse é o líquido real. Compare com o",
        "Tesouro Selic (≈CDI - IR) e com as LCIs disponíveis antes de decidir.",
    ]
    return "\n".join(linhas)


def format_tesouro(titulos: list[Titulo]) -> str:
    if not titulos:
        return "Nenhum título retornado (API do Tesouro pode estar instável — tente mais tarde)."
    grupos = {"SELIC": [], "IPCA": [], "PREFIXADO": [], "OUTRO": []}
    for t in titulos:
        grupos[t.indexador].append(t)
    out = ["\n=== TESOURO DIRETO — títulos disponíveis para compra (fonte oficial) ==="]
    nomes = {"SELIC": "Pós-fixados (Selic)", "IPCA": "Inflação (IPCA+)",
             "PREFIXADO": "Prefixados", "OUTRO": "Outros"}
    for key, lista in grupos.items():
        if not lista:
            continue
        out.append(f"\n{nomes[key]}:")
        for t in lista:
            taxa = f"{t.taxa_compra:.2f}% a.a." if t.taxa_compra else "—"
            extra = " + taxa" if key in ("SELIC", "IPCA") else ""
            minimo = f" | mín R$ {t.investimento_minimo:,.2f}" if t.investimento_minimo else ""
            out.append(f"  • {t.nome:<38} {taxa}{extra}  venc {t.vencimento}{minimo}")
    return "\n".join(out)
