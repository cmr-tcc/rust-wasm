"""Gera o grafico do fator Wasm/nativo por algoritmo usado no TCC.

Para cada algoritmo ha uma coluna vertical por computador (fator calculado com
as medianas daquele computador), e o traco horizontal indica o fator
consolidado pela media geometrica, o mesmo calculo de analyze_stats.py. As
colunas partem de 1,0, que corresponde ao mesmo tempo nos dois ambientes. Cada
coleta e associada ao numero do computador no TCC pelo campo "runner", de modo
que cada computador mantem a mesma cor e a mesma textura.

Uso: python3 scripts/generate_factor_chart.py <json_file> [<json_file> ...] [--output caminho.png]
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator

sys.path.insert(0, str(Path(__file__).parent))
from analyze_stats import analyze, consolidate

DEFAULT_OUTPUT = "charts/tcc/fator-por-algoritmo.png"

# Numero de cada computador na secao "Hardwares" do TCC.
COMPUTER_BY_RUNNER = {"Mateus": 1, "Raissa": 2, "Carlos": 3}
# Paleta categorica validada para ate 3 series (todas as combinacoes de pares).
COMPUTER_COLORS = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a"}
# Textura como codificacao secundaria (impressao em escala de cinza e daltonismo).
COMPUTER_HATCHES = {1: "", 2: "////", 3: "...."}
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID_COLOR = "#e4e3df"

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
    # Algoritmos em ordem crescente de fator, da esquerda para a direita.
    order = sorted(range(len(consolidated)), key=lambda i: consolidated[i].slowdown_factor)
    computer_count = len(stats_by_computer)
    bar_width = 0.8 / computer_count
    offsets = [(i - (computer_count - 1) / 2) * bar_width for i in range(computer_count)]

    fig, ax = plt.subplots(figsize=(8, 4.4))
    for column, index in enumerate(order):
        for position, (computer, stats) in enumerate(zip(computers, stats_by_computer)):
            factor = stats[index].slowdown_factor
            ax.bar(column + offsets[position], factor - 1.0, bottom=1.0, width=bar_width,
                   color=COMPUTER_COLORS[computer], hatch=COMPUTER_HATCHES[computer],
                   edgecolor="white", linewidth=1, zorder=2)
        consolidated_factor = consolidated[index].slowdown_factor
        group_half_width = bar_width * computer_count / 2
        ax.hlines(consolidated_factor, column - group_half_width, column + group_half_width,
                  color=TEXT_PRIMARY, linewidth=2.5, zorder=3)
        group_top = max(stats[index].slowdown_factor for stats in stats_by_computer)
        ax.annotate(format_factor(consolidated_factor), (column, group_top), xytext=(0, 6),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, color=TEXT_PRIMARY)

    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([ALGORITHM_LABELS.get(consolidated[i].algorithm, consolidated[i].algorithm)
                        for i in order], color=TEXT_PRIMARY)
    largest = max(stats[i].slowdown_factor for stats in stats_by_computer for i in range(len(consolidated)))
    ax.set_ylim(1.0, largest + 0.25)
    ax.set_ylabel("Fator (tempo Wasm / tempo nativo)", color=TEXT_PRIMARY)
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1f}".replace(".", ",")))
    ax.tick_params(colors=TEXT_SECONDARY, length=0)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    for name, spine in ax.spines.items():
        spine.set_visible(name == "bottom")
    ax.spines["bottom"].set_color(TEXT_SECONDARY)

    handles = [
        Patch(facecolor=COMPUTER_COLORS[computer], hatch=COMPUTER_HATCHES[computer], edgecolor="white",
              label=f"Computador {computer}")
        for computer in computers
    ]
    handles.append(Line2D([], [], color=TEXT_PRIMARY, linewidth=2.5, label="Média geométrica"))
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY)

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
