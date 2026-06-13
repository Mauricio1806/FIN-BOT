"""
FIN-BOT | Camada de insights técnicos (estendida)
- Breadth & regime de mercado
- Análise por classe de ativo (ETFs / ações / FIIs / cripto)
- Detecção de cruzamentos, divergências e setups
- Comparações cross-market (correlação dólar, juros)
- Setups de aporte por perfil
"""
from __future__ import annotations
from collections import Counter, defaultdict
from .trends import Analysis


# -------------------- Classificação de ativos --------------------
def asset_class(ticker: str) -> str:
    """Classifica o ticker em classe de ativo para análise por bucket."""
    t = ticker.upper()
    if t.endswith("-USD"):
        return "cripto"
    if t.endswith("11.SA"):
        # FIIs e ETFs B3 terminam em 11 — distinguimos pelos prefixos comuns
        etfs_b3 = {"BOVA", "SMAL", "IVVB", "B5P2", "IMAB", "SPXI", "HASH", "BBSD",
                   "ECOO", "ISUS", "PIBB", "DIVO", "FIND", "GOVE", "MATB", "MOBI",
                   "SMAC", "XINA", "EURP"}
        if any(t.startswith(p) for p in etfs_b3):
            return "etf_br"
        return "fii"
    if t.endswith(".SA"):
        return "acao_br"
    # Tickers de ETFs internacionais conhecidos
    etfs_us = {"VOO", "VTI", "QQQ", "DIA", "IWM", "VXUS", "SCHD", "VYM", "VEA", "VWO",
               "VEUR.AS", "IMEU.AS", "EXS1.DE", "CAC.PA",
               "MCHI", "FXI", "KWEB", "ASHR", "EWH", "EWT", "INDA", "EWJ", "EWG"}
    if t in etfs_us:
        return "etf_intl"
    return "acao_intl"


def by_class(analyses: list[Analysis]) -> dict[str, list[Analysis]]:
    out = defaultdict(list)
    for a in analyses:
        out[asset_class(a.ticker)].append(a)
    return dict(out)


# -------------------- Métricas de mercado --------------------
def market_breadth(analyses: list[Analysis]) -> dict:
    n = len(analyses)
    if not n:
        return {}
    trends = Counter(a.trend for a in analyses)
    em_alta = trends.get("ALTA", 0) + trends.get("ALTA_FORTE", 0)
    em_baixa = trends.get("BAIXA", 0) + trends.get("BAIXA_FORTE", 0)
    scores = [a.score for a in analyses]
    breadth_pct = em_alta / n * 100
    rsis = [a.rsi for a in analyses]
    return {
        "n": n,
        "em_alta": em_alta,
        "em_baixa": em_baixa,
        "laterais": trends.get("LATERAL", 0),
        "alta_forte": trends.get("ALTA_FORTE", 0),
        "baixa_forte": trends.get("BAIXA_FORTE", 0),
        "breadth_pct": breadth_pct,
        "score_medio": sum(scores) / n,
        "score_max": max(scores),
        "score_min": min(scores),
        "rsi_medio": sum(rsis) / n,
        "regime": (
            "EXPANSIVO" if breadth_pct >= 60
            else "MISTO" if breadth_pct >= 35
            else "DEFENSIVO"
        ),
    }


# -------------------- Insights principais (página) --------------------
def insights_text(analyses: list[Analysis], breadth: dict,
                  macro: dict | None = None, market_key: str = "brasil") -> list[str]:
    """Gera bullets ricos de análise. Cada bullet é HTML curto."""
    out = []
    if not breadth:
        return out

    regime = breadth["regime"]
    pct = breadth["breadth_pct"]
    rsi_m = breadth["rsi_medio"]

    # ===== 1. Regime de mercado (sempre) =====
    if regime == "EXPANSIVO":
        ctx = (f"📈 <b>Mercado expansivo</b>: {pct:.0f}% dos ativos em tendência de alta, "
               f"RSI médio {rsi_m:.0f}. ")
        if rsi_m > 65:
            ctx += ("Sinal de <b>euforia</b> — historicamente precede correções de "
                    "5-15%. Aporte com critério (escalonar, não tudo de uma vez).")
        elif rsi_m > 55:
            ctx += ("Cenário favorável para aportes em renda variável; foco em "
                    "qualidade fundamentalista, não em barganha de preço.")
        else:
            ctx += ("Início de ciclo de alta — momento atrativo para construir posição "
                    "em ativos de qualidade.")
        out.append(ctx)
    elif regime == "MISTO":
        out.append(f"⚖️ <b>Mercado misto</b>: {pct:.0f}% em alta, {breadth['em_baixa']} em "
                   f"baixa, {breadth['laterais']} laterais. <b>Seletividade importa mais "
                   f"que timing</b>: foque nos ativos com score ≥ 60 e tendência clara, "
                   "evite os laterais sem catalisador.")
    else:
        out.append(f"🛡️ <b>Mercado defensivo</b>: apenas {pct:.0f}% em alta. "
                   "Cenários históricos similares pediram: (1) fortalecer posição em renda "
                   "fixa e caixa, (2) reduzir tamanho de aporte mensal em RV, (3) aportar "
                   "só nos 2-3 ativos com score mais alto, (4) evitar aportes em "
                   "tendência de baixa, por mais 'descontados' que pareçam.")

    # ===== 2. Macro & contexto Brasil =====
    if market_key == "brasil" and macro:
        selic = macro.get("selic_meta_aa", {}).get("valor")
        ipca = macro.get("ipca_12m", {}).get("valor")
        jr = macro.get("juro_real_aa", {}).get("valor")
        if selic and ipca and jr:
            if jr >= 7:
                out.append(f"🏦 <b>Juro real em {jr:.1f}% a.a.</b> (Selic {selic:.2f}% vs "
                           f"IPCA {ipca:.2f}%) é <b>excepcionalmente alto</b> — entre os "
                           f"maiores do mundo. Tesouro Selic e CDB ≥100% CDI rendem mais "
                           "que a média histórica da bolsa com risco bem menor. Isso "
                           "<b>achata o prêmio de risco</b> da renda variável — exige "
                           "ainda mais critério na seleção.")
            elif jr >= 4:
                out.append(f"🏦 <b>Juro real em {jr:.1f}% a.a.</b> mantém renda fixa "
                           "competitiva. Cenário equilibrado entre classes.")
            else:
                out.append(f"🏦 <b>Juro real em {jr:.1f}% a.a.</b> baixo — renda variável "
                           "e ativos reais (FIIs, ações) ganham atratividade relativa.")

    # ===== 3. Análise por classe de ativo =====
    classes = by_class(analyses)
    if len(classes) > 1:
        class_labels = {"acao_br": "Ações BR", "etf_br": "ETFs BR", "fii": "FIIs",
                        "cripto": "Cripto", "acao_intl": "Ações", "etf_intl": "ETFs"}
        parts = []
        for cls, items in classes.items():
            if not items:
                continue
            avg = sum(a.score for a in items) / len(items)
            cor = "🟢" if avg >= 60 else "🟡" if avg >= 45 else "🔴"
            label = class_labels.get(cls, cls)
            parts.append(f"{cor} {label} (média {avg:.0f})")
        out.append(f"📊 <b>Por classe de ativo</b>: " + " · ".join(parts) +
                   ". Use isso para decidir a <b>composição</b> do aporte, não só "
                   "ativos individuais.")

    # ===== 4. Sobrevendidos em tendência saudável (oportunidade) =====
    sobrevendidos = [a for a in analyses
                     if a.rsi < 40 and a.trend in ("ALTA", "ALTA_FORTE", "LATERAL")]
    if sobrevendidos:
        nomes = ", ".join(f"<b>{a.ticker}</b> (RSI {a.rsi:.0f})" for a in sobrevendidos[:5])
        out.append(f"🎯 <b>Oportunidades de aporte</b> — recuo técnico em tendência "
                   f"sustentada: {nomes}. Quando o RSI cai abaixo de 40 sem quebra "
                   "estrutural da tendência, é o setup clássico de 'comprar na queda'. "
                   "Confirme com volume e divergências de MACD antes de pesar a mão.")

    # ===== 5. Sobrecomprados (cautela) =====
    sobrecomprados = [a for a in analyses if a.rsi > 70]
    if sobrecomprados:
        nomes = ", ".join(f"<b>{a.ticker}</b> (RSI {a.rsi:.0f})" for a in sobrecomprados[:5])
        out.append(f"⚠️ <b>Esticados (RSI > 70)</b>: {nomes}. Aportar agora paga prêmio "
                   "de curto prazo. Estratégia mais eficiente: reduzir peso destes no "
                   "aporte do mês ou aguardar correção de 5-10% para entrada.")

    # ===== 6. Cruzamentos estruturais =====
    cross_alta = [a for a in analyses if "GOLDEN CROSS" in " ".join(a.signals)]
    cross_baixa = [a for a in analyses if "DEATH CROSS" in " ".join(a.signals)]
    if cross_alta:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in cross_alta[:3])
        out.append(f"🟢 <b>Golden Cross recente</b> em {nomes} — SMA50 cruzou SMA200 "
                   "para cima. Sinal de virada de ciclo de médio/longo prazo; "
                   "historicamente precede ganhos médios de 8-15% nos 6 meses "
                   "seguintes (não é garantia, é estatística histórica).")
    if cross_baixa:
        nomes = ", ".join(f"<b>{a.ticker}</b>" for a in cross_baixa[:3])
        out.append(f"🔴 <b>Death Cross recente</b> em {nomes} — SMA50 cruzou SMA200 "
                   "para baixo. Sinal de fim de ciclo de alta. Evite aportar "
                   "neste ativo até que (1) o preço recupere a SMA200 ou (2) "
                   "MACD apresente cruzamento de alta com volume.")

    # ===== 7. Volume anômalo (movimento institucional) =====
    volume_anomalo = [a for a in analyses if a.vol_ratio > 1.8]
    if volume_anomalo:
        for a in volume_anomalo[:3]:
            direcao = "compradora" if a.trend in ("ALTA", "ALTA_FORTE") else "vendedora"
            out.append(f"🔊 <b>{a.ticker}</b> com volume <b>{a.vol_ratio:.1f}x</b> "
                       f"acima da média — pressão {direcao} relevante. Investigue "
                       "o fato gerador (resultado trimestral, fato relevante, "
                       "decisão regulatória). Volume sem notícia conhecida pode "
                       "indicar movimentação institucional antecipada.")

    # ===== 8. Descontados vs máxima 52s =====
    descontos = [a for a in analyses if a.pct_from_high_52w < -20 and a.score >= 50]
    if descontos:
        for a in sorted(descontos, key=lambda x: x.pct_from_high_52w)[:3]:
            out.append(f"💎 <b>{a.ticker}</b> a {a.pct_from_high_52w:.0f}% da máxima de "
                       f"52 semanas com score técnico {a.score} ainda saudável. "
                       "Combinação de desconto de preço + tese técnica preservada = "
                       "candidato forte a aporte por <b>valor relativo</b>.")

    # ===== 9. Volatilidade extrema =====
    voláteis = [a for a in analyses if a.atr_pct > 3.5]
    if voláteis:
        nomes = ", ".join(f"<b>{a.ticker}</b> (ATR {a.atr_pct:.1f}%)" for a in voláteis[:3])
        out.append(f"⚡ <b>Alta volatilidade</b>: {nomes}. Variação diária típica > 3,5%. "
                   "Reduza o tamanho da posição proporcionalmente — risco/posição deve "
                   "ser constante, não o valor aportado.")

    # ===== 10. Top/bottom ranking =====
    top3 = sorted(analyses, key=lambda x: x.score, reverse=True)[:3]
    out.append(f"🏆 <b>Top 3 por condição técnica</b>: " +
               ", ".join(f"<b>{a.ticker}</b> (score {a.score}, {a.trend.replace('_',' ').lower()})"
                         for a in top3) +
               ". Estrutura técnica mais saudável neste momento — não é " 
               "'comprar agora', é 'priorizar na próxima janela de entrada'.")
    bottom3 = sorted(analyses, key=lambda x: x.score)[:3]
    out.append(f"🐌 <b>Piores condições técnicas</b>: " +
               ", ".join(f"<b>{a.ticker}</b> (score {a.score})" for a in bottom3) +
               ". Considere reduzir peso ou suspender aporte neste mês. "
               "Score baixo persistente por 3+ meses pede reavaliação da tese.")

    # ===== 11. Específico por mercado =====
    if market_key == "eua":
        out.append("🇺🇸 <b>Contexto EUA</b>: monitore Fed Funds Rate, CPI e payrolls "
                   "mensais. Cortes de juros tendem a beneficiar small caps (IWM) e "
                   "tech (QQQ); altas favorecem value (DIA) e dividendos (SCHD).")
    elif market_key == "europa":
        out.append("🇪🇺 <b>Contexto Europa</b>: BCE (taxa de depósito) e energia são os "
                   "drivers. ASML é proxy de ciclo de semicondutores global; bancos "
                   "europeus (HSBC, SAN) reagem rápido a juros.")
    elif market_key == "china":
        out.append("🇨🇳 <b>Contexto China & Ásia</b>: estímulos do PBOC, tensão com EUA e "
                   "regulação tech são os drivers principais. KWEB e BABA têm beta alto "
                   "vs notícias regulatórias; TSM é proxy do ciclo global de chips.")

    # ===== 12. Glossário rápido para os termos da página =====
    out.append("📚 <b>Glossário</b>: <b>Score</b> = condição técnica 0-100 (40 tendência "
               "+ 20 MACD + 20 RSI + 10 ATR + 10 volume). <b>RSI</b> > 70 sobrecomprado, "
               "< 30 sobrevendido. <b>MACD</b> mede momentum (positivo = força "
               "compradora). <b>ATR%</b> = volatilidade diária típica. <b>Vs Máx 52s</b> "
               "= recuo % desde a maior cotação do último ano. <b>Golden/Death Cross</b> "
               "= SMA50 cruza SMA200 (sinal estrutural).")

    return out
