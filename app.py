"""Dashboard - Acidentes nas Rodovias Federais (PRF, jan-ago/2026).

Atividade - Análise e Visualização de Dados (CESAR School)
Aluno: Edgleyson Pereira da Silva

Para rodar localmente:  streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from dados import (AMOSTRA_MINIMA, MESES, TIPOS_PISTA, carregar_dados, contagem_semana_hora, filtrar,
                   letalidade, pico_semana_hora, resumo_por)
from graficos import (METRICAS, barras_ranking, fmt_int, fmt_pct, heatmap_semana_hora,
                      linha_letalidade_hora, mapa_densidade)

BANNER_IMG = Path(__file__).parent / "assets" / "banner.png"
CONFIG_PLOTLY = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}
FONTE_URL = "https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf"

st.set_page_config(
    page_title="Acidentes nas Rodovias Federais | PRF 2026",
    page_icon="🚧",
    layout="wide",
)


def juntar(nomes):
    """['A', 'B', 'C'] -> 'A, B e C'"""
    return nomes[0] if len(nomes) == 1 else ", ".join(nomes[:-1]) + " e " + nomes[-1]


# --------- LEITURA DO DATASET --------------------
df = carregar_dados()
LETALIDADE_BRASIL = letalidade(df)

# --------- WIDGETS DE FILTRO -------------------
with st.sidebar:
    st.header("Filtros")

    meses = sorted(int(m) for m in df["mes"].unique())
    periodo = st.select_slider(
        "Período",
        options=meses,
        value=(meses[0], meses[-1]),
        format_func=MESES.get,  # mostra "Jan", "Fev"... no lugar de 1, 2...
    )
    ufs = st.multiselect(
        "Estados (UF)",
        options=sorted(df["uf"].unique()),
        placeholder="Todos os estados",
    )
    pistas = st.pills(
        "Tipo de pista",
        options=TIPOS_PISTA,
        selection_mode="multi",
        default=TIPOS_PISTA,
    )
    if not pistas:
        st.caption("Nenhum tipo de pista marcado: mostrando todos.")

    st.divider()
    st.caption(f"**Fonte:** [PRF – Dados Abertos]({FONTE_URL}), acidentes de 01/01 a 31/08/2026.")
    st.caption("**Aluno:** Edgleyson Pereira da Silva  \nAnálise e Visualização de Dados – CESAR School")

dff = filtrar(df, periodo, ufs, pistas)

# --------- CABEÇALHO --------------------
st.image(str(BANNER_IMG))  # figura fixa que ilustra o dashboard

st.markdown(
    "Painel construído a partir de análises exploratórias e explanatórias: **o horário com mais acidentes "
    "não é o mais letal** e **os tipos de acidente mais frequentes não são os que mais matam**. "
    "Use os filtros da barra lateral para explorar os dados."
)

texto_periodo = MESES[periodo[0]] if periodo[0] == periodo[1] else f"{MESES[periodo[0]]}–{MESES[periodo[1]]}"
texto_ufs = ", ".join(ufs) if ufs else "todos os estados"
texto_pistas = ", ".join(pistas).lower() if pistas and len(pistas) < len(TIPOS_PISTA) else "todas"
st.caption(f"Recorte atual: {texto_periodo}/2026 · {texto_ufs} · pistas: {texto_pistas}")

if dff.empty:
    st.warning("Nenhum acidente encontrado para os filtros escolhidos. Ajuste a barra lateral.")
    st.stop()

# --------- INDICADORES --------------------
media = letalidade(dff)
diferenca = media - LETALIDADE_BRASIL

col1, col2, col3, col4 = st.columns(4)
col1.metric("Acidentes", fmt_int(len(dff)), border=True)
col2.metric("Mortos", fmt_int(dff["mortos"].sum()), border=True)
col3.metric("Feridos", fmt_int(dff["feridos"].sum()), border=True, help="Feridos leves + graves.")
col4.metric(
    "Letalidade",
    fmt_pct(media),
    # sem filtros o recorte é o próprio Brasil, então não há diferença para mostrar
    delta=f"{diferenca:+.1f}".replace(".", ",") + " p.p. vs. média nacional" if abs(diferenca) >= 0.05 else None,
    delta_color="inverse",
    help=f"% dos acidentes com pelo menos uma morte. Média nacional no período todo: {fmt_pct(LETALIDADE_BRASIL)}.",
    border=True,
)

if len(dff) < 500:
    st.info("Poucos acidentes neste recorte: as taxas por hora, tipo e estado podem oscilar bastante.")

aba_quando, aba_como, aba_onde, aba_dados = st.tabs(["🕒 Quando?", "🚗 Como?", "📍 Onde?", "📋 Dados"])

# --------- ABA 1: QUANDO? --------------------
with aba_quando:
    contagem = contagem_semana_hora(dff)
    por_hora = resumo_por(dff, "hora")

    st.subheader("Volume de acidentes por dia da semana e hora")
    st.caption("Cada célula é o nº de acidentes naquele dia e hora. O contorno vermelho marca o pico.")
    st.plotly_chart(heatmap_semana_hora(contagem), config=CONFIG_PLOTLY)

    st.subheader("% dos acidentes que terminam em morte, por hora")
    st.caption("A faixa azul marca a madrugada (0h–5h). Passe o mouse para ver o nº de acidentes de cada hora.")
    st.plotly_chart(linha_letalidade_hora(por_hora, media), config=CONFIG_PLOTLY)

    linha, coluna = pico_semana_hora(contagem)
    texto = (
        f"**Insight:** o pico de volume é **{contagem.index[linha]} às {coluna}h** "
        f"({fmt_int(contagem.iat[linha, coluna])} acidentes)"
    )
    # só compara a letalidade entre horas com amostra suficiente
    horas_confiaveis = por_hora[por_hora["acidentes"] >= AMOSTRA_MINIMA]
    if horas_confiaveis.empty:
        texto += ". O recorte é pequeno demais para comparar a letalidade entre as horas."
    else:
        hora_letal = horas_confiaveis["letalidade"].idxmax()
        texto += (
            f"{', que também é' if hora_letal == coluna else ', mas'} a maior letalidade acontece "
            f"às **{hora_letal}h**: {fmt_pct(por_hora.loc[hora_letal, 'letalidade'])} dos acidentes "
            f"têm morte, contra {fmt_pct(media)} na média do recorte."
        )
    st.info(texto)

# --------- ABA 2: COMO? --------------------
with aba_como:
    col_metrica, col_minimo = st.columns([3, 2])
    metrica = METRICAS[col_metrica.radio("Ordenar por", list(METRICAS), horizontal=True, key="metrica_como")]
    minimo = col_minimo.slider(
        "Esconder categorias com menos de N acidentes",
        min_value=0, max_value=200, value=10, step=5,
        help="Categorias raras distorcem a letalidade (ex.: 9 casos e 6 mortes = 66,7%).",
    )

    tipos = resumo_por(dff, "tipo_acidente")
    tipos = tipos[tipos["acidentes"] >= minimo]
    causas = resumo_por(dff, "causa_acidente")
    causas = causas[causas["acidentes"] >= minimo]

    col_tipos, col_causas = st.columns(2, gap="large")
    with col_tipos:
        st.subheader("Tipos de acidente")
        if tipos.empty:
            st.info("Nenhum tipo com acidentes suficientes. Diminua o mínimo.")
        else:
            st.plotly_chart(barras_ranking(tipos, metrica, media), config=CONFIG_PLOTLY)
    with col_causas:
        st.subheader("10 principais causas")
        if causas.empty:
            st.info("Nenhuma causa com acidentes suficientes. Diminua o mínimo.")
        else:
            st.plotly_chart(barras_ranking(causas, metrica, media, top=10), config=CONFIG_PLOTLY)

    if not tipos.empty:
        mais_comum = tipos["acidentes"].idxmax()
        let_comum = tipos.loc[mais_comum, "letalidade"]
        texto = (
            f"**Insight:** **{mais_comum}** é o tipo mais frequente "
            f"({fmt_int(tipos.loc[mais_comum, 'acidentes'])} acidentes) e {fmt_pct(let_comum)} deles têm morte "
            f"({'abaixo' if let_comum < media else 'acima'} da média de {fmt_pct(media)})."
        )
        criticos = tipos[tipos["letalidade"] > 2 * media].sort_values("mortos", ascending=False)
        if not criticos.empty and dff["mortos"].sum() > 0:
            pct_acidentes = criticos["acidentes"].sum() / len(dff) * 100
            pct_mortes = criticos["mortos"].sum() / dff["mortos"].sum() * 100
            texto += (
                f" Já **{juntar(list(criticos.index))}** {'soma' if len(criticos) == 1 else 'somam'} "
                f"{fmt_pct(pct_acidentes)} dos acidentes, mas **{fmt_pct(pct_mortes)} das mortes**."
            )
        st.info(texto)

# --------- ABA 3: ONDE? --------------------
with aba_onde:
    por_uf = resumo_por(dff, "uf")

    col_mapa, col_ufs = st.columns([3, 2], gap="large")
    with col_mapa:
        st.subheader("Onde os acidentes se concentram")
        so_com_morte = st.toggle("Mostrar apenas acidentes com morte")
        if so_com_morte and dff["com_morte"].sum() == 0:
            st.info("Não há acidentes com morte neste recorte.")
        else:
            st.plotly_chart(mapa_densidade(dff, so_com_morte), config=CONFIG_PLOTLY)
        st.caption("Quanto mais escuro, maior a concentração. Use o scroll para dar zoom e arraste para mover.")
    with col_ufs:
        st.subheader("Ranking por estado")
        metrica_uf = METRICAS[st.radio("Ordenar por", list(METRICAS), horizontal=True, key="metrica_onde")]
        st.plotly_chart(barras_ranking(por_uf, metrica_uf, media), config=CONFIG_PLOTLY)

    # só compara estados com amostra suficiente
    ufs_comparaveis = por_uf[por_uf["acidentes"] >= AMOSTRA_MINIMA]
    if len(ufs_comparaveis) >= 2:
        uf_volume = ufs_comparaveis["acidentes"].idxmax()
        uf_letal = ufs_comparaveis["letalidade"].idxmax()
        let_uf = ufs_comparaveis.loc[uf_letal, "letalidade"]
        razao = f"{let_uf / media:.1f}".replace(".", ",") if media > 0 else "-"
        st.info(
            f"**Insight:** **{uf_volume}** concentra o maior volume "
            f"({fmt_int(ufs_comparaveis.loc[uf_volume, 'acidentes'])} acidentes, letalidade de "
            f"{fmt_pct(ufs_comparaveis.loc[uf_volume, 'letalidade'])}), enquanto **{uf_letal}** tem a maior "
            f"letalidade: {fmt_pct(let_uf)}, {razao}× a média do recorte."
        )

# --------- ABA 4: DADOS --------------------
with aba_dados:
    colunas = {
        "data_inversa": "Data", "horario": "Horário", "uf": "UF", "br": "BR", "km": "Km",
        "municipio": "Município", "tipo_acidente": "Tipo", "causa_acidente": "Causa",
        "classificacao_acidente": "Classificação", "tipo_pista": "Pista",
        "condicao_metereologica": "Clima", "mortos": "Mortos", "feridos": "Feridos", "veiculos": "Veículos",
    }
    tabela = dff[list(colunas)].rename(columns=colunas)

    st.subheader(f"{fmt_int(len(tabela))} acidentes no recorte")
    st.dataframe(tabela, hide_index=True, height=420)
    st.download_button(
        "Baixar CSV do recorte",
        data=tabela.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
        file_name="acidentes_prf_2026_recorte.csv",
        mime="text/csv",
    )

    with st.expander("Sobre os dados e a metodologia"):
        st.markdown(
            f"""
- **Base:** `datatran2026.csv` da [PRF]({FONTE_URL}), um registro por acidente, de 01/01 a 31/08/2026.
- **Limpeza:** remoção das 27 linhas com algum campo nulo (48.712 → 48.685 acidentes), igual às Atividades 1 e 2.
- **Letalidade:** % dos acidentes com pelo menos uma morte (`mortos > 0`). Média nacional: {fmt_pct(LETALIDADE_BRASIL)}.
- **Azul-escuro nos rankings:** categorias com letalidade acima de 2× a média do recorte.
- **Mapa:** densidade das coordenadas (latitude/longitude) de cada acidente.
"""
        )
