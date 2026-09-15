import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.stats_utils import parse_cpu_percent, parse_memory_kib_to_mib

IDLE_CPU_THRESHOLD = 10.0
ACTIVE_CPU_THRESHOLD = 80.0


def baseline_memory(samples):
    idle = [parse_memory_kib_to_mib(s["memory"]) for s in samples if parse_cpu_percent(s["cpu"]) < IDLE_CPU_THRESHOLD]
    return min(idle) if idle else 0.0


def peak_memory(samples):
    active = [parse_memory_kib_to_mib(s["memory"]) for s in samples if parse_cpu_percent(s["cpu"]) > ACTIVE_CPU_THRESHOLD]
    return max(active) if active else 0.0

def filter_total_usage(resource_usage):
    return [
        sample
        for sample in resource_usage
        if sample.get("pid#process_name") == "TOTAL#total"
    ]

@dataclass
class AlgorithmStats:
    algorithm: str
    rust_mean_ms: float
    wasm_mean_ms: float
    rust_mem_baseline: float
    rust_mem_peak: float
    wasm_mem_baseline: float
    wasm_mem_peak: float

    @property
    def overhead_percent(self):
        return (self.wasm_mean_ms / self.rust_mean_ms - 1) * 100

    @property
    def slowdown_factor(self):
        return self.wasm_mean_ms / self.rust_mean_ms

    @property
    def rust_mem_net(self):
        return self.rust_mem_peak - self.rust_mem_baseline

    @property
    def wasm_mem_net(self):
        return self.wasm_mem_peak - self.wasm_mem_baseline


def analyze(data):
    return [
        AlgorithmStats(
            algorithm=entry["algorithm"],
            rust_mean_ms=entry["rust"]["mean_ms"],
            wasm_mean_ms=entry["wasm"]["mean_ms"],
            rust_mem_baseline=baseline_memory(filter_total_usage(entry["rust"]["resource_usage"])),
            rust_mem_peak=peak_memory(filter_total_usage(entry["rust"]["resource_usage"])),
            wasm_mem_baseline=baseline_memory(filter_total_usage(entry["wasm"]["resource_usage"])),
            wasm_mem_peak=peak_memory(filter_total_usage(entry["wasm"]["resource_usage"])),
        )
        for entry in data
    ]


def print_table(headers, rows, formats):
    column_widths = [
        max(len(header), max(len(fmt % value) for value in column))
        for header, fmt, column in zip(headers, formats, zip(*rows))
    ]
    print("  ".join(header.ljust(width) for header, width in zip(headers, column_widths)))
    print("  ".join("-" * width for width in column_widths))
    for row in rows:
        first_cell = (formats[0] % row[0]).ljust(column_widths[0])
        other_cells = [
            (fmt % value).rjust(width)
            for fmt, value, width in zip(formats[1:], row[1:], column_widths[1:])
        ]
        print("  ".join([first_cell] + other_cells))


def print_report(stats):
    print("\n=== TEMPO DE EXECUCAO ===\n")
    print_table(
        headers=["Algoritmo", "Rust (ms)", "Wasm (ms)", "Overhead", "Fator"],
        rows=[(s.algorithm, s.rust_mean_ms, s.wasm_mean_ms, s.overhead_percent, s.slowdown_factor) for s in stats],
        formats=["%s", "%.1f", "%.1f", "%.1f%%", "%.3fx"],
    )
    overheads = [s.overhead_percent for s in stats]
    sorted_overheads = sorted(overheads)
    best = min(stats, key=lambda stat: stat.overhead_percent)
    worst = max(stats, key=lambda stat: stat.overhead_percent)
    print(f"\n  Media: {sum(overheads)/len(overheads):.1f}%  |  Mediana: {sorted_overheads[len(sorted_overheads)//2]:.1f}%")
    print(f"  Melhor: {best.algorithm} ({best.overhead_percent:.1f}%)  |  Pior: {worst.algorithm} ({worst.overhead_percent:.1f}%)")

    print("\n=== MEMORIA (MiB) ===\n")
    print_table(
        headers=["Algoritmo", "Rust base", "Rust pico", "Rust liquido", "Wasm base", "Wasm pico", "Wasm liquido"],
        rows=[
            (s.algorithm, s.rust_mem_baseline, s.rust_mem_peak, s.rust_mem_net,
             s.wasm_mem_baseline, s.wasm_mem_peak, s.wasm_mem_net)
            for s in stats
        ],
        formats=["%s", "%.1f", "%.1f", "%.1f", "%.1f", "%.1f", "%.1f"],
    )
    print("\n  Nota: baseline Wasm (~190-200 MiB) inclui Chrome headless + Puppeteer.")
    print("  Comparar totais diretamente nao e valido; use os valores liquidos.")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/analyze_stats.py <json_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    print_report(analyze(data))
