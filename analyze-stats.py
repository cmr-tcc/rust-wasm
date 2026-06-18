import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

IDLE_CPU_THRESHOLD = 10.0
ACTIVE_CPU_THRESHOLD = 80.0


def parse_memory_mib(mem_str):
    match = re.match(r"([\d.]+)([KMG]iB)", mem_str)
    if not match:
        return 0.0
    value, unit = float(match.group(1)), match.group(2)
    return value * {"KiB": 1 / 1024, "MiB": 1, "GiB": 1024}[unit]


def parse_cpu_pct(cpu_str):
    return float(cpu_str.replace("%", ""))


def baseline_memory(samples):
    idle = [parse_memory_mib(s["memory"]) for s in samples if parse_cpu_pct(s["cpu"]) < IDLE_CPU_THRESHOLD]
    return min(idle) if idle else 0.0


def peak_memory(samples):
    active = [parse_memory_mib(s["memory"]) for s in samples if parse_cpu_pct(s["cpu"]) > ACTIVE_CPU_THRESHOLD]
    return max(active) if active else 0.0


@dataclass
class AlgorithmStats:
    algorithm: str
    rust_ms: float
    wasm_ms: float
    rust_mem_baseline: float
    rust_mem_peak: float
    wasm_mem_baseline: float
    wasm_mem_peak: float

    @property
    def overhead_pct(self):
        return (self.wasm_ms / self.rust_ms - 1) * 100

    @property
    def slowdown_factor(self):
        return self.wasm_ms / self.rust_ms

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
            rust_ms=entry["rust"]["mean_ms"],
            wasm_ms=entry["wasm"]["mean_ms"],
            rust_mem_baseline=baseline_memory(entry["rust"]["resource_usage"]),
            rust_mem_peak=peak_memory(entry["rust"]["resource_usage"]),
            wasm_mem_baseline=baseline_memory(entry["wasm"]["resource_usage"]),
            wasm_mem_peak=peak_memory(entry["wasm"]["resource_usage"]),
        )
        for entry in data
    ]


def print_table(headers, rows, fmts, align=None):
    if align is None:
        align = ["<" if fmt == "%s" else ">" for fmt in fmts]
    col_widths = [max(len(h), max(len(fmt % v) for v in col)) for h, fmt, col in zip(headers, fmts, zip(*rows))]
    separator = "  ".join("-" * w for w in col_widths)
    header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_row)
    print(separator)
    for row in rows:
        cells = []
        for fmt, v, w, a in zip(fmts, row, col_widths, align):
            cell = fmt % v
            cells.append(cell.ljust(w) if a == "<" else cell.rjust(w))
        print("  ".join(cells))


def print_report(stats):
    print("\n=== TEMPO DE EXECUCAO ===\n")
    print_table(
        headers=["Algoritmo", "Rust (ms)", "Wasm (ms)", "Overhead", "Fator"],
        rows=[(s.algorithm, s.rust_ms, s.wasm_ms, s.overhead_pct, s.slowdown_factor) for s in stats],
        fmts=["%s", "%.1f", "%.1f", "%.1f%%", "%.3fx"],
    )
    overheads = [s.overhead_pct for s in stats]
    sorted_overheads = sorted(overheads)
    worst = max(stats, key=lambda s: s.overhead_pct)
    best = min(stats, key=lambda s: s.overhead_pct)
    print(f"\n  Media: {sum(overheads)/len(overheads):.1f}%  |  Mediana: {sorted_overheads[len(sorted_overheads)//2]:.1f}%")
    print(f"  Melhor: {best.algorithm} ({best.overhead_pct:.1f}%)  |  Pior: {worst.algorithm} ({worst.overhead_pct:.1f}%)")

    print("\n=== MEMORIA (MiB) ===\n")
    print_table(
        headers=["Algoritmo", "R.base", "R.pico", "R.liq", "W.base", "W.pico", "W.liq"],
        rows=[(s.algorithm, s.rust_mem_baseline, s.rust_mem_peak, s.rust_mem_net,
               s.wasm_mem_baseline, s.wasm_mem_peak, s.wasm_mem_net) for s in stats],
        fmts=["%s", "%.1f", "%.1f", "%.1f", "%.1f", "%.1f", "%.1f"],
    )
    print("\n  Nota: baseline Wasm (~190-200 MiB) inclui Chrome headless + Puppeteer.")
    print("  Comparar totais diretamente nao e valido; use os valores liquidos (liq).")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 analyze-stats.py <json_file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    print_report(analyze(data))
