"""Leitura, limpeza e agregações do dataset de acidentes da PRF"""

from pathlib import Path

import pandas as pd
import streamlit as st

CAMINHO_CSV = Path(__file__).parent / "data" / "datatran2026.csv"

DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
TIPOS_PISTA = ["Simples", "Dupla", "Múltipla"]

# mínimo de acidentes para destacar uma taxa nos textos/anotações (evita ruído de amostras pequenas)
AMOSTRA_MINIMA = 30


# --------- LEITURA E LIMPEZA --------------------
@st.cache_data(show_spinner="Carregando os dados da PRF...")
def carregar_dados():
    """Lê o CSV e faz a limpeza dos dados"""
    # o CSV separa com ;, usa vírgula decimal, codificação latin-1 e NA para ausentes
    df = pd.read_csv(CAMINHO_CSV, sep=";", encoding="latin-1", decimal=",", na_values=["NA"])

    # remover linhas que tenham qualquer nulo
    df = df.dropna().copy()

    # colunas derivadas usadas nos filtros e gráficos
    df["mes"] = pd.to_datetime(df["data_inversa"]).dt.month
    df["hora"] = pd.to_datetime(df["horario"], format="%H:%M:%S").dt.hour
    df["com_morte"] = (df["mortos"] > 0).astype(int)
    return df


# --------- FILTROS --------------------
def filtrar(df, meses, ufs, pistas):
    """Aplica os filtros da barra lateral. Lista vazia = sem filtro."""
    filtro = df["mes"].between(meses[0], meses[1])
    if ufs:
        filtro &= df["uf"].isin(ufs)
    if pistas:
        filtro &= df["tipo_pista"].isin(pistas)
    return df[filtro]


# --------- AGREGAÇÕES --------------------
def letalidade(df):
    """% dos acidentes com pelo menos uma morte."""
    return df["com_morte"].mean() * 100


def resumo_por(df, coluna):
    """Nº de acidentes, nº de mortos e letalidade (%) de cada categoria da coluna."""
    tabela = df.groupby(coluna).agg(
        acidentes=("com_morte", "size"),
        mortos=("mortos", "sum"),
        letalidade=("com_morte", "mean"),
    )
    tabela["letalidade"] *= 100
    return tabela


def contagem_semana_hora(df):
    """Matriz dia da semana (linhas) x hora do dia (colunas) com o nº de acidentes."""
    return (
        pd.crosstab(df["dia_semana"], df["hora"])
        .reindex(index=DIAS_SEMANA, columns=range(24), fill_value=0)
    )


def pico_semana_hora(contagem):
    """Posição (linha, coluna) da célula com mais acidentes na matriz dia x hora."""
    return divmod(int(contagem.values.argmax()), contagem.shape[1])
