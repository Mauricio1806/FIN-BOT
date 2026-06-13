"""
FIN-BOT | Página de corretoras (estática, dados verificados)
Tabela comparativa por mercado-alvo. Fontes: sites oficiais das corretoras,
ANBIMA, B3 e reportagens 2025-2026. Dados sujeitos a mudança — sempre confirmar
no site oficial antes de abrir conta. Educativo, não é recomendação.

Última verificação dos dados: junho/2026.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


# Dados das corretoras — organizados por foco de mercado.
# Cada item: (nome, regulador, foco, taxa_acoes, taxa_rf, custodia, spread_cambial, link)
BROKERS_BR = [
    {
        "nome": "XP Investimentos",
        "regulador": "CVM/BCB",
        "fundada": "2001",
        "foco": "Ações, FIIs, RF, fundos, BDRs",
        "taxa_acoes": "R$ 8,90/ordem (swing); R$ 2,90 day trade",
        "taxa_rf": "Isenta em RF, FIIs e fundos",
        "custodia": "Isenta",
        "diferencial": "Maior plataforma do BR; mesa de operações; assessor",
        "atencao": "Taxa de ações por ordem pesa em aportes pequenos",
        "link": "https://www.xpi.com.br",
    },
    {
        "nome": "Rico (grupo XP)",
        "regulador": "CVM/BCB",
        "fundada": "2008",
        "foco": "Ações, FIIs, RF, fundos",
        "taxa_acoes": "Isenta para ações e FIIs",
        "taxa_rf": "Isenta",
        "custodia": "Isenta",
        "diferencial": "Corretagem zero em RV; plataforma simples",
        "atencao": "Faz parte do grupo XP; mesa de operações cobrada à parte",
        "link": "https://www.rico.com.vc",
    },
    {
        "nome": "BTG Pactual",
        "regulador": "CVM/BCB",
        "fundada": "1983",
        "foco": "Ações, FIIs, RF, fundos exclusivos, private",
        "taxa_acoes": "Isenta para ações e FIIs",
        "taxa_rf": "Isenta",
        "custodia": "Isenta",
        "diferencial": "Banco de investimento; produtos exclusivos; conta global",
        "atencao": "Plataforma mais técnica que apps de banco digital",
        "link": "https://www.btgpactual.com",
    },
    {
        "nome": "Banco Inter",
        "regulador": "CVM/BCB",
        "fundada": "1994",
        "foco": "Conta + ações, FIIs, RF, ETFs internacionais",
        "taxa_acoes": "Isenta para ações e FIIs",
        "taxa_rf": "Isenta",
        "custodia": "Isenta",
        "diferencial": "Conta + investimentos no mesmo app; integração com Pix",
        "atencao": "Plataforma de investimento menos sofisticada que XP/BTG",
        "link": "https://www.bancointer.com.br",
    },
    {
        "nome": "NuInvest (Nubank)",
        "regulador": "CVM/BCB",
        "fundada": "2011 (Easynvest)",
        "foco": "Ações, FIIs, RF, ETFs",
        "taxa_acoes": "Isenta",
        "taxa_rf": "Isenta",
        "custodia": "Isenta",
        "diferencial": "Integrado ao Nubank; UX simples para iniciantes",
        "atencao": "Catálogo de RF menor; sem mesa de operações",
        "link": "https://nuinvest.com.br",
    },
    {
        "nome": "Clear (grupo XP)",
        "regulador": "CVM/BCB",
        "fundada": "2010",
        "foco": "Trading (day/swing), ações, futuros",
        "taxa_acoes": "Isenta para ações e FIIs (swing)",
        "taxa_rf": "Isenta",
        "custodia": "Isenta",
        "diferencial": "Plataforma profissional de trading; gráficos avançados",
        "atencao": "Foco em trader ativo, não em aporte de longo prazo",
        "link": "https://www.clear.com.br",
    },
    {
        "nome": "Tesouro Direto (B3)",
        "regulador": "CVM/Tesouro Nacional",
        "fundada": "2002",
        "foco": "Títulos públicos federais (única plataforma)",
        "taxa_acoes": "—",
        "taxa_rf": "Taxa B3: 0,20% a.a. até R$ 10k; 0% acima",
        "custodia": "Inclusa na taxa B3",
        "diferencial": "Acesso direto via qualquer corretora cadastrada",
        "atencao": "Algumas corretoras zeram a taxa B3 nos primeiros R$ 10k",
        "link": "https://www.tesourodireto.com.br",
    },
]

BROKERS_EUA = [
    {
        "nome": "Avenue Securities",
        "regulador": "SEC/FINRA (EUA) + Banco Central (BR)",
        "fundada": "2018",
        "foco": "Ações, ETFs, REITs e RF dos EUA",
        "taxa_acoes": "US$ 2,50/ordem (corretagem)",
        "taxa_rf": "Conforme produto",
        "custodia": "Isenta",
        "diferencial": "Pioneira para brasileiros nos EUA; pertence ao Itaú; site em PT",
        "atencao": "Spread cambial 1,6%–1,95% (mais alto que concorrentes)",
        "link": "https://www.avenue.us",
    },
    {
        "nome": "Nomad",
        "regulador": "DriveWealth/FINRA (EUA) + BCB",
        "fundada": "2020",
        "foco": "Conta em dólar + ações, ETFs, REITs EUA",
        "taxa_acoes": "Isenta (corretagem zero)",
        "taxa_rf": "Conforme produto",
        "custodia": "Isenta",
        "diferencial": "Conta + cartão internacional + investimentos no mesmo app",
        "atencao": "Spread cambial a partir de 1% (sobre dólar comercial)",
        "link": "https://www.nomadglobal.com",
    },
    {
        "nome": "Inter (mercado global)",
        "regulador": "BCB + parceiro internacional",
        "fundada": "2022 (Inter Global)",
        "foco": "Conta global + ações e ETFs dos EUA",
        "taxa_acoes": "Isenta",
        "taxa_rf": "—",
        "custodia": "Isenta",
        "diferencial": "Conta global integrada ao banco; baixo custo para aporte mensal",
        "atencao": "Plataforma mais simples; menos recursos avançados",
        "link": "https://www.bancointer.com.br/global-account/",
    },
    {
        "nome": "Interactive Brokers",
        "regulador": "SEC/FINRA (EUA)",
        "fundada": "1978",
        "foco": "Acesso a 150+ bolsas em 33 países (EUA, Europa, Ásia)",
        "taxa_acoes": "US$ 0,005/ação (mín. US$ 1/ordem) ou plano Lite zero",
        "taxa_rf": "Conforme produto",
        "custodia": "Isenta acima de US$ 100k em conta",
        "diferencial": "Único caminho a mercados além dos EUA (Europa, Ásia, Hong Kong, Tóquio)",
        "atencao": "Plataforma técnica em inglês; documentação fiscal de fora do BR",
        "link": "https://www.interactivebrokers.com",
    },
    {
        "nome": "C6 Bank Global",
        "regulador": "BCB + parceiro internacional",
        "fundada": "2019",
        "foco": "Conta global + ações e ETFs dos EUA",
        "taxa_acoes": "Isenta",
        "taxa_rf": "—",
        "custodia": "Isenta",
        "diferencial": "Conta global integrada; programa de pontos Átomos",
        "atencao": "Catálogo focado em ativos mais negociados",
        "link": "https://www.c6bank.com.br",
    },
]

BROKERS_GLOBAL = [
    {
        "nome": "Interactive Brokers",
        "regulador": "SEC/FINRA + FCA (UK) + outros",
        "fundada": "1978",
        "foco": "Bolsas dos EUA + LSE, Frankfurt, Paris, Tóquio, Hong Kong, Singapura, Shanghai (via HK)",
        "taxa_acoes": "Tier (~US$ 0,005/ação); planos europeus por região",
        "taxa_rf": "Acesso a treasuries, gilts, bunds",
        "custodia": "Isenta acima de US$ 100k",
        "diferencial": "ÚNICO caminho real para brasileiros acessarem Europa, Japão, China A-shares (via Hong Kong) e Reino Unido",
        "atencao": "Plataforma técnica; documentação fiscal complexa; necessário declarar bens no exterior à RFB",
        "link": "https://www.interactivebrokers.com",
    },
    {
        "nome": "Saxo Bank",
        "regulador": "Danish FSA + FCA + MAS",
        "fundada": "1992",
        "foco": "40+ bolsas globais, FX, derivativos",
        "taxa_acoes": "Variável por bolsa (NYSE ~US$ 4/ordem)",
        "taxa_rf": "Acesso amplo a bonds globais",
        "custodia": "0,12% a.a. (mín. 5 EUR/mês)",
        "diferencial": "Alternativa europeia ao IB; bom para residentes UE",
        "atencao": "Pouca documentação em português; depósito mínimo varia",
        "link": "https://www.home.saxo",
    },
    {
        "nome": "DEGIRO",
        "regulador": "BaFin (Alemanha) / AFM (Holanda)",
        "fundada": "2008",
        "foco": "Bolsas europeias + EUA + algumas asiáticas",
        "taxa_acoes": "EUR 1,00 + 1 EUR conexão/bolsa/ano",
        "taxa_rf": "Sim",
        "custodia": "Isenta",
        "diferencial": "Custo baixíssimo para europeus; popular para ETFs UCITS",
        "atencao": "APENAS para residentes em países europeus listados — brasileiro só pode operar se mudar residência",
        "link": "https://www.degiro.eu",
    },
]


_CSS_BROKERS = """
:root{color-scheme:dark}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0b1020;
  color:#e2e8f0;padding:20px;max-width:1100px;margin:0 auto;line-height:1.55}
h1{font-size:1.6rem;margin-bottom:4px}
h2{font-size:1.15rem;margin:28px 0 14px;color:#93c5fd}
.sub{color:#64748b;font-size:.85rem;margin-bottom:16px}
.back{display:inline-block;color:#60a5fa;text-decoration:none;font-size:.88rem;
  margin-bottom:16px;padding:6px 12px;border:1px solid #1e2a4a;border-radius:8px}
.back:hover{background:#16213f}
.intro{background:#111a33;border:1px solid #1e2a4a;border-left:3px solid #3b82f6;
  border-radius:10px;padding:14px 18px;margin-bottom:24px;font-size:.92rem}
.broker{background:#111a33;border:1px solid #1e2a4a;border-radius:12px;
  padding:18px 20px;margin-bottom:14px}
.broker h3{font-size:1.05rem;color:#fff;margin-bottom:4px;display:flex;
  align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.broker h3 a{font-size:.78rem;background:#3b82f6;color:#fff;padding:5px 12px;
  border-radius:99px;text-decoration:none;font-weight:600}
.broker h3 a:hover{background:#2563eb}
.meta{font-size:.78rem;color:#64748b;margin-bottom:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin-top:10px}
.grid div{background:#0b1020;border:1px solid #1e2a4a;padding:9px 12px;border-radius:8px;font-size:.85rem}
.grid b{color:#93c5fd;font-size:.7rem;text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px}
.atencao{background:#7f1d1d33;border-left:3px solid #f87171;padding:9px 13px;
  border-radius:8px;margin-top:10px;font-size:.85rem;color:#fca5a5}
.disc{margin-top:32px;color:#475569;font-size:.78rem;line-height:1.5}
@media(max-width:640px){body{padding:12px}h1{font-size:1.3rem}}
"""


def _render_broker(b: dict) -> str:
    atencao = f'<div class="atencao">⚠️ <b>Atenção:</b> {b["atencao"]}</div>' if b.get("atencao") else ""
    return f"""
    <div class="broker">
      <h3>{b['nome']} <a href="{b['link']}" target="_blank" rel="noopener">Site oficial →</a></h3>
      <div class="meta">Regulador: {b['regulador']} · Fundada em {b['fundada']} · Foco: {b['foco']}</div>
      <div class="grid">
        <div><b>Corretagem ações</b>{b['taxa_acoes']}</div>
        <div><b>Renda fixa</b>{b['taxa_rf']}</div>
        <div><b>Custódia</b>{b['custodia']}</div>
      </div>
      <div class="grid" style="margin-top:8px">
        <div style="grid-column:1/-1"><b>Diferencial</b>{b['diferencial']}</div>
      </div>
      {atencao}
    </div>"""


def build_brokers_page() -> str:
    now = datetime.now(ZoneInfo("America/Bahia")).strftime("%d/%m/%Y")
    br = "".join(_render_broker(b) for b in BROKERS_BR)
    eua = "".join(_render_broker(b) for b in BROKERS_EUA)
    glob = "".join(_render_broker(b) for b in BROKERS_GLOBAL)

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FIN-BOT — Corretoras</title><style>{_CSS_BROKERS}</style></head><body>
<a href="index.html" class="back">← Voltar ao painel</a>
<h1>🏦 Corretoras por mercado</h1>
<p class="sub">Tabela comparativa · dados verificados em {now} · sempre confirme no site oficial</p>

<div class="intro">
<b>Como ler esta página:</b> as corretoras estão agrupadas por mercado-alvo.
Para a B3 (🇧🇷), praticamente todas zeraram corretagem em ações/FIIs/RF — o que
diferencia é catálogo de produtos, qualidade da plataforma e suporte. Para os
EUA (🇺🇸), o que pesa é o <b>spread cambial</b> (custo real de conversão BRL→USD),
não a corretagem. Para Europa (🇪🇺) e China/Ásia (🇨🇳), na prática só a
<b>Interactive Brokers</b> dá acesso direto de quem mora no Brasil; o resto exige
mudança de residência fiscal.
</div>

<h2>🇧🇷 Mercado brasileiro (B3 — ações, FIIs, RF, Tesouro Direto)</h2>
{br}

<h2>🇺🇸 Mercado dos EUA (NYSE, NASDAQ — ações, ETFs, REITs)</h2>
{eua}

<h2>🌍 Europa e Ásia (LSE, Frankfurt, Tóquio, Hong Kong, Shanghai)</h2>
{glob}

<p class="disc">Dados compilados de sites oficiais das corretoras, ANBIMA, B3 e
reportagens 2025–2026 (XP, Nord Investimentos, iDinheiro, A Revista, Mobills).
Taxas e condições mudam frequentemente — <b>sempre confirme no site oficial</b>
antes de abrir conta. Esta página é informativa e educativa, <b>não é recomendação
de qual corretora usar</b>. A escolha depende do seu perfil, volume aportado e
preferência de plataforma. O FIN-BOT <b>não tem parceria comercial</b> com nenhuma
das corretoras listadas.</p>
</body></html>"""


def save_brokers_page() -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path = DOCS_DIR / "corretoras.html"
    path.write_text(build_brokers_page(), encoding="utf-8")
    return path
