"""Calcula as metricas do TCC (secao 3.4) a partir de um ou mais arquivos de stats/.

Cada arquivo corresponde a um computador e precisa conter os tempos de cada
execucao (campo "times"). Para cada computador, o tempo de cada algoritmo e a
mediana das execucoes, e o overhead e calculado a partir dessas medianas. Entre
computadores, o fator e consolidado pela media geometrica, evitando misturar
tempos absolutos de maquinas diferentes. A memoria, que nao depende da
velocidade da maquina, e consolidada pela media aritmetica.
"""
import json
import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils.stats_utils import parse_cpu_percent, parse_memory_kib_to_mib

# A execucao usa uma unica thread e ocupa um nucleo inteiro, que corresponde a 100% de CPU.
ACTIVE_CPU_THRESHOLD = 100.0
# k: numero minimo de amostras consecutivas acima do limiar que caracterizam a execucao.
SUSTAINED_SAMPLES = 8
# n: ultimas amostras de repouso antes da execucao que formam o conjunto ocioso.
IDLE_SAMPLES = 10
# Faixas da analise de sensibilidade.
SUSTAINED_SAMPLES_RANGE = range(8, 21)
IDLE_SAMPLES_RANGE = range(3, 18)


def filter_total_usage(resource_usage):
    return [
        sample
        for sample in resource_usage
        if sample.get("pid#process_name") == "TOTAL#total"
    ]


def group_by_reading(resource_usage):
    """Agrupa cada linha TOTAL com as linhas de processo coletadas na mesma leitura."""
    readings = []
    for sample in resource_usage:
        if sample.get("pid#process_name") == "TOTAL#total":
            readings.append({"total": sample, "processes": []})
        elif readings:
            readings[-1]["processes"].append(sample)
    return readings


def execution_and_idle_sets(samples, sustained_samples=SUSTAINED_SAMPLES, idle_samples=IDLE_SAMPLES):
    """Indices do conjunto de execucao E e do conjunto ocioso O."""
    cpu = [parse_cpu_percent(sample["cpu"]) for sample in samples]
    active_runs = []
    index = 0
    while index < len(cpu):
        if cpu[index] > ACTIVE_CPU_THRESHOLD:
            end = index
            while end < len(cpu) and cpu[end] > ACTIVE_CPU_THRESHOLD:
                end += 1
            if end - index >= sustained_samples:
                active_runs.append((index, end - 1))
            index = end
        else:
            index += 1

    if not active_runs:
        raise ValueError("Nenhum periodo de execucao encontrado")

    first, last = active_runs[0][0], active_runs[-1][1]
    execution = [i for i in range(first, last + 1) if cpu[i] > ACTIVE_CPU_THRESHOLD]
    idle = [i for i in range(first) if cpu[i] <= ACTIVE_CPU_THRESHOLD][-idle_samples:]
    return execution, idle


def memory_metrics(resource_usage, **set_parameters):
    samples = filter_total_usage(resource_usage)
    execution, idle = execution_and_idle_sets(samples, **set_parameters)
    memory = [parse_memory_kib_to_mib(sample["memory"]) for sample in samples]
    baseline = min(memory[i] for i in idle)
    peak = max(memory[i] for i in execution)
    return baseline, peak


def geometric_mean(values):
    return math.exp(statistics.mean(math.log(value) for value in values))


@dataclass
class TimeStats:
    times: list

    @property
    def median(self):
        return statistics.median(self.times)

    @property
    def mean(self):
        return statistics.mean(self.times)

    @property
    def stdev(self):
        return statistics.stdev(self.times)  # desvio padrao amostral

    @property
    def coefficient_of_variation(self):
        return self.stdev / self.mean * 100


@dataclass
class AlgorithmStats:
    """Resultados de um algoritmo em um computador."""
    algorithm: str
    rust: TimeStats
    wasm: TimeStats
    rust_mem_baseline: float
    rust_mem_peak: float
    wasm_mem_baseline: float
    wasm_mem_peak: float

    @property
    def slowdown_factor(self):
        return self.wasm.median / self.rust.median

    @property
    def overhead_percent(self):
        return (self.slowdown_factor - 1) * 100

    @property
    def rust_mem_net(self):
        return self.rust_mem_peak - self.rust_mem_baseline

    @property
    def wasm_mem_net(self):
        return self.wasm_mem_peak - self.wasm_mem_baseline


@dataclass
class ConsolidatedStats:
    """Resultados de um algoritmo consolidados entre os computadores."""
    algorithm: str
    slowdown_factor: float
    overheads_by_computer: list
    rust_mem_baseline: float
    rust_mem_peak: float
    wasm_mem_baseline: float
    wasm_mem_peak: float

    @property
    def overhead_percent(self):
        return (self.slowdown_factor - 1) * 100

    @property
    def rust_mem_net(self):
        return self.rust_mem_peak - self.rust_mem_baseline

    @property
    def wasm_mem_net(self):
        return self.wasm_mem_peak - self.wasm_mem_baseline


def analyze(data, **set_parameters):
    stats = []
    for entry in data:
        for environment in ("rust", "wasm"):
            if not entry[environment].get("times"):
                raise ValueError(
                    f"{entry['algorithm']} ({environment}) nao possui os tempos de cada execucao; "
                    "use uma coleta no formato atual"
                )
        rust_baseline, rust_peak = memory_metrics(entry["rust"]["resource_usage"], **set_parameters)
        wasm_baseline, wasm_peak = memory_metrics(entry["wasm"]["resource_usage"], **set_parameters)
        stats.append(AlgorithmStats(
            algorithm=entry["algorithm"],
            rust=TimeStats(entry["rust"]["times"]),
            wasm=TimeStats(entry["wasm"]["times"]),
            rust_mem_baseline=rust_baseline,
            rust_mem_peak=rust_peak,
            wasm_mem_baseline=wasm_baseline,
            wasm_mem_peak=wasm_peak,
        ))
    return stats


def consolidate(stats_by_computer):
    consolidated = []
    for per_algorithm in zip(*stats_by_computer):
        consolidated.append(ConsolidatedStats(
            algorithm=per_algorithm[0].algorithm,
            slowdown_factor=geometric_mean([stat.slowdown_factor for stat in per_algorithm]),
            overheads_by_computer=[stat.overhead_percent for stat in per_algorithm],
            **{
                field: statistics.mean(getattr(stat, field) for stat in per_algorithm)
                for field in ("rust_mem_baseline", "rust_mem_peak", "wasm_mem_baseline", "wasm_mem_peak")
            },
        ))
    return consolidated


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


def print_memory_table(stats):
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


def print_computer_report(runner, stats):
    print(f"\n##### {runner} #####")
    print("\n=== TEMPO DE EXECUCAO (ms, 10 execucoes) ===\n")
    print_table(
        headers=["Algoritmo", "Rust mediana", "Rust media", "Rust DP", "Rust CV",
                 "Wasm mediana", "Wasm media", "Wasm DP", "Wasm CV", "Overhead", "Fator"],
        rows=[
            (s.algorithm, s.rust.median, s.rust.mean, s.rust.stdev, s.rust.coefficient_of_variation,
             s.wasm.median, s.wasm.mean, s.wasm.stdev, s.wasm.coefficient_of_variation,
             s.overhead_percent, s.slowdown_factor)
            for s in stats
        ],
        formats=["%s", "%.1f", "%.1f", "%.1f", "%.1f%%", "%.1f", "%.1f", "%.1f", "%.1f%%", "%.1f%%", "%.3fx"],
    )
    print_memory_table(stats)


def print_consolidated_report(runners, consolidated):
    print(f"\n##### CONSOLIDADO ({len(runners)} computadores) #####")
    print("\n=== OVERHEAD (fator consolidado pela media geometrica) ===\n")
    print_table(
        headers=["Algoritmo"] + [f"Overhead {runner}" for runner in runners] + ["Overhead", "Fator"],
        rows=[
            (s.algorithm, *s.overheads_by_computer, s.overhead_percent, s.slowdown_factor)
            for s in consolidated
        ],
        formats=["%s"] + ["%.1f%%"] * len(runners) + ["%.1f%%", "%.3fx"],
    )
    overheads = [s.overhead_percent for s in consolidated]
    best = min(consolidated, key=lambda stat: stat.overhead_percent)
    worst = max(consolidated, key=lambda stat: stat.overhead_percent)
    print(f"\n  Entre os algoritmos: media {statistics.mean(overheads):.1f}%  |  mediana {statistics.median(overheads):.1f}%")
    print(f"  Melhor: {best.algorithm} ({best.overhead_percent:.1f}%)  |  Pior: {worst.algorithm} ({worst.overhead_percent:.1f}%)")
    print_memory_table(consolidated)


def print_collection_report(datasets):
    """Metricas da coleta citadas na metodologia: taxa de amostragem e utilizacao de CPU."""
    print("\n##### COLETA #####\n")
    for runner, data in datasets:
        rates = []
        active_cpu = {"rust": [], "wasm": []}
        for entry in data:
            for environment in ("rust", "wasm"):
                samples = filter_total_usage(entry[environment]["resource_usage"])
                duration = samples[-1]["timestamp"] - samples[0]["timestamp"]
                if duration > 0:
                    rates.append(len(samples) / duration)
                execution, _ = execution_and_idle_sets(samples)
                active_cpu[environment].append(
                    statistics.mean(parse_cpu_percent(samples[i]["cpu"]) for i in execution)
                )
        print(f"  {runner}: {statistics.median(rates):.2f} amostras/s (mediana)")
        for environment, values in active_cpu.items():
            print(f"    CPU media na execucao ({environment}): {min(values):.1f}% a {max(values):.1f}%")

    for environment in ("rust", "wasm"):
        idle_cpu, unattributed_cpu = [], []
        for _, data in datasets:
            for entry in data:
                readings = group_by_reading(entry[environment]["resource_usage"])
                _, idle = execution_and_idle_sets([reading["total"] for reading in readings])
                for i in idle:
                    total_cpu = parse_cpu_percent(readings[i]["total"]["cpu"])
                    process_cpu = sum(parse_cpu_percent(p["cpu"]) for p in readings[i]["processes"])
                    idle_cpu.append(total_cpu)
                    unattributed_cpu.append(total_cpu - process_cpu)
        print(f"  CPU no conjunto ocioso ({environment}): media {statistics.mean(idle_cpu):.1f}%, "
              f"maximo {max(idle_cpu):.1f}%, "
              f"nao atribuida a processos {100 * sum(unattributed_cpu) / sum(idle_cpu):.1f}%")


def print_sensitivity_report(datasets):
    """Variacao do consumo liquido consolidado para outros pares de k e n."""
    def net_memory(**set_parameters):
        stats = consolidate([analyze(data, **set_parameters) for _, data in datasets])
        return [value for s in stats for value in (s.rust_mem_net, s.wasm_mem_net)]

    reference = net_memory()
    largest_deviation, pairs = 0.0, 0
    for sustained_samples in SUSTAINED_SAMPLES_RANGE:
        for idle_samples in IDLE_SAMPLES_RANGE:
            values = net_memory(sustained_samples=sustained_samples, idle_samples=idle_samples)
            largest_deviation = max(largest_deviation, *(abs(a - b) for a, b in zip(values, reference)))
            pairs += 1
    print("\n##### SENSIBILIDADE #####\n")
    print(f"  k de {SUSTAINED_SAMPLES_RANGE.start} a {SUSTAINED_SAMPLES_RANGE.stop - 1}, "
          f"n de {IDLE_SAMPLES_RANGE.start} a {IDLE_SAMPLES_RANGE.stop - 1} ({pairs} pares): "
          f"variacao maxima do consumo liquido medio de {largest_deviation:.2f} MiB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/analyze_stats.py <json_file> [<json_file> ...]")
        sys.exit(1)

    datasets = []
    for path in sys.argv[1:]:
        with open(path) as f:
            data = json.load(f)
        datasets.append((data[0].get("runner", path), data))

    stats_by_computer = [analyze(data) for _, data in datasets]
    for (runner, _), stats in zip(datasets, stats_by_computer):
        print_computer_report(runner, stats)
    if len(datasets) > 1:
        print_consolidated_report([runner for runner, _ in datasets], consolidate(stats_by_computer))
    print_collection_report(datasets)
    if len(datasets) > 1:
        print_sensitivity_report(datasets)
    print()
