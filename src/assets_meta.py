"""
FIN-BOT | Metadados dos ativos
Catálogo curado com nome completo, exchange, setor, país e tese de cada ticker
da watchlist. Usado para enriquecer o ranking e os insights.
"""
from __future__ import annotations

# Estrutura: ticker -> (nome, exchange, setor, país, categoria, tese curta)
ASSETS = {
    # ========== BRASIL — ETFs ==========
    "BOVA11.SA": ("iShares Ibovespa", "B3", "ETF Índice", "BR", "ETF Amplo",
                  "Replica o Ibovespa — exposição às 80+ maiores empresas da B3."),
    "SMAL11.SA": ("iShares Small Cap", "B3", "ETF Small Caps", "BR", "ETF Small",
                  "Pequenas empresas brasileiras — maior beta com ciclo doméstico."),
    "IVVB11.SA": ("iShares S&P 500 BRL", "B3", "ETF Internacional", "BR/US", "ETF Internacional",
                  "S&P 500 em reais — dolarização sem remessa internacional."),
    "B5P211.SA": ("IMA-B 5 Tesouro IPCA+", "B3", "ETF Renda Fixa", "BR", "ETF RF",
                  "Tesouro IPCA+ via bolsa — trava juro real até 5 anos."),

    # ========== BRASIL — Blue chips ==========
    "ITUB4.SA": ("Itaú Unibanco PN", "B3", "Bancos", "BR", "Ação BR",
                 "Maior banco privado da AL — beneficiário direto de juros altos."),
    "WEGE3.SA": ("WEG ON", "B3", "Bens de Capital", "BR", "Ação BR",
                 "Multinacional de motores e equipamentos elétricos — exportadora."),
    "VALE3.SA": ("Vale ON", "B3", "Mineração", "BR", "Ação BR",
                 "Maior mineradora de ferro do mundo — proxy do ciclo China."),
    "PETR4.SA": ("Petrobras PN", "B3", "Petróleo & Gás", "BR", "Ação BR",
                 "Estatal de petróleo — alta dividend yield, risco político."),
    "BBSE3.SA": ("BB Seguridade ON", "B3", "Seguros", "BR", "Ação BR",
                 "Seguradora do BB — beneficiária de juros altos (float)."),

    # ========== BRASIL — FIIs ==========
    "HGLG11.SA": ("CGHG Logística", "B3", "FII Logística", "BR", "FII Tijolo",
                  "FII de galpões logísticos — exposição ao e-commerce."),
    "MXRF11.SA": ("Maxi Renda", "B3", "FII Papel", "BR", "FII Papel",
                  "FII de CRIs — renda mensal isenta de IR para PF."),
    "KNRI11.SA": ("Kinea Renda Imobiliária", "B3", "FII Híbrido", "BR", "FII Híbrido",
                  "FII híbrido (lajes + logística) — gestão Kinea/Itaú."),

    # ========== CRIPTO ==========
    "BTC-USD": ("Bitcoin", "Global", "Criptomoeda", "Global", "Cripto",
                "Maior criptoativo — store of value digital, alta volatilidade."),

    # ========== EUA — ETFs ==========
    "VOO":  ("Vanguard S&P 500", "NYSE", "ETF Large Cap", "US", "ETF Amplo",
             "500 maiores empresas dos EUA — núcleo de carteira americana."),
    "QQQ":  ("Invesco QQQ Trust", "NASDAQ", "ETF Tech", "US", "ETF Setorial",
             "Nasdaq 100 — 100 maiores não-financeiras, peso em Big Tech."),
    "DIA":  ("SPDR Dow Jones", "NYSE", "ETF Large Cap", "US", "ETF Amplo",
             "30 blue chips americanas — viés value e dividendos."),
    "IWM":  ("iShares Russell 2000", "NYSE", "ETF Small Cap", "US", "ETF Small",
             "2000 small caps dos EUA — sensível a juros internos."),
    "VXUS": ("Vanguard Total World ex-US", "NASDAQ", "ETF Global", "Global", "ETF Internacional",
             "Mundo ex-EUA — diversificação fora do dólar/Wall Street."),
    "SCHD": ("Schwab US Dividend Equity", "NYSE", "ETF Dividendos", "US", "ETF Setorial",
             "ETF de dividendos com qualidade — foco em fluxo de caixa."),

    # ========== EUA — Mag 7 e outras ==========
    "AAPL":  ("Apple Inc.", "NASDAQ", "Tech / Hardware", "US", "Ação US",
              "Maior empresa do mundo por market cap — ecossistema iPhone."),
    "MSFT":  ("Microsoft Corp.", "NASDAQ", "Tech / Software", "US", "Ação US",
              "Software + cloud Azure + OpenAI — exposição direta a IA."),
    "GOOGL": ("Alphabet (Google) A", "NASDAQ", "Tech / Internet", "US", "Ação US",
              "Búsca, YouTube, cloud, Waymo — diversificação tech."),
    "AMZN":  ("Amazon.com Inc.", "NASDAQ", "E-commerce / Cloud", "US", "Ação US",
              "E-commerce + AWS (líder em cloud) — duplo motor."),
    "NVDA":  ("NVIDIA Corp.", "NASDAQ", "Semicondutores", "US", "Ação US",
              "GPUs para IA — principal beneficiária do ciclo de IA."),
    "META":  ("Meta Platforms", "NASDAQ", "Tech / Mídia", "US", "Ação US",
              "Facebook, Instagram, WhatsApp + Reality Labs (VR/AR)."),
    "TSLA":  ("Tesla Inc.", "NASDAQ", "Veículos Elétricos", "US", "Ação US",
              "Líder em EVs + energia + IA (FSD) — alta volatilidade."),
    "JPM":   ("JPMorgan Chase", "NYSE", "Bancos", "US", "Ação US",
              "Maior banco dos EUA — barômetro do sistema financeiro."),
    "XOM":   ("ExxonMobil", "NYSE", "Petróleo & Gás", "US", "Ação US",
              "Maior petroleira dos EUA — hedge contra inflação de energia."),
    "JNJ":   ("Johnson & Johnson", "NYSE", "Healthcare", "US", "Ação US",
              "Farmacêutica + dispositivos médicos — defensiva clássica."),

    # ========== EUROPA ==========
    "EXS1.DE":  ("iShares Core DAX", "Frankfurt (XETRA)", "ETF Alemanha", "DE", "ETF",
                 "DAX 40 — 40 maiores empresas alemãs (Siemens, SAP, Allianz)."),
    "IMEU.AS":  ("iShares MSCI Europe", "Euronext Amsterdam", "ETF Europa", "EU", "ETF",
                 "MSCI Europe — diversificação ampla pela Europa desenvolvida."),
    "VEUR.AS":  ("Vanguard FTSE Europe", "Euronext Amsterdam", "ETF Europa", "EU", "ETF",
                 "FTSE Developed Europe — taxa de adm. muito baixa."),
    "ASML":     ("ASML Holding", "Euronext / NASDAQ", "Semicondutores", "NL", "Ação UE",
                 "Monopólio em litografia EUV — gargalo da indústria de chips."),
    "SAP":      ("SAP SE", "NYSE (ADR)", "Software Empresarial", "DE", "Ação UE",
                 "Líder global em ERP — base de receita recorrente."),
    "NVO":      ("Novo Nordisk", "NYSE (ADR)", "Farmacêutica", "DK", "Ação UE",
                 "Líder em diabetes/obesidade (Ozempic, Wegovy)."),
    "SHEL":     ("Shell plc", "NYSE (ADR)", "Petróleo & Gás", "UK", "Ação UE",
                 "Major europeia de óleo & gás — dividendo robusto."),
    "HSBC":     ("HSBC Holdings", "NYSE (ADR)", "Bancos", "UK/HK", "Ação UE",
                 "Banco anglo-asiático — ponte entre UK, Hong Kong e China."),
    "SAN":      ("Banco Santander", "NYSE (ADR)", "Bancos", "ES", "Ação UE",
                 "Banco espanhol global — forte exposição a América Latina."),
    "NESN.SW":  ("Nestlé SA", "SIX (Suíça)", "Alimentos", "CH", "Ação UE",
                 "Maior empresa de alimentos do mundo — defensiva clássica."),
    "ROG.SW":   ("Roche Holding", "SIX (Suíça)", "Farmacêutica", "CH", "Ação UE",
                 "Líder em oncologia e diagnósticos."),

    # ========== CHINA & ÁSIA ==========
    "MCHI":  ("iShares MSCI China", "NASDAQ", "ETF China", "CN", "ETF",
              "ETF amplo de ações chinesas (incluindo ADRs)."),
    "FXI":   ("iShares China Large-Cap", "NYSE", "ETF China", "CN", "ETF",
              "50 maiores empresas chinesas — concentrado em bancos."),
    "KWEB":  ("KraneShares CSI China Internet", "NYSE", "ETF Tech CN", "CN", "ETF",
              "Internet/tech chinesa (Alibaba, Tencent, JD)."),
    "ASHR":  ("Xtrackers CSI 300 A-Shares", "NYSE", "ETF China", "CN", "ETF",
              "Ações A negociadas em Xangai/Shenzhen — mercado doméstico."),
    "EWH":   ("iShares MSCI Hong Kong", "NYSE", "ETF Hong Kong", "HK", "ETF",
              "Mercado de Hong Kong — ponte para China e finanças asiáticas."),
    "EWT":   ("iShares MSCI Taiwan", "NYSE", "ETF Taiwan", "TW", "ETF",
              "Taiwan — concentrado em TSMC e cadeia de chips."),
    "INDA":  ("iShares MSCI India", "NYSE", "ETF Índia", "IN", "ETF",
              "Mercado indiano — demografia favorável e crescimento alto."),
    "BABA":  ("Alibaba Group", "NYSE (ADR)", "E-commerce / Cloud", "CN", "Ação CN",
              "Amazon chinesa — e-commerce, cloud, fintech (Ant)."),
    "JD":    ("JD.com", "NASDAQ (ADR)", "E-commerce", "CN", "Ação CN",
              "E-commerce com logística própria — concorrente da Alibaba."),
    "PDD":   ("PDD Holdings (Temu)", "NASDAQ (ADR)", "E-commerce", "CN", "Ação CN",
              "Dona do Pinduoduo e Temu — crescimento agressivo global."),
    "BIDU":  ("Baidu", "NASDAQ (ADR)", "Internet / IA", "CN", "Ação CN",
              "Google chinês + carros autônomos Apollo + LLM Ernie."),
    "TCEHY": ("Tencent Holdings", "OTC (ADR)", "Tech / Gaming", "CN", "Ação CN",
              "WeChat + maior empresa de jogos do mundo."),
    "TSM":   ("Taiwan Semiconductor (TSMC)", "NYSE (ADR)", "Semicondutores", "TW", "Ação Asia",
              "Maior fabricante de chips do mundo — fabrica para Apple, NVIDIA, AMD."),
}


def get_meta(ticker: str) -> dict:
    """Retorna metadados de um ticker. Se não conhecido, retorna defaults."""
    if ticker in ASSETS:
        nome, exch, setor, pais, cat, tese = ASSETS[ticker]
        return {"nome": nome, "exchange": exch, "setor": setor,
                "pais": pais, "categoria": cat, "tese": tese}
    return {"nome": ticker, "exchange": "—", "setor": "—",
            "pais": "—", "categoria": "—",
            "tese": "Metadados não cadastrados."}
