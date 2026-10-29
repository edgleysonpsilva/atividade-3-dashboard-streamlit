"""Gera a figura fixa do dashboard (assets/banner.png) com matplotlib.

Uso (na raiz do projeto, com o venv ativado):
    pip install matplotlib
    python scripts/gerar_banner.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle
from matplotlib.path import Path as Caminho

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from graficos import AZUL_1, AZUL_2, AZUL_3, AZUL_4, AZUL_7, AZUL_8, AZUL_9, BRANCO, DESTAQUE  # noqa: E402

plt.rcParams["font.family"] = ["Avenir Next", "Arial", "DejaVu Sans"]

# área de desenho de 12 x 4 "polegadas" -> 2400 x 800 px com dpi=200
fig = plt.figure(figsize=(12, 4), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 12)
ax.set_ylim(0, 4)
ax.axis("off")

# --------- FUNDO --------------------
degrade = LinearSegmentedColormap.from_list("fundo", ["#E2EDFF", "#F7FAFF"])
ax.imshow(np.linspace(0, 1, 256).reshape(-1, 1), extent=[0, 12, 0, 4], cmap=degrade,
          aspect="auto", origin="lower", zorder=0)

# cantos decorativos
ax.add_patch(Polygon([[0, 4], [1.5, 4], [0, 2.9]], color=AZUL_4, zorder=1))
ax.add_patch(Polygon([[1.5, 4], [2.1, 4], [0, 2.45], [0, 2.9]], color=AZUL_8, alpha=0.55, zorder=1))

# --------- ESCUDO "BR" (placa das rodovias federais) --------------------
cx, topo, base = 1.55, 2.75, 1.05
esq, dir_ = cx - 0.62, cx + 0.62
escudo = Caminho(
    [(esq, topo), (dir_, topo), (dir_, 2.0), (dir_, 1.45), (cx, base), (esq, 1.45), (esq, 2.0), (esq, topo)],
    [Caminho.MOVETO, Caminho.LINETO, Caminho.LINETO, Caminho.CURVE3, Caminho.CURVE3,
     Caminho.CURVE3, Caminho.CURVE3, Caminho.CLOSEPOLY],
)
ax.add_patch(PathPatch(escudo, facecolor=BRANCO, edgecolor=AZUL_3, lw=5, zorder=3))
ax.text(cx, 2.3, "BR", ha="center", va="center", fontsize=30, fontweight="bold", color=AZUL_1, zorder=4)
ax.plot([esq + 0.15, dir_ - 0.15], [1.92, 1.92], color=AZUL_3, lw=2.5, zorder=4)
ax.text(cx, 1.6, "2026", ha="center", va="center", fontsize=17, fontweight="bold", color=AZUL_3, zorder=4)

ax.plot([2.55, 2.55], [1.1, 2.75], color=AZUL_8, lw=2, zorder=2)  # divisória

# --------- TÍTULO --------------------
ax.text(2.85, 2.5, "Acidentes nas", fontsize=32, color=AZUL_3, va="center", zorder=4)
ax.text(2.85, 1.85, "Rodovias Federais", fontsize=40, fontweight="bold", color=AZUL_1, va="center", zorder=4)
ax.text(2.88, 1.32, "Quando, como e onde acontecem os acidentes registrados pela PRF",
        fontsize=13, color=AZUL_2, va="center", zorder=4)
ax.text(2.88, 0.98, "Dados abertos PRF  ·  01/01 a 31/08/2026  ·  48.685 ocorrências",
        fontsize=11, color=AZUL_4, va="center", zorder=4)

# --------- ILUSTRAÇÃO: GRÁFICO DE BARRAS AO FUNDO --------------------
for x, altura in zip([8.85, 9.2, 9.55], [0.55, 0.85, 0.7]):
    ax.add_patch(Rectangle((x, 2.6), 0.24, altura, color=AZUL_9, zorder=1))
for x, altura in zip([10.75, 11.1, 11.45], [0.75, 0.98, 1.18]):
    ax.add_patch(Rectangle((x, 2.6), 0.24, altura, color=AZUL_9, zorder=1))
ax.plot([10.6, 10.95, 11.25, 11.68], [3.1, 3.25, 3.2, 3.56], color=AZUL_7, lw=3,
        solid_capstyle="round", zorder=2)
ax.annotate("", xy=(11.8, 3.74), xytext=(11.58, 3.46),
            arrowprops=dict(arrowstyle="-|>", color=AZUL_7, lw=3, mutation_scale=22), zorder=2)

# --------- ILUSTRAÇÃO: RODOVIA EM PERSPECTIVA --------------------
horizonte, centro = 2.6, 10.2
ax.add_patch(Polygon([[8.55, 0], [11.85, 0], [centro + 0.12, horizonte], [centro - 0.12, horizonte]],
                     color=AZUL_2, zorder=2))
ax.plot([8.85, centro - 0.08], [0, horizonte], color=BRANCO, lw=2.5, zorder=3)   # acostamento
ax.plot([11.55, centro + 0.08], [0, horizonte], color=BRANCO, lw=2.5, zorder=3)

# faixa central tracejada, diminuindo em direção ao horizonte
for y0, y1 in [(0.05, 0.55), (0.85, 1.25), (1.48, 1.78), (1.95, 2.15), (2.27, 2.4), (2.47, 2.54)]:
    meia0 = 0.075 * (1 - y0 / horizonte) + 0.008
    meia1 = 0.075 * (1 - y1 / horizonte) + 0.008
    ax.add_patch(Polygon([[centro - meia0, y0], [centro + meia0, y0], [centro + meia1, y1],
                          [centro - meia1, y1]], color=BRANCO, zorder=3))

# --------- ILUSTRAÇÃO: PINO DE LOCALIZAÇÃO --------------------
px_, py_ = 10.2, 3.05
ax.add_patch(Polygon([[px_ - 0.26, py_ - 0.12], [px_ + 0.26, py_ - 0.12], [px_, py_ - 0.68]],
                     color=DESTAQUE, zorder=5))
ax.add_patch(Circle((px_, py_), 0.3, color=DESTAQUE, zorder=5))
ax.add_patch(Circle((px_, py_), 0.12, color=BRANCO, zorder=6))

destino = RAIZ / "assets" / "banner.png"
fig.savefig(destino, dpi=200)
print(f"Banner salvo em {destino}")
