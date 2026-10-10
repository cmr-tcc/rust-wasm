"""Gera o grafico do fator Wasm/nativo por algoritmo usado no TCC.

Cada computador aparece como um ponto (fator calculado com as medianas daquele
computador) e o traco vertical indica o fator consolidado pela media geometrica, o
mesmo calculo de analyze_stats.py. Cada coleta e associada ao numero do
computador no TCC pelo campo "runner", de modo que cada computador mantem a
mesma cor e o mesmo marcador.

Uso: python3 scripts/generate_factor_chart.py <json_file> [<json_file> ...] [--output caminho.png]
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

sys.path.insert(0, str(Path(__file__).parent))
from analyze_stats import analyze, consolidate

DEFAULT_OUTPUT = "charts/tcc/fator-por-algoritmo.png"

# Numero de cada computador na secao "Hardwares" do TCC.
COMPUTER_BY_RUNNER = {"Mateus": 1, "Raissa": 2, "Carlos": 3}
# Paleta categorica validada para ate 3 series (todas as combinacoes de pares).
COMPUTER_COLORS = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a"}
# Formato do marcador como codificacao secundaria (impressao em escala de cinza e daltonismo).
COMPUTER_MARKERS = {1: "o", 2: "s", 3: "^"}
# O triangulo ocupa menos area que os demais marcadores com o mesmo tamanho.
MARKER_SIZES = {1: 55, 2: 50, 3: 75}
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID_COLOR = "#e4e3df"
RANGE_COLOR = "#b5b4ae"

ALGORITHM_LABELS = {
    "fannkuch_redux": "fannkuch-redux",
    "spectral_norm": "spectral-norm",
    "n_body": "n-body",
    "mandelbrot": "mandelbrot",
    "fasta": "fasta",
}


def format_factor(value):
    return f"{value:.3f}".replace(".", ",") + "x"


def plot(computers, stats_by_computer, consolidated, output):
    # Algoritmo com maior fator no topo.
    order = sorted(range(len(consolidated)), key=lambda i: consolidated[i].slowdown_factor)
    computer_count = len(stats_by_computer)
    offsets = [(i - (computer_count - 1) / 2) * 0.14 for i in range(computer_count)]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    for row, index in enumerate(order):
        factors = [stats[index].slowdown_factor for stats in stats_by_computer]
        ax.plot([min(factors), max(factors)], [row, row], color=RANGE_COLOR, linewidth=2,
                solid_capstyle="round", zorder=1)
        for position, (computer, factor) in enumerate(zip(computers, factors)):
            ax.scatter(factor, row + offsets[position], s=MARKER_SIZES[computer], marker=COMPUTER_MARKERS[computer],
                       color=COMPUTER_COLORS[computer], edgecolors="white", linewidths=1.2, zorder=3)
        # Traco vertical atras dos pontos, para nao esconder um computador com o mesmo fator.
        consolidated_factor = consolidated[index].slowdown_factor
        ax.scatter(consolidated_factor, row, s=700, marker="|", color=TEXT_PRIMARY, linewidths=2.5, zorder=2)
        ax.annotate(format_factor(consolidated_factor), (max(factors), row), xytext=(10, 0),
                    textcoords="offset points", va="center", fontsize=9, color=TEXT_PRIMARY)

    ax.axvline(1.0, color=TEXT_SECONDARY, linewidth=1, linestyle="--", zorder=0)
    ax.annotate("mesmo tempo\nnos dois ambientes", (1.0, len(order) - 0.5), xytext=(6, 0),
                textcoords="offset points", va="top", fontsize=8, color=TEXT_SECONDARY)

    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([ALGORITHM_LABELS.get(consolidated[i].algorithm, consolidated[i].algorithm)
                        for i in order], color=TEXT_PRIMARY)
    ax.set_ylim(-0.6, len(order) - 0.4)
    largest = max(stats[i].slowdown_factor for stats in stats_by_computer for i in range(len(consolidated)))
    ax.set_xlim(0.9, largest + 0.35)
    ax.set_xlabel("Fator (tempo Wasm / tempo nativo)", color=TEXT_PRIMARY)
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1f}".replace(".", ",")))
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    ax.grid(axis="x", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    handles = [
        Line2D([], [], linestyle="none", marker=COMPUTER_MARKERS[computer], markersize=8,
               markerfacecolor=COMPUTER_COLORS[computer], markeredgecolor="white",
               label=f"Computador {computer}")
        for computer in computers
    ]
    handles.append(Line2D([], [], linestyle="none", marker="|", markersize=14, markeredgewidth=2.5,
                          color=TEXT_PRIMARY, label="Média geométrica"))
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY)

    fig.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200)
    print(f"Grafico salvo em {output}")


if __name__ == "__main__":
    arguments = sys.argv[1:]
    output = DEFAULT_OUTPUT
    if "--output" in arguments:
        position = arguments.index("--output")
        output = arguments[position + 1]
        del arguments[position:position + 2]

    if not arguments:
        print(__doc__)
        sys.exit(1)
    if len(arguments) > len(COMPUTER_COLORS):
        print(f"No maximo {len(COMPUTER_COLORS)} computadores")
        sys.exit(1)

    collections = []
    for path in arguments:
        with open(path) as f:
            data = json.load(f)
        runner = data[0].get("runner")
        if runner not in COMPUTER_BY_RUNNER:
            print(f"Computador desconhecido em {path}: {runner!r}")
            sys.exit(1)
        collections.append((COMPUTER_BY_RUNNER[runner], analyze(data)))
    collections.sort(key=lambda collection: collection[0])

    computers = [computer for computer, _ in collections]
    stats_by_computer = [stats for _, stats in collections]
    plot(computers, stats_by_computer, consolidate(stats_by_computer), output)
